from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from typing import List

from app.db.session import get_db
from app.models.tables import Transaction, Account, CreditCard
from app.api.security import get_current_user
from app.models.tables import User

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Saldo Atual REAL (Soma de todas as contas do usuário)
    # Como corrigimos o transactions.py, este valor agora deve diminuir com despesas
    total_balance = db.query(func.sum(Account.current_balance)).filter(
        Account.user_id == current_user.id
    ).scalar() or 0.0

    # 2. Receitas e Despesas do Mês
    month_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year,
        Transaction.type.in_(['receita', 'income', 'entrada'])
    ).scalar() or 0.0

    month_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year,
        Transaction.type.in_(['despesa', 'expense', 'saida'])
    ).scalar() or 0.0

    # 3. Projeção (Saldo Atual + O que vai entrar - O que vai sair do saldo)
    pending_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year,
        Transaction.type.in_(['receita', 'income']),
        Transaction.status == 'pendente'
    ).scalar() or 0.0

    # Despesas pendentes que NÃO SÃO CARTÃO (pois cartão paga na fatura)
    pending_expense_debit = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year,
        Transaction.type.in_(['despesa', 'expense', 'saida']),
        Transaction.status == 'pendente',
        Transaction.payment_method != 'credito'
    ).scalar() or 0.0

    projected_balance = total_balance + pending_income - pending_expense_debit

    # 4. Renda Comprometida
    if month_income > 0:
        commitment_ratio = round((month_expense / month_income) * 100)
    else:
        # Se não ganhou nada mas gastou, comprometimento é total ou infinito
        commitment_ratio = 100 if month_expense > 0 else 0

    return {
        "balance": total_balance,
        "month_income": month_income,
        "month_expense": month_expense,
        "projected_balance": projected_balance,
        "commitment_ratio": commitment_ratio
    }

@router.get("/upcoming")
def get_upcoming_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    limit_date = today + timedelta(days=7)

    upcoming = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= today,
        Transaction.date <= limit_date,
        Transaction.status == 'pendente',
        Transaction.type.in_(['despesa', 'expense', 'saida']),
        Transaction.payment_method != 'credito'
    ).order_by(Transaction.date).limit(5).all()

    return upcoming

@router.get("/charts/categories")
def get_category_chart(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Traz o ID da categoria e a soma dos valores
    results = db.query(
        Transaction.category_id, 
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year,
        Transaction.type.in_(['despesa', 'expense', 'saida'])
    ).group_by(Transaction.category_id).all()
    
    chart_data = []
    # Paleta de cores para o gráfico
    colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6', '#EC4899', '#14B8A6']
    
    from app.models.tables import Category # Importando aqui para evitar ciclo se estivesse no topo

    for i, (cat_id, total) in enumerate(results):
        cat_name = "Outros"
        cat_color = colors[i % len(colors)]

        # Busca o nome real da categoria se existir ID
        if cat_id:
            category = db.query(Category).filter(Category.id == cat_id).first()
            if category:
                cat_name = category.name
                # Se a categoria tem cor salva (ex: bg-red-500), tentamos mapear para Hex ou usamos a cor do gráfico
                # Para simplificar o gráfico, usamos a paleta fixa por enquanto, 
                # mas você pode mapear as classes Tailwind para Hex se quiser perfeição visual.
        
        chart_data.append({
            "name": cat_name,
            "value": total,
            "color": cat_color
        })
    
    return chart_data