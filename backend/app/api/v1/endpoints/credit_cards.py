from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date
import calendar
from pydantic import BaseModel

from app.db.session import get_db
# Importamos TransactionStatus para usar Enums
from app.models.tables import CreditCard, Transaction, CreditCardBill, User, TransactionStatus
from app.api.security import get_current_user
from app.schemas.credit_card import CreditCardCreate, CreditCardResponse
from app.schemas.transaction import TransactionResponse

router = APIRouter()

class CreditCardWithInvoice(BaseModel):
    id: int
    name: str
    limit: float
    color: Optional[str] = "#111"
    invoice: float      
    total_debt: float   
    due_day: int
    closing_day: int

    class Config:
        from_attributes = True

# --- ROTA: CRIAR CARTÃO ---
@router.post("/", response_model=CreditCardResponse)
def create_credit_card(
    card: CreditCardCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_card = CreditCard(
        name=card.name,
        limit=card.limit,
        closing_day=card.closing_day,
        due_day=card.due_day,
        color=card.color,
        user_id=current_user.id
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

# --- ROTA: LISTAR CARTÕES ---
@router.get("/", response_model=List[CreditCardWithInvoice])
def read_credit_cards(
    month: int = None, 
    year: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not month or not year:
            today = date.today()
            month = today.month
            year = today.year

        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        cards = db.query(CreditCard).filter(CreditCard.user_id == current_user.id).all()
        
        result = []

        for card in cards:
            # Gasto do Mês
            current_invoice = db.query(func.sum(Transaction.amount)).join(
                CreditCardBill, Transaction.bill_id == CreditCardBill.id
            ).filter(
                CreditCardBill.card_id == card.id,      
                Transaction.date >= start_date,         
                Transaction.date <= end_date,
                Transaction.payment_method == 'credito'
            ).scalar() or 0.0
            
            # Dívida Total (Usando Enum PENDING)
            total_debt = db.query(func.sum(Transaction.amount)).join(
                CreditCardBill, Transaction.bill_id == CreditCardBill.id
            ).filter(
                CreditCardBill.card_id == card.id,
                Transaction.status == TransactionStatus.PENDING 
            ).scalar() or 0.0
            
            result.append({
                "id": card.id,
                "name": card.name,
                "limit": card.limit,
                "color": card.color,
                "invoice": current_invoice,
                "total_debt": total_debt,
                "due_day": card.due_day,
                "closing_day": card.closing_day
            })

        return result

    except Exception as e:
        print(f"ERRO READ_CREDIT_CARDS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ROTA: EDITAR CARTÃO ---
@router.put("/{card_id}", response_model=CreditCardResponse)
def update_credit_card(
    card_id: int,
    card_in: CreditCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado."
        )

    card.name = card_in.name
    card.limit = card_in.limit
    card.closing_day = card_in.closing_day
    card.due_day = card_in.due_day
    
    if card_in.color:
        card.color = card_in.color

    db.commit()
    db.refresh(card)

    return card

# --- ROTA: DETALHES DA FATURA ---
@router.get("/{card_id}/invoice/transactions", response_model=List[TransactionResponse])
def read_card_invoice_transactions(
    card_id: int,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    transactions = db.query(Transaction).join(
        CreditCardBill, Transaction.bill_id == CreditCardBill.id
    ).filter(
        CreditCardBill.card_id == card_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.payment_method == 'credito'
    ).order_by(desc(Transaction.date)).all()

    return transactions