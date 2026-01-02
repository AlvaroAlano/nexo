import uuid
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.tables import Transaction, Account, CreditCard, CreditCardBill, BillStatus
from app.schemas.transaction import TransactionCreate

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, tx_data: TransactionCreate):
        if tx_data.amount <= 0:
            raise ValueError("O valor da transação deve ser positivo.")
        
        # VALIDAÇÃO: Impedir Recorrência + Parcelamento simultâneo
        if tx_data.is_recurring and (tx_data.total_installments and tx_data.total_installments > 1):
            raise ValueError("Não é possível criar uma transação que seja Recorrente e Parcelada ao mesmo tempo.")

        try:
            if tx_data.payment_method == "credito":
                if not tx_data.credit_card_id:
                    raise ValueError("ID do cartão de crédito é obrigatório.")
                tx_data.type = "despesa" 
                
                if tx_data.is_recurring:
                    return self._create_credit_recurring(tx_data)
                else:
                    return self._create_credit_installments(tx_data)
            else:
                return self._create_debit_transaction(tx_data)
        except Exception as e:
            self.db.rollback() 
            print(f"ERRO CREATE TRANSACTION: {e}")
            raise e

    def _create_debit_transaction(self, tx_data: TransactionCreate):
        repeat_count = 12 if tx_data.is_recurring else 1
        group_id = str(uuid.uuid4()) if tx_data.is_recurring else None
        
        base_date = tx_data.date if isinstance(tx_data.date, date) else tx_data.date.date()
        created_transactions = []
        
        # Pega a data de hoje para comparação
        today = date.today()

        for i in range(repeat_count):
            target_date = base_date + relativedelta(months=i)
            
            # --- NOVA LÓGICA DE STATUS ---
            # Se a data for hoje ou no passado -> Nasce PAGO
            # Se a data for futura -> Nasce PENDENTE
            if target_date <= today:
                current_status = "pago"
            else:
                current_status = "pendente"
            # -----------------------------

            db_obj = Transaction(
                description=tx_data.description,
                amount=tx_data.amount,
                type=tx_data.type,
                date=target_date,
                category_id=tx_data.category_id,
                account_id=tx_data.account_id or 1,
                is_recurring=tx_data.is_recurring,
                frequency=tx_data.frequency,
                payment_method="debito",
                status=current_status, # Usa a variável calculada acima
                installment_group_id=group_id,
                debtor_name=tx_data.debtor_name
            )
            self.db.add(db_obj)
            created_transactions.append(db_obj)

            # Atualiza saldo apenas se o status calculado for pago
            if current_status == "pago":
                self._update_account_balance(db_obj.account_id, tx_data.amount, tx_data.type)

        self.db.commit()
        if created_transactions:
            self.db.refresh(created_transactions[0])
            return created_transactions[0]
        return None

    def _create_credit_recurring(self, tx_data: TransactionCreate):
        card = self.db.get(CreditCard, tx_data.credit_card_id)
        if not card: raise ValueError("Cartão não encontrado.")

        group_id = str(uuid.uuid4())
        base_date = tx_data.date if isinstance(tx_data.date, date) else tx_data.date.date()
        created_transactions = []

        for i in range(12):
            display_date = base_date + relativedelta(months=i)
            if display_date.day >= card.closing_day:
                bill_reference_date = display_date + relativedelta(months=1)
            else:
                bill_reference_date = display_date

            bill = self._get_or_create_bill(card.id, bill_reference_date.month, bill_reference_date.year)

            db_obj = Transaction(
                description=tx_data.description, 
                amount=tx_data.amount,
                type="despesa",
                date=display_date, 
                category_id=tx_data.category_id,
                bill_id=bill.id,
                is_installment=False,
                installment_group_id=group_id,
                payment_method="credito",
                status="pendente",
                is_recurring=True,
                frequency="mensal",
                debtor_name=tx_data.debtor_name
            )
            self.db.add(db_obj)
            created_transactions.append(db_obj)

        self.db.commit()
        if created_transactions: self.db.refresh(created_transactions[0])
        return created_transactions[0]

    def _create_credit_installments(self, tx_data: TransactionCreate):
        card = self.db.get(CreditCard, tx_data.credit_card_id)
        if not card: raise ValueError("Cartão não encontrado.")

        installments = tx_data.total_installments or 1
        installment_amount = round(tx_data.amount / installments, 2)
        remainder = round(tx_data.amount - (installment_amount * installments), 2)
        group_id = str(uuid.uuid4()) if installments > 1 else None
        
        purchase_date = tx_data.date if isinstance(tx_data.date, date) else tx_data.date.date()
        created_transactions = []

        for i in range(installments):
            current_amount = installment_amount + remainder if i == 0 else installment_amount
            display_date = purchase_date + relativedelta(months=i)
            
            if display_date.day >= card.closing_day:
                bill_reference_date = display_date + relativedelta(months=1)
            else:
                bill_reference_date = display_date

            bill = self._get_or_create_bill(card.id, bill_reference_date.month, bill_reference_date.year)
            desc_suffix = f" ({i+1}/{installments})" if installments > 1 else ""
            
            db_obj = Transaction(
                description=f"{tx_data.description}{desc_suffix}",
                amount=current_amount,
                type="despesa",
                date=display_date, 
                category_id=tx_data.category_id,
                bill_id=bill.id,
                is_installment=(installments > 1),
                installment_current=i+1 if installments > 1 else None,
                installment_total=installments if installments > 1 else None,
                installment_group_id=group_id,
                payment_method="credito",
                status="pendente",
                is_recurring=False,
                debtor_name=tx_data.debtor_name
            )
            self.db.add(db_obj)
            created_transactions.append(db_obj)

        self.db.commit()
        if created_transactions: self.db.refresh(created_transactions[0])
        return created_transactions[0]

    def delete(self, transaction_id: int):
        try:
            tx = self.db.get(Transaction, transaction_id)
            if not tx: raise ValueError("Transação não encontrada.")
            group_id = tx.installment_group_id
            transactions_to_delete = []

            if group_id:
                transactions_to_delete = self.db.query(Transaction).filter(
                    Transaction.installment_group_id == group_id
                ).all()
            else:
                transactions_to_delete = [tx]

            for t in transactions_to_delete:
                if t.payment_method == "debito" and t.status == "pago":
                    self._update_account_balance(t.account_id, t.amount, t.type, is_reversal=True)
                self.db.delete(t)

            self.db.commit()
            return {"message": "Transações excluídas."}
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, transaction_id: int, update_data: dict):
        try:
            tx = self.db.get(Transaction, transaction_id)
            if not tx: raise ValueError("Transação não encontrada.")

            if tx.payment_method == "debito" and tx.status == "pago":
                self._update_account_balance(tx.account_id, tx.amount, tx.type, is_reversal=True)

            for key, value in update_data.items():
                if key != 'id': 
                    if key == 'date' and isinstance(value, str):
                        try: value = datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError: pass 
                    setattr(tx, key, value)

            if tx.payment_method == "debito" and tx.status == "pago":
                self._update_account_balance(tx.account_id, tx.amount, tx.type, is_reversal=False)

            self.db.commit()
            self.db.refresh(tx)
            return tx
        except Exception as e:
            self.db.rollback()
            print(f"ERRO UPDATE: {e}")
            raise e

    def _get_or_create_bill(self, card_id, month, year):
        stmt = select(CreditCardBill).where(
            CreditCardBill.card_id == card_id, 
            CreditCardBill.month == month, 
            CreditCardBill.year == year
        )
        bill = self.db.execute(stmt).scalars().first()
        if not bill:
            bill = CreditCardBill(card_id=card_id, month=month, year=year, status=BillStatus.OPEN)
            self.db.add(bill)
            self.db.flush()
        return bill

    # --- CORREÇÃO AQUI: AUTO-CRIAÇÃO DA CONTA ---
    def _update_account_balance(self, account_id, amount, type, is_reversal=False):
        account = self.db.get(Account, account_id)
        
        # Se a conta não existe, cria ela agora para não perder o saldo
        if not account:
            print(f"⚠️ Conta {account_id} não encontrada! Criando automaticamente...")
            # Cria a conta padrão se não existir
            account = Account(id=account_id, name="Carteira", current_balance=0.0)
            self.db.add(account)
            self.db.flush() # Garante que ela exista para o update abaixo

        if type == "receita":
            if is_reversal: account.current_balance -= amount
            else: account.current_balance += amount
        else: 
            if is_reversal: account.current_balance += amount
            else: account.current_balance -= amount
            
        self.db.add(account)