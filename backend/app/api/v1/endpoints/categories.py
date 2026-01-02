from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.tables import Category, User, TransactionType
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.api.security import get_current_user

router = APIRouter()

# Rota: Listar (GET) - Agora filtrada por usuário!
@router.get("/", response_model=List[CategoryResponse])
def read_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Category).filter(Category.user_id == current_user.id).all()

# Rota: Criar (POST) - Agora insere o ID do usuário!
@router.post("/", response_model=CategoryResponse)
def create_new_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificação simples para garantir que o tipo é válido (income, expense, transf)
    # O Pydantic já valida string, mas aqui garantimos conversão para Enum se necessário
    
    db_obj = Category(
        name=category.name,
        icon=category.icon,
        color=category.color,
        type=category.type, 
        user_id=current_user.id # <--- OBRIGATÓRIO
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Rota: Editar (PUT)
@router.put("/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int, 
    category_update: CategoryUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Busca garantindo que pertence ao usuário
    db_obj = db.query(Category).filter(
        Category.id == category_id, 
        Category.user_id == current_user.id
    ).first()
    
    if not db_obj:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Atualiza apenas campos enviados
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj

# Rota: Excluir (DELETE)
@router.delete("/{category_id}")
def delete_existing_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_obj = db.query(Category).filter(
        Category.id == category_id, 
        Category.user_id == current_user.id
    ).first()
    
    if not db_obj:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
    db.delete(db_obj)
    db.commit()
    return {"message": "Deletada com sucesso"}