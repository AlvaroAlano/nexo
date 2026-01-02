from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import uuid
import calendar

from app.models.tables import Transaction, Account, CreditCard, CreditCardBill, TransactionType, TransactionStatus, BillStatus

class FinanceService:
    
    @staticmethod
    def recalculate_account_balance(db: Session, account_id: int):
        """
        Recalcula o saldo de uma conta somando receitas - despesas efetivadas.
        """
        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or Decimal(0)

        expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or Decimal(0)

        new_balance = income - expense
        
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.current_balance = new_balance
            db.commit()
            db.refresh(account)

    @staticmethod
    def _get_or_create_bill(db: Session, card_id: int, month: int, year: int):
        """
        Busca ou cria uma fatura para o cartão no mês/ano especificado.
        """
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
            db.commit()
            db.refresh(bill)
        
        return bill

    @staticmethod
    def process_credit_card_purchase(db: Session, user_id: int, card_id: int, tx_data: dict):
        """
        Processa compras no crédito, gerando parcelas e faturas automaticamente.
        """
        card = db.query(CreditCard).filter(CreditCard.id == card_id).first()
        if not card:
            raise ValueError("Cartão não encontrado")

        base_date = tx_data['date']
        # Converte para Decimal se vier float/str
        amount = Decimal(str(tx_data['amount']))
        description = tx_data['description']
        category_id = tx_data.get('category_id')
        debtor_id = tx_data.get('debtor_id')
        
        is_installment = tx_data.get('is_installment', False)
        installments = tx_data.get('installment_total', 1) if is_installment else 1
        
        created_txs = []
        group_id = str(uuid.uuid4()) if is_installment else None
        
        # Valor da parcela
        installment_value = amount / installments

        for i in range(installments):
            # Lógica de Data da Fatura:
            # Se a compra foi feita antes do fechamento, entra no mês atual.
            # Se foi depois, entra no mês seguinte.
            # Adicionamos +i meses para cada parcela subsequente.
            
            p_date = base_date
            
            if p_date.day >= card.closing_day:
                first_bill_date = p_date + relativedelta(months=1)
            else:
                first_bill_date = p_date
            
            target_bill_date = first_bill_date + relativedelta(months=i)
            
            bill = FinanceService._get_or_create_bill(db, card.id, target_bill_date.month, target_bill_date.year)
            
            # Definindo a data da transação para o dia de vencimento da fatura
            try:
                final_date = date(target_bill_date.year, target_bill_date.month, card.due_day)
            except ValueError:
                # Caso o dia de vencimento não exista no mês (ex: dia 31 em fevereiro), usa o último dia
                last_day = calendar.monthrange(target_bill_date.year, target_bill_date.month)[1]
                final_date = date(target_bill_date.year, target_bill_date.month, last_day)

            new_tx = Transaction(
                user_id=user_id,
                description=f"{description} ({i+1}/{installments})" if is_installment else description,
                amount=installment_value,
                date=final_date, # Data ajustada para o vencimento
                type=TransactionType.EXPENSE,
                payment_method="credito",
                status=TransactionStatus.PENDING, # Crédito é sempre pendente até pagar a fatura
                category_id=category_id,
                card_id=card.id,
                bill_id=bill.id,
                is_installment=is_installment,
                installment_current=i+1 if is_installment else 1,
                installment_total=installments,
                installment_group_id=group_id,
                debtor_id=debtor_id
            )
            db.add(new_tx)
            created_txs.append(new_tx)

        db.commit()
        return created_txs