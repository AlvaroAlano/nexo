from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import date, timedelta
from decimal import Decimal
import calendar

# Importa os modelos e enums novos
from app.models.tables import Transaction, Account, Category, TransactionType, TransactionStatus

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    # ADICIONADO user_id: Obrigatório para não vazar dados de outros usuários
    def get_summary(self, user_id: int, month: int, year: int):
        
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        # 1. Saldo Atual (Filtrado por USER_ID!)
        # Retorna Decimal para não perder precisão
        current_balance = self.db.query(func.sum(Account.current_balance)).filter(
            Account.user_id == user_id
        ).scalar() or Decimal(0)

        # Filtros comuns para reutilizar
        base_filters = [
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ]

        # 2. Fluxo do Mês
        income = self.db.query(func.sum(Transaction.amount)).filter(
            *base_filters,
            Transaction.type == TransactionType.INCOME
        ).scalar() or Decimal(0)

        expense = self.db.query(func.sum(Transaction.amount)).filter(
            *base_filters,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or Decimal(0)

        # 3. Pendências (Runway)
        # Usamos TransactionStatus.PENDING
        pending_income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.date <= end_date,
            Transaction.status == TransactionStatus.PENDING,
            Transaction.type == TransactionType.INCOME
        ).scalar() or Decimal(0)

        pending_expense = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.date <= end_date,
            Transaction.status == TransactionStatus.PENDING,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or Decimal(0)

        projected_balance = current_balance + pending_income - pending_expense

        # 4. Commitment Ratio
        commitment_ratio = 0
        if income > 0:
            commitment_ratio = int((expense / income) * 100)
        elif expense > 0:
            commitment_ratio = 100 

        return {
            "balance": current_balance,
            "month_income": income,
            "month_expense": expense,
            "projected_balance": projected_balance,
            "commitment_ratio": commitment_ratio
        }

    def get_category_breakdown(self, user_id: int, month: int, year: int):
        """Retorna dados para o gráfico de Donut (Filtrado por usuário)"""
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        results = self.db.query(
            Category.name,
            Category.color,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction, Transaction.category_id == Category.id)\
         .filter(
            Transaction.user_id == user_id, # Segurança
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == TransactionType.EXPENSE
         )\
         .group_by(Category.name, Category.color)\
         .order_by(text('total DESC'))\
         .all()

        return [
            {"name": r.name, "value": r.total, "color": r.color} 
            for r in results
        ]

    def get_upcoming_transactions(self, user_id: int, days: int = 7):
        """Busca contas a pagar (Despesas Pendentes) nos próximos X dias"""
        today = date.today()
        limit_date = today + timedelta(days=days)

        results = self.db.query(Transaction).filter(
            Transaction.user_id == user_id, # Segurança
            Transaction.type == TransactionType.EXPENSE,
            Transaction.status == TransactionStatus.PENDING,
            Transaction.date >= today,
            Transaction.date <= limit_date
        ).order_by(Transaction.date.asc()).limit(10).all()

        return results