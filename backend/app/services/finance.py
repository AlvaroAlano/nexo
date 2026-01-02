from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_DOWN
import uuid

# Importe seus modelos
from app.models.tables import Transaction, Account, CreditCard, CreditCardBill, BillStatus, TransactionType, TransactionStatus

class FinanceService:
    
    @staticmethod
    def recalculate_account_balance(db: Session, account_id: int):
        """
        Recalcula o saldo total da conta somando todas as receitas e subtraindo despesas.
        IMPORTANTE: Isso corrige qualquer inconsistência se alguém editar algo no banco.
        """
        if not account_id: return

        # 1. Soma Entradas (Income)
        # Nota: Convertemos para Decimal para garantir matemática precisa
        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or Decimal(0)

        # 2. Soma Saídas (Expense)
        expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or Decimal(0)

        # 3. Atualiza a conta com o valor real
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.current_balance = income - expense
            db.add(account)
            # Não damos commit aqui para permitir que quem chamou faça o commit em transação única

    @staticmethod
    def process_credit_card_purchase(db: Session, user_id: int, card_id: int, transaction_data: dict):
        """
        Gera as transações de cartão de crédito parceladas com as datas corretas e sem perder centavos.
        """
        card = db.query(CreditCard).filter(CreditCard.id == card_id).first()
        if not card:
            raise ValueError("Cartão não encontrado")

        purchase_date = transaction_data.get('date', date.today())
        # Garante que estamos lidando com Decimal
        total_amount = Decimal(str(transaction_data['amount'])) 
        installments = transaction_data.get('installment_total', 1)
        
        # --- MATEMÁTICA FINANCEIRA (CORREÇÃO DOS CENTAVOS) ---
        # Ex: 100 / 3 = 33.33 (sobra 0.01)
        if installments > 1:
            base_amount = (total_amount / installments).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            remainder = total_amount - (base_amount * installments)
        else:
            base_amount = total_amount
            remainder = Decimal(0)

        group_id = str(uuid.uuid4())
        created_transactions = []

        for i in range(installments):
            # A primeira parcela absorve os centavos de resto (ex: 33.34, 33.33, 33.33)
            amount = base_amount + remainder if i == 0 else base_amount
            
            # --- LÓGICA DE DATA DE FATURA ---
            # Se compra dia 25 e o cartão fecha dia 20, a parcela 1 já cai no mês seguinte
            month_offset = i
            if purchase_date.day >= card.closing_day:
                month_offset += 1
            
            target_date = purchase_date + relativedelta(months=month_offset)
            
            # Busca ou Cria a Fatura para esse mês específico
            bill = FinanceService._get_or_create_bill(db, card.id, target_date.month, target_date.year)
            
            tx = Transaction(
                user_id=user_id,
                description=f"{transaction_data['description']} ({i+1}/{installments})",
                amount=amount, 
                date=target_date, # A data é a data da fatura, não da compra
                type=TransactionType.EXPENSE,
                payment_method='credito',
                status=TransactionStatus.PENDING, # Fatura nasce pendente
                
                card_id=card.id,
                bill_id=bill.id,
                category_id=transaction_data.get('category_id'),
                debtor_id=transaction_data.get('debtor_id'),
                
                is_installment=True if installments > 1 else False,
                installment_current=i+1,
                installment_total=installments,
                installment_group_id=group_id
            )
            db.add(tx)
            created_transactions.append(tx)

        return created_transactions # Retorna a lista para ser commitada pelo service principal

    @staticmethod
    def _get_or_create_bill(db: Session, card_id: int, month: int, year: int):
        bill = db.query(CreditCardBill).filter(
            CreditCardBill.card_id == card_id,
            CreditCardBill.month == month,
            CreditCardBill.year == year
        ).first()

        if not bill:
            bill = CreditCardBill(
                card_id=card_id,
                month=month,
                year=year,
                status=BillStatus.OPEN
            )
            db.add(bill)
            db.flush() # Garante que o bill tenha ID antes de usar
        
        return bill