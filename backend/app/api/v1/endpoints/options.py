from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.tables import Category, CreditCard
# Se você tiver schemas definidos, seria ideal usá-los, mas vamos retornar o objeto direto por enquanto
# from app.schemas.category import CategoryOut
# from app.schemas.credit_card import CreditCardOut

router = APIRouter()

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Retorna lista de categorias para o select.
    Rota: /api/v1/options/categories
    """
    return db.query(Category).all()

@router.get("/credit-cards")
def get_credit_cards(db: Session = Depends(get_db)):
    """
    Retorna lista de cartões para o select.
    Rota: /api/v1/options/credit-cards
    """
    return db.query(CreditCard).all()