from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
import calendar

from app.db.session import get_db
from app.models.tables import Transaction, User
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.api.security import get_current_user
from app.services.transaction_service import TransactionService

router = APIRouter()

# 1. CRIAR
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TransactionService(db)
    try:
        # Passamos o user_id para garantir que a transação seja do usuário logado
        return service.create(current_user.id, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao criar transação: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar transação.")

# 2. LISTAR (Mantemos aqui pois é apenas leitura e filtros)
@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    limit: int = 100, 
    month: int = None, 
    year: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id) 

    if month and year:
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        query = query.filter(Transaction.date >= start_date, Transaction.date <= end_date)

    # Dica: Como configuramos lazy="selectin" no tables.py, 
    # o SQLAlchemy já vai carregar categorias/contas de forma otimizada!
    return query.order_by(desc(Transaction.date), desc(Transaction.id)).limit(limit).all()

# 3. EDITAR
@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TransactionService(db)
    try:
        updated_tx = service.update(current_user.id, transaction_id, transaction)
        if not updated_tx:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        return updated_tx
    except Exception as e:
        print(f"Erro ao atualizar: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 4. DELETAR
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TransactionService(db)
    try:
        success = service.delete(current_user.id, transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        return {"message": "Transação excluída"}
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        raise HTTPException(status_code=400, detail=str(e))