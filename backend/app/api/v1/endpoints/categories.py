from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import category_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota: Listar (GET)
@router.get("/", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    return category_service.get_categories(db)

# Rota: Criar (POST)
@router.post("/", response_model=CategoryResponse)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, category)

# Rota: Editar (PUT) - ESSENCIAL PARA O BOTÃO EDITAR
@router.put("/{category_id}", response_model=CategoryResponse)
def update_existing_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    updated = category_service.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return updated

# Rota: Excluir (DELETE) - ESSENCIAL PARA O BOTÃO EXCLUIR
@router.delete("/{category_id}")
def delete_existing_category(category_id: int, db: Session = Depends(get_db)):
    success = category_service.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"message": "Deletada com sucesso"}