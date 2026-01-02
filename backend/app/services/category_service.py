from sqlalchemy.orm import Session
from app.models.tables import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

# Listar todas
def get_categories(db: Session):
    # Futuramente: .filter(Category.user_id == user_id)
    return db.query(Category).all()

# Criar
def create_category(db: Session, category: CategoryCreate):
    # Futuramente: user_id=user_id
    db_obj = Category(
        name=category.name,
        icon=category.icon,
        color=category.color,
        type=category.type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Atualizar
def update_category(db: Session, category_id: int, category_data: CategoryUpdate):
    db_obj = db.query(Category).filter(Category.id == category_id).first()
    if not db_obj:
        return None
    
    # Atualiza apenas os campos enviados
    update_data = category_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Deletar
def delete_category(db: Session, category_id: int):
    db_obj = db.query(Category).filter(Category.id == category_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False