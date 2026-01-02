from pydantic import BaseModel
from typing import Optional

# Base para leitura e escrita
class CategoryBase(BaseModel):
    name: str
    icon: str
    color: str
    type: str  # 'expense', 'income', 'investment'

# Para criar (POST)
class CategoryCreate(CategoryBase):
    pass

# Para atualizar (PUT) - tudo opcional
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    type: Optional[str] = None

# O que devolvemos para o Frontend
class CategoryResponse(CategoryBase):
    id: int
    # user_id: int

    class Config:
        from_attributes = True