from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Base comum (campos que existem na criação e leitura)
class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    deadline: Optional[date] = None
    color: Optional[str] = "bg-blue-500"
    icon: Optional[str] = "target"
    order_index: Optional[int] = 0

# O que precisamos receber para CRIAR
class GoalCreate(GoalBase):
    pass

# O que podemos receber para ATUALIZAR (Tudo opcional)
class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    deadline: Optional[date] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None

# O que devolvemos para o Frontend (inclui ID e user_id)
class GoalResponse(GoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
    
# Schema simples apenas para o depósito
class GoalDeposit(BaseModel):
    amount: float