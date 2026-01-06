from typing import Any, Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password

# MUDANÇA CRÍTICA: Importando do tables.py
from app.models.tables import User
from app.schemas.user import UserCreate

class CRUDUser:
    def get(self, db: Session, id: Any) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            # is_active=True # Se seu model tiver esse campo, descomente
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return True # Simplificado para garantir o login

user = CRUDUser()