from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import date
from app.db.session import Base
import enum

class BillStatus(str, enum.Enum):
    OPEN = "aberta"
    CLOSED = "fechada"
    PAID = "paga"

class TransactionStatus(str, enum.Enum):
    PAID = "pago"
    PENDING = "pendente"

# --- NOVO: TABELA DE USUÁRIOS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    
    # Relacionamentos (Opcional, mas útil para o futuro)
    categories = relationship("Category", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    credit_cards = relationship("CreditCard", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    
    goals = relationship("Goal", back_populates="user")

# 1. Categorias
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Vínculo com Usuário
    
    name = Column(String, nullable=False)
    icon = Column(String, default="Tag") 
    color = Column(String, default="bg-zinc-500") 
    type = Column(String, default="expense") 
    
    user = relationship("User", back_populates="categories")

# 2. Contas Bancárias
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Vínculo com Usuário
    
    name = Column(String, nullable=False)
    type = Column(String, default="corrente")
    current_balance = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="accounts")

# 3. Cartões de Crédito
class CreditCard(Base):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Vínculo com Usuário

    name = Column(String, nullable=False)
    limit = Column(Float, nullable=False)
    closing_day = Column(Integer, nullable=False)
    due_day = Column(Integer, nullable=False)
    color = Column(String, default="#000000")
    
    user = relationship("User", back_populates="credit_cards")
    bills = relationship("CreditCardBill", back_populates="card")

# 4. Faturas do Cartão
class CreditCardBill(Base):
    __tablename__ = "credit_card_bills"
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("credit_cards.id"))
    
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String, default=BillStatus.OPEN)
    
    card = relationship("CreditCard", back_populates="bills")
    transactions = relationship("Transaction", back_populates="bill")

# 5. Transações
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Vínculo com Usuário

    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
    type = Column(String, nullable=False) 
    payment_method = Column(String, default="debito") 
    status = Column(String, default="pago")

    is_recurring = Column(Boolean, default=False)
    frequency = Column(String, nullable=True)
    
    is_installment = Column(Boolean, default=False)
    installment_current = Column(Integer, nullable=True)
    installment_total = Column(Integer, nullable=True) 
    installment_group_id = Column(String, nullable=True)

    debtor_name = Column(String, nullable=True) 
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    bill_id = Column(Integer, ForeignKey("credit_card_bills.id"), nullable=True)
    
    bill = relationship("CreditCardBill", back_populates="transactions")
    category = relationship("Category")
    account = relationship("Account")
    user = relationship("User", back_populates="transactions")
    
# 6. Metas e Objetivos (ADICIONE NO FINAL DO ARQUIVO)
class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)     # Valor Alvo
    current_amount = Column(Float, default=0.0)       # Valor Atual
    deadline = Column(Date, nullable=True)            # Prazo
    color = Column(String, default="bg-blue-500")     # Cor Visual
    icon = Column(String, default="target")           # Ícone (plane, car, etc)
    order_index = Column(Integer, default=0)          # Para o Drag & Drop
    
    user = relationship("User", back_populates="goals")