from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import date, timedelta
import calendar
from app.models.tables import Transaction, Account, Category

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, month: int, year: int):
        # 1. Definir intervalo do mês
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        # 2. Saldo Atual (Vem das Contas Bancárias - Já considera tudo que foi pago)
        current_balance = self.db.query(func.sum(Account.current_balance)).scalar() or 0.0

        # 3. Fluxo do Mês (Relatório: Tudo que vence neste mês, pago ou não)
        income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == 'receita'
        ).scalar() or 0.0

        expense = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == 'despesa'
        ).scalar() or 0.0

        # 4. Cálculo do Runway (Projeção de Saldo)
        # Saldo Projetado = Saldo Hoje + (Receitas Pendentes do Mês - Despesas Pendentes do Mês)
        # Usamos 'status' == 'pendente' para ser exato.
        
        pending_income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.date <= end_date, # Até o fim do mês
            Transaction.status == 'pendente',
            Transaction.type == 'receita'
        ).scalar() or 0.0

        pending_expense = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.date <= end_date, # Até o fim do mês
            Transaction.status == 'pendente',
            Transaction.type == 'despesa'
        ).scalar() or 0.0

        projected_balance = current_balance + pending_income - pending_expense

        # 5. Commitment Ratio (Renda Comprometida)
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

    def get_category_breakdown(self, month: int, year: int):
        """Retorna dados para o gráfico de Donut"""
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        results = self.db.query(
            Category.name,
            Category.color,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction, Transaction.category_id == Category.id)\
         .filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == 'despesa'
         )\
         .group_by(Category.name, Category.color)\
         .order_by(text('total DESC'))\
         .all()

        return [
            {"name": r.name, "value": r.total, "color": r.color} 
            for r in results
        ]

    # --- O MÉTODO QUE FALTAVA ---
    def get_upcoming_transactions(self, days: int = 7):
        """Busca contas a pagar (Despesas Pendentes) nos próximos X dias"""
        today = date.today()
        limit_date = today + timedelta(days=days)

        results = self.db.query(Transaction).filter(
            Transaction.type == 'despesa',
            Transaction.status == 'pendente', # Só o que falta pagar
            Transaction.date >= today,
            Transaction.date <= limit_date
        ).order_by(Transaction.date.asc()).limit(10).all()

        return results