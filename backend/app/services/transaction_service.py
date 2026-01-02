import uuid
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.tables import Transaction, CreditCard, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.finance import FinanceService

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    # CORREÇÃO: Adicionado parâmetro user_id obrigatório
    def create(self, user_id: int, tx_data: TransactionCreate):
        # Validações Básicas
        if tx_data.amount <= 0:
            raise ValueError("O valor da transação deve ser positivo.")
        
        if tx_data.is_recurring and (tx_data.installment_total and tx_data.installment_total > 1):
            raise ValueError("Não é possível criar transação Recorrente e Parcelada ao mesmo tempo.")

        try:
            # --- ROTA CRÉDITO ---
            if tx_data.payment_method == "credito":
                if not tx_data.card_id:
                    raise ValueError("ID do cartão de crédito é obrigatório.")
                
                # Se for Recorrente (Assinatura Mensal), tratamos aqui
                if tx_data.is_recurring:
                    return self._create_credit_recurring(user_id, tx_data)
                
                # Se for Parcelado ou À Vista no Crédito, o FinanceService resolve
                created_txs = FinanceService.process_credit_card_purchase(
                    self.db, 
                    user_id, # Usa o ID real do usuário logado
                    tx_data.card_id, 
                    tx_data.dict()
                )
                return created_txs[0] if created_txs else None

            # --- ROTA DÉBITO / PIX ---
            else:
                return self._create_debit_transaction(user_id, tx_data)

        except Exception as e:
            self.db.rollback()
            print(f"ERRO CREATE TRANSACTION: {e}")
            raise e

    def _create_debit_transaction(self, user_id: int, tx_data: TransactionCreate):
        """
        Cria transações de débito (pode ser única ou recorrente 12x).
        """
        repeat_count = 12 if tx_data.is_recurring else 1
        group_id = str(uuid.uuid4()) if tx_data.is_recurring else None
        
        base_date = tx_data.date
        created_transactions = []
        today = date.today()

        for i in range(repeat_count):
            target_date = base_date + relativedelta(months=i)
            
            # Lógica: Se data é hoje ou passado -> PAGO. Futuro -> PENDENTE.
            if target_date <= today:
                current_status = TransactionStatus.PAID
            else:
                current_status = TransactionStatus.PENDING

            db_obj = Transaction(
                user_id=user_id, # ID Real
                description=tx_data.description,
                amount=Decimal(str(tx_data.amount)),
                type=tx_data.type,
                date=target_date,
                category_id=tx_data.category_id,
                account_id=tx_data.account_id,
                is_recurring=tx_data.is_recurring,
                frequency=tx_data.frequency,
                payment_method=tx_data.payment_method,
                status=current_status,
                installment_group_id=group_id,
                debtor_id=tx_data.debtor_id
            )
            self.db.add(db_obj)
            created_transactions.append(db_obj)

        self.db.commit()
        
        # Recalcula saldo apenas se houver transações pagas e uma conta vinculada
        if tx_data.account_id:
            FinanceService.recalculate_account_balance(self.db, tx_data.account_id)

        if created_transactions:
            self.db.refresh(created_transactions[0])
            return created_transactions[0]
        return None

    def _create_credit_recurring(self, user_id: int, tx_data: TransactionCreate):
        """
        Cria assinaturas no crédito (12 meses fixos).
        """
        card = self.db.get(CreditCard, tx_data.card_id)
        if not card: raise ValueError("Cartão não encontrado.")

        group_id = str(uuid.uuid4())
        base_date = tx_data.date
        created_transactions = []

        for i in range(12):
            display_date = base_date + relativedelta(months=i)
            
            # Lógica de Fechamento para alocar na fatura correta
            if display_date.day >= card.closing_day:
                bill_date = display_date + relativedelta(months=1)
            else:
                bill_date = display_date

            bill = FinanceService._get_or_create_bill(self.db, card.id, bill_date.month, bill_date.year)

            db_obj = Transaction(
                user_id=user_id, # ID Real
                description=tx_data.description, 
                amount=Decimal(str(tx_data.amount)),
                type="expense", 
                date=display_date, 
                category_id=tx_data.category_id,
                card_id=card.id,
                bill_id=bill.id,
                is_installment=False,
                installment_group_id=group_id,
                payment_method="credito",
                status=TransactionStatus.PENDING,
                is_recurring=True,
                frequency="mensal",
                debtor_id=tx_data.debtor_id
            )
            self.db.add(db_obj)
            created_transactions.append(db_obj)

        self.db.commit()
        if created_transactions: self.db.refresh(created_transactions[0])
        return created_transactions[0]

    # CORREÇÃO: Adicionado user_id para segurança (IDOR)
    def update(self, user_id: int, transaction_id: int, update_data: dict):
        try:
            # Busca garantindo que a transação pertence ao usuário logado
            tx = self.db.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id 
            ).first()
            
            if not tx: return None # Retorna None se não achar ou não for dono

            old_account_id = tx.account_id

            # Atualiza campos
            for key, value in update_data.items():
                if key != 'id': 
                    if key == 'date' and isinstance(value, str):
                        try: value = datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError: pass 
                    setattr(tx, key, value)

            self.db.commit()
            self.db.refresh(tx)

            # Recalcula saldos
            if old_account_id:
                FinanceService.recalculate_account_balance(self.db, old_account_id)
            if tx.account_id and tx.account_id != old_account_id:
                FinanceService.recalculate_account_balance(self.db, tx.account_id)

            return tx
        except Exception as e:
            self.db.rollback()
            print(f"ERRO UPDATE: {e}")
            raise e

    # CORREÇÃO: Adicionado user_id para segurança
    def delete(self, user_id: int, transaction_id: int):
        try:
            tx = self.db.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id
            ).first()
            
            if not tx: return False
            
            group_id = tx.installment_group_id
            account_id = tx.account_id
            
            # Se faz parte de um grupo, deleta todos DO MESMO USUÁRIO
            if group_id:
                self.db.query(Transaction).filter(
                    Transaction.installment_group_id == group_id,
                    Transaction.user_id == user_id
                ).delete()
            else:
                self.db.delete(tx)

            self.db.commit()

            if account_id:
                FinanceService.recalculate_account_balance(self.db, account_id)
                
            return True
        except Exception as e:
            self.db.rollback()
            raise e