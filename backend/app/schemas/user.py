from typing import Optional

from pydantic import BaseModel, EmailStr

# Propriedades compartilhadas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

# Propriedades para receber via API na criação
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Propriedades para receber via API na atualização
class UserUpdate(UserBase):
    password: Optional[str] = None

# Propriedades para retornar ao banco
class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True # Antigo orm_mode

# O que retornamos para o Frontend (Sem senha!)
class User(UserInDBBase):
    pass

# O que guardamos no banco (Com senha hasheada)
class UserInDB(UserInDBBase):
    hashed_password: str