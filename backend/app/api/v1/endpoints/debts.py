from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal

from app.db.session import get_db
from app.models.tables import Transaction, User, Account, Debtor, TransactionType, TransactionStatus
from app.api.security import get_current_user
from app.schemas.transaction import TransactionResponse

router = APIRouter()

# --- SCHEMAS LOCAIS (Com Decimal) ---
class DebtorSchema(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None

class DebtorSummary(BaseModel):
    id: int
    name: str
    total_debt: Decimal
    total_paid: Decimal
    balance: Decimal
    count: int
    is_fully_paid: bool

    # Garante que Decimal seja enviado como float/string no JSON
    model_config = ConfigDict(json_encoders={Decimal: lambda v: float(v)})

class DebtsDashboard(BaseModel):
    total_receivable: Decimal
    debtors: List[DebtorSummary]

    model_config = ConfigDict(json_encoders={Decimal: lambda v: float(v)})

class PaymentRequest(BaseModel):
    amount: Decimal # Float -> Decimal
    date: date
    payment_method: str = "pix"
    account_id: int

# 1. Dashboard de Dívidas
@router.get("/summary", response_model=DebtsDashboard)
def get_debts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debtors = db.query(Debtor).filter(Debtor.user_id == current_user.id).all()
    
    summary_list = []
    total_receivable_global = Decimal(0)

    for debtor in debtors:
        # CORREÇÃO: Usando Enums (TransactionType.INCOME) e Decimal
        stats = db.query(
            func.sum(case((Transaction.type != TransactionType.INCOME, func.abs(Transaction.amount)), else_=0)).label("debt"),
            func.sum(case((Transaction.type == TransactionType.INCOME, func.abs(Transaction.amount)), else_=0)).label("paid"),
            func.count(Transaction.id).label("cnt")
        ).filter(
            Transaction.debtor_id == debtor.id
        ).first()

        debt = stats.debt or Decimal(0)
        paid = stats.paid or Decimal(0)
        balance = debt - paid
        
        # Considera pago se o saldo for menor que 1 centavo
        is_paid = balance <= Decimal("0.01")

        if not is_paid:
            total_receivable_global += balance

        if stats.cnt > 0:
            summary_list.append({
                "id": debtor.id,
                "name": debtor.name,
                "total_debt": debt,
                "total_paid": paid,
                "balance": max(balance, Decimal(0)),
                "count": stats.cnt,
                "is_fully_paid": is_paid
            })

    summary_list.sort(key=lambda x: (x['is_fully_paid'], -x['balance']))

    return {
        "total_receivable": total_receivable_global,
        "debtors": summary_list
    }

# 2. Registrar Pagamento
@router.post("/{debtor_id}/pay")
def register_payment(
    debtor_id: int,
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser positivo")

    debtor = db.query(Debtor).filter(Debtor.id == debtor_id, Debtor.user_id == current_user.id).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Devedor não encontrado")

    account = db.query(Account).filter(Account.id == payment.account_id, Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=400, detail="Conta de destino inválida")

    # CORREÇÃO: Cria a transação usando Enums
    pay_tx = Transaction(
        description=f"Pgto. {debtor.name}",
        amount=payment.amount,
        date=payment.date,
        type=TransactionType.INCOME, # Enum correto
        payment_method=payment.payment_method,
        status=TransactionStatus.PAID,
        debtor_id=debtor.id,
        user_id=current_user.id,
        account_id=account.id
    )
    
    # CORREÇÃO: REMOVIDA A LINHA 'account.current_balance += ...'
    # O Trigger automático no tables.py (after_insert) vai recalcular o saldo sozinho.
    
    db.add(pay_tx)
    db.commit()
    return {"message": "Pagamento registrado com sucesso!"}

# 3. Histórico
@router.get("/{debtor_id}/history", response_model=List[TransactionResponse])
def get_debtor_history(
    debtor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TransactionResponse já sabe lidar com Decimal via ConfigDict do Schema
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.debtor_id == debtor_id
    ).order_by(desc(Transaction.date), desc(Transaction.id)).all()

# 4. Apagar Devedor
@router.delete("/{debtor_id}")
def delete_debtor(
    debtor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debtor = db.query(Debtor).filter(Debtor.id == debtor_id, Debtor.user_id == current_user.id).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Devedor não encontrado")

    # O Cascade configurado no tables.py (ondelete="SET NULL") vai desvincular as transações automaticamente
    # ou apagá-las se estiver configurado cascade="all, delete-orphan" no relacionamento.
    # No seu código atual de tables.py, está como SET NULL no banco e delete-orphan no ORM.
    
    db.delete(debtor)
    db.commit()
    return {"message": "Devedor removido."}