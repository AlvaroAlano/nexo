from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal

# Base: Campos comuns
class TransactionBase(BaseModel):
    description: str
    amount: Decimal # CORREÇÃO: Decimal para precisão financeira
    date: date
    type: str 
    payment_method: str = "debito"
    
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    card_id: Optional[int] = None
    
    is_recurring: bool = False
    frequency: Optional[str] = None
    
    is_installment: bool = False
    installment_total: Optional[int] = 1
    
    debtor_id: Optional[int] = None

    # Configuração para o Pydantic saber converter Decimal para JSON
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: float(v)}
    )

    @field_validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v

    @field_validator('type')
    def validate_type(cls, v):
        v = v.lower()
        if v in ['receita', 'entrada']: return 'income'
        if v in ['despesa', 'saida', 'gasto']: return 'expense'
        if v not in ['income', 'expense', 'transf']:
            raise ValueError("Tipo inválido. Use: income, expense")
        return v

    # CORREÇÃO: Regra de Negócio Blindada
    @model_validator(mode='after')
    def validate_payment_logic(self):
        # 1. Se é parcelado, TEM QUE SER Crédito e TER Cartão
        if self.is_installment:
            if self.payment_method != 'credito':
                raise ValueError("Parcelamento só é permitido no Crédito.")
            if not self.card_id:
                raise ValueError("Transação parcelada exige um Cartão vinculado.")
            if not self.installment_total or self.installment_total < 2:
                # Se mandou parcelado 1x, corrige silenciosamente para à vista
                self.is_installment = False
                self.installment_total = 1
        
        # 2. Se é Crédito, TEM QUE TER Cartão (mesmo à vista)
        if self.payment_method == 'credito' and not self.card_id:
             raise ValueError("Pagamento no Crédito exige selecionar um cartão.")

        return self

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    status: str
    
    installment_current: Optional[int] = None
    installment_group_id: Optional[str] = None
    bill_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: float(v)}