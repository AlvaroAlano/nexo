from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import datetime
from app.models.tables import Transaction, Category

class DashboardService:
    @staticmethod
    def get_summary(db: Session, user_id: int, month: int, year: int):
        # Cálculos de Entrada e Saída usando CASE WHEN para ser compatível com Postgres
        # Soma apenas se type for 'income', senão 0
        income = db.query(func.sum(Transaction.value)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar() or 0

        # Soma apenas se type for 'expense', senão 0
        expense = db.query(func.sum(Transaction.value)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar() or 0

        balance = income - expense

        return {
            "income": float(income),
            "expense": float(expense),
            "balance": float(balance)
        }

    @staticmethod
    def get_upcoming_transactions(db: Session, user_id: int):
        today = datetime.now().date()
        
        # AQUI ESTAVA O ERRO: Removemos 'despesa', 'saida', etc.
        # Usamos apenas 'expense' que é o que o banco aceita.
        upcoming = db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.date >= today,
                Transaction.status == 'pending',
                Transaction.type == 'expense' 
            )\
            .order_by(Transaction.date.asc())\
            .limit(5)\
            .all()
            
        return upcoming

    @staticmethod
    def get_category_chart(db: Session, user_id: int, month: int, year: int):
        # Busca gastos por categoria
        results = db.query(
            Category.name,
            Category.color,
            func.sum(Transaction.value).label('total')
        )\
        .join(Transaction)\
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        )\
        .group_by(Category.id, Category.name, Category.color)\
        .all()

        total_expenses = sum(r.total for r in results) if results else 0
        
        chart_data = []
        if total_expenses > 0:
            for name, color, total in results:
                val = float(total) if total else 0.0
                percent = (val / float(total_expenses)) * 100
                chart_data.append({
                    "name": name,
                    "value": val,
                    "color": color,
                    "percent": round(percent, 1)
                })
        
        return chart_data