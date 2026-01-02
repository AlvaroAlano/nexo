from pydantic import BaseModel
from typing import Optional
from datetime import date

# Base: Campos comuns para Criar, Atualizar e Ler
class TransactionBase(BaseModel):
    description: str
    amount: float
    date: date
    type: str # 'expense' ou 'income'
    payment_method: str = "debito" # 'credito', 'debito', 'pix'
    
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    card_id: Optional[int] = None
    
    # --- NOVOS CAMPOS QUE FALTAVAM ---
    is_recurring: bool = False
    frequency: Optional[str] = None
    
    is_installment: bool = False
    installment_total: Optional[int] = 1
    
    debtor_name: Optional[str] = None

# Schema para CRIAÇÃO (Recebe tudo do Base)
class TransactionCreate(TransactionBase):
    pass

# Schema para ATUALIZAÇÃO
class TransactionUpdate(TransactionBase):
    pass

# Schema para RESPOSTA (O que o backend devolve pro frontend)
class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    status: str
    
    # Campos de resposta específicos
    installment_current: Optional[int] = None
    installment_group_id: Optional[str] = None
    bill_id: Optional[int] = None

    class Config:
        from_attributes = True