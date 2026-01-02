from pydantic import BaseModel
from typing import Optional

# Classe Base com os campos comuns
class CreditCardBase(BaseModel):
    name: str
    limit: float
    closing_day: int
    due_day: int
    color: Optional[str] = "#111111" # Cor padrão se não enviar

# Usada para validar o POST (Criação)
class CreditCardCreate(CreditCardBase):
    pass

# Usada para devolver o JSON (Leitura)
class CreditCardResponse(CreditCardBase):
    id: int

    class Config:
        from_attributes = True