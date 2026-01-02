from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db.session import get_db
from app.api.security import get_current_user
# Adicione TransactionType e TransactionStatus aqui
from app.models.tables import Goal, User, Transaction, Account, TransactionType, TransactionStatus
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate, GoalDeposit

router = APIRouter()

# 1. LISTAR
@router.get("/", response_model=List[GoalResponse])
def read_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.order_index).all()

# 2. CRIAR
@router.post("/", response_model=GoalResponse)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    last_goal = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.order_index.desc()).first()
    new_order = (last_goal.order_index + 1) if last_goal else 0
    
    db_goal = Goal(
        **goal.dict(exclude={'order_index'}), 
        user_id=current_user.id, 
        order_index=new_order
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

# 3. ATUALIZAR
@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    for key, value in goal_update.dict(exclude_unset=True).items():
        setattr(db_goal, key, value)

    db.commit()
    db.refresh(db_goal)
    return db_goal

# 4. DELETAR
@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.delete(db_goal)
    db.commit()
    return {"detail": "Meta excluída"}

# 5. REORDENAR
@router.post("/reorder")
def reorder_goals(id_list: List[int], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    goals_map = {g.id: g for g in goals}
    for index, goal_id in enumerate(id_list):
        if goal_id in goals_map:
            goals_map[goal_id].order_index = index
    db.commit()
    return {"detail": "Ordem atualizada"}

# 6. DEPÓSITO (Corrigido com Enums)
@router.post("/{goal_id}/deposit", response_model=GoalResponse)
def deposit_to_goal(
    goal_id: int, 
    deposit: GoalDeposit, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    transaction = Transaction(
        description=f"Depósito Meta: {db_goal.name}",
        amount=-abs(deposit.amount), 
        date=date.today(),
        type=TransactionType.EXPENSE, # <--- CORRIGIDO: Era "despesa"
        payment_method="saldo",
        status=TransactionStatus.PAID, # Importante definir como pago
        account_id=account.id if account else None,
        user_id=current_user.id,
        category_id=None
    )
    db.add(transaction)

    # Nota: O trigger automático no tables.py já deve atualizar o saldo da conta,
    # mas mantemos aqui por segurança da lógica de meta.
    if account:
        account.current_balance -= abs(deposit.amount)

    db_goal.current_amount += abs(deposit.amount)

    db.commit()
    db.refresh(db_goal)
    return db_goal

# 7. SAQUE / RESGATE (Corrigido com Enums)
@router.post("/{goal_id}/withdraw", response_model=GoalResponse)
def withdraw_from_goal(
    goal_id: int, 
    deposit: GoalDeposit, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    if db_goal.current_amount < deposit.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente na meta")

    account = db.query(Account).filter(Account.user_id == current_user.id).first()

    transaction = Transaction(
        description=f"Resgate Meta: {db_goal.name}",
        amount=abs(deposit.amount),
        date=date.today(),
        type=TransactionType.INCOME, # <--- CORRIGIDO: Era "receita"
        payment_method="saldo",
        status=TransactionStatus.PAID,
        account_id=account.id if account else None,
        user_id=current_user.id,
        category_id=None
    )
    db.add(transaction)

    if account:
        account.current_balance += abs(deposit.amount)

    db_goal.current_amount -= abs(deposit.amount)

    db.commit()
    db.refresh(db_goal)
    return db_goal