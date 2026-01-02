from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tables import User
from app.api.security import get_current_user
# Importamos o especialista (Service) que já tem a lógica corrigida
from app.services.dashboard_service import DashboardService 

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # O código "grande" agora está escondido aqui dentro dessa função segura
    service = DashboardService(db)
    return service.get_summary(current_user.id, month, year)

@router.get("/upcoming")
def get_upcoming_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DashboardService(db)
    return service.get_upcoming_transactions(current_user.id)

@router.get("/charts/categories")
def get_category_chart(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DashboardService(db)
    return service.get_category_breakdown(current_user.id, month, year)