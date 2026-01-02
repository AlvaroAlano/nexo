from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from typing import List
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.models.tables import Transaction, User, Account
from app.api.security import get_current_user
from app.schemas.transaction import TransactionResponse # <--- Importante

router = APIRouter()

class DebtorSummary(BaseModel):
    name: str
    total_debt: float
    total_paid: float
    balance: float
    count: int
    is_fully_paid: bool

class DebtsDashboard(BaseModel):
    total_receivable: float
    debtors: List[DebtorSummary]

class PaymentRequest(BaseModel):
    amount: float

@router.get("/summary", response_model=DebtsDashboard)
def get_debts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(
        Transaction.debtor_name,
        func.sum(case((Transaction.type != 'income', func.abs(Transaction.amount)), else_=0)).label("debt"),
        func.sum(case((Transaction.type == 'income', func.abs(Transaction.amount)), else_=0)).label("paid"),
        func.count(Transaction.id).label("cnt")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.debtor_name.isnot(None),
        Transaction.debtor_name != ""
    ).group_by(Transaction.debtor_name).all()

    debtors_list = []
    total_global = 0

    for r in rows:
        debt = r.debt or 0
        paid = r.paid or 0
        balance = debt - paid
        is_paid = balance <= 0.01 

        if not is_paid:
            total_global += balance

        debtors_list.append({
            "name": r.debtor_name,
            "total_debt": debt,
            "total_paid": paid,
            "balance": max(balance, 0),
            "count": r.cnt,
            "is_fully_paid": is_paid
        })

    debtors_list.sort(key=lambda x: (x['is_fully_paid'], -x['balance']))

    return {
        "total_receivable": total_global,
        "debtors": debtors_list
    }

@router.post("/{debtor_name}/pay")
def register_payment(
    debtor_name: str,
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser positivo")

    user_account = db.query(Account).filter(Account.user_id == current_user.id).first()

    pay_tx = Transaction(
        description=f"Pgto. {debtor_name}",
        amount=payment.amount,
        date=date.today(),
        type="income",
        payment_method="pix",
        debtor_name=debtor_name,
        user_id=current_user.id,
        account_id=user_account.id if user_account else None
    )
    
    if user_account:
        user_account.current_balance += payment.amount

    db.add(pay_tx)
    db.commit()
    return {"message": "Pagamento recebido!"}

# --- NOVA ROTA: HISTÓRICO DETALHADO ---
@router.get("/{debtor_name}/history", response_model=List[TransactionResponse])
def get_debtor_history(
    debtor_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna todas as transações (compras e pagamentos) de uma pessoa específica"""
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.debtor_name == debtor_name
    ).order_by(desc(Transaction.date), desc(Transaction.id)).all()