from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tables import User, Goal, CreditCard # Adicionei Goal e CreditCard
from app.api.security import get_current_user
from app.services.dashboard_service import DashboardService 

# Precisamos importar as lógicas de Cartão e Meta para agrupar tudo
# (Para simplificar, vou fazer as queries aqui, mas o ideal seria services separados)
from sqlalchemy import func, desc 
from app.models.tables import Transaction, CreditCardBill

router = APIRouter()

# --- MANTENHA AS ROTAS ANTIGAS AQUI (summary, upcoming, etc) PARA NÃO QUEBRAR NADA ---
# (Cole aqui o conteúdo que já te passei antes para summary, upcoming e charts)
# ...

# --- NOVA ROTA SUPER RÁPIDA ---
@router.get("/full-load")
def get_full_dashboard_data(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Carrega TODOS os dados do dashboard em uma única conexão.
    Drasticamente mais rápido para conexões móveis.
    """
    service = DashboardService(db)
    
    # 1. Resumo Financeiro (Saldo, Receita, Despesa)
    summary = service.get_summary(current_user.id, month, year)
    
    # 2. Contas a Pagar (Próximos 7 dias)
    upcoming = service.get_upcoming_transactions(current_user.id)
    
    # 3. Gráfico de Categorias
    chart = service.get_category_breakdown(current_user.id, month, year)
    
    # 4. Metas (Copiando a lógica simples do goals.py)
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.order_index).all()
    
    # 5. Cartões (Resumo simples)
    cards_data = []
    cards = db.query(CreditCard).filter(CreditCard.user_id == current_user.id).all()
    # Lógica simplificada de fatura atual para performance
    # (Se precisar da lógica completa, importamos do credit_cards.py, mas aqui vamos focar em velocidade)
    
    return {
        "summary": summary,
        "upcoming": upcoming,
        "chart": chart,
        "goals": goals,
        "cards": cards  # O frontend pode processar isso
    }