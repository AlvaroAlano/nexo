from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum, UniqueConstraint, Index, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
from app.db.session import Base
import enum

# --- ENUMS ---
class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transf"

class BillStatus(str, enum.Enum):
    OPEN = "aberta"
    CLOSED = "fechada"
    PAID = "paga"

class TransactionStatus(str, enum.Enum):
    PAID = "pago"
    PENDING = "pendente"

# --- MIXIN DE AUDITORIA ---
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# --- USUÁRIOS ---
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Cascade ALL: Se apagar o usuário, limpa tudo relacionado a ele
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    debtors = relationship("Debtor", back_populates="user", cascade="all, delete-orphan")

# 1. Categorias
class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    icon = Column(String, default="Tag") 
    color = Column(String, default="bg-zinc-500") 
    type = Column(Enum(TransactionType), default=TransactionType.EXPENSE, nullable=False) 
    
    user = relationship("User", back_populates="categories")
    
    # passive_deletes=True é obrigatório aqui pois usamos ON DELETE SET NULL na transação
    transactions = relationship("Transaction", back_populates="category", passive_deletes=True)

# 2. Contas
class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default="corrente")
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", passive_deletes=True)

# 3. Cartões
class CreditCard(Base, TimestampMixin):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    limit = Column(Numeric(15, 2), nullable=False)
    closing_day = Column(Integer, nullable=False)
    due_day = Column(Integer, nullable=False)
    color = Column(String, default="#000000")
    
    user = relationship("User", back_populates="credit_cards")
    bills = relationship("CreditCardBill", back_populates="card", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="card", passive_deletes=True) 

# 4. Faturas
class CreditCardBill(Base, TimestampMixin):
    __tablename__ = "credit_card_bills"
    
    # Garante que não existam duas faturas iguais (Ex: Nubank - Jan/2025 duplicado)
    __table_args__ = (
        UniqueConstraint('card_id', 'month', 'year', name='uq_bill_card_period'),
    )

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.OPEN, nullable=False)
    
    card = relationship("CreditCard", back_populates="bills")
    transactions = relationship("Transaction", back_populates="bill", passive_deletes=True)

# --- DEVEDORES ---
class Debtor(Base, TimestampMixin):
    __tablename__ = "debtors"
    
    # Garante que não tenha dois "João" para o mesmo usuário
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_debtor_user_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    user = relationship("User", back_populates="debtors")
    
    # Se apagar o devedor, as transações dele NÃO somem (para não quebrar saldo),
    # apenas ficam com debtor_id = NULL.
    transactions = relationship("Transaction", back_populates="debtor", passive_deletes=True)

# 5. Transações
class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    # Índices para o Dashboard voar
    __table_args__ = (
        Index('idx_user_date_type', 'user_id', 'date', 'type'),
        Index('idx_debtor_date', 'debtor_id', 'date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    description = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False) 
    payment_method = Column(String, default="debito") 
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PAID, nullable=False)

    is_recurring = Column(Boolean, default=False)
    frequency = Column(String, nullable=True)
    
    is_installment = Column(Boolean, default=False)
    installment_current = Column(Integer, nullable=True)
    installment_total = Column(Integer, nullable=True) 
    installment_group_id = Column(String, nullable=True)

    # RELACIONAMENTOS (lazy="selectin" para performance)
    # ON DELETE SET NULL: Mantém o histórico financeiro mesmo se a categoria/conta for apagada
    
    debtor_id = Column(Integer, ForeignKey("debtors.id", ondelete="SET NULL"), nullable=True)
    debtor = relationship("Debtor", back_populates="transactions", lazy="selectin")

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category = relationship("Category", back_populates="transactions", lazy="selectin")

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    account = relationship("Account", back_populates="transactions", lazy="selectin")

    card_id = Column(Integer, ForeignKey("credit_cards.id", ondelete="SET NULL"), nullable=True)
    card = relationship("CreditCard", back_populates="transactions", lazy="selectin")

    bill_id = Column(Integer, ForeignKey("credit_card_bills.id", ondelete="SET NULL"), nullable=True)
    bill = relationship("CreditCardBill", back_populates="transactions", lazy="selectin")
    
    user = relationship("User", back_populates="transactions")

# 6. Metas
class Goal(Base, TimestampMixin):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0.0)
    deadline = Column(Date, nullable=True)
    color = Column(String, default="bg-blue-500")
    icon = Column(String, default="target")
    order_index = Column(Integer, default=0)
    user = relationship("User", back_populates="goals")

# ==========================================
# EVENTOS AUTOMÁTICOS (Recálculo de Saldo)
# ==========================================
from sqlalchemy import event
from sqlalchemy.orm import Session

def update_account_balance_on_change(mapper, connection, target):
    """
    Sempre que uma transação for Inserida, Atualizada ou Deletada:
    Recalcula o saldo da conta vinculada no banco.
    """
    if not target.account_id:
        return

    session = Session(bind=connection)
    try:
        # Soma Receitas
        income = session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == target.account_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or 0

        # Soma Despesas
        expense = session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == target.account_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.status == TransactionStatus.PAID
        ).scalar() or 0

        new_balance = income - expense

        # Update Direto
        session.query(Account).filter(Account.id == target.account_id).update(
            {"current_balance": new_balance}
        )
    except Exception as e:
        print(f"Erro no recálculo automático de saldo: {e}")
    finally:
        session.close()

# Registra os ouvintes
event.listen(Transaction, 'after_insert', update_account_balance_on_change)
event.listen(Transaction, 'after_update', update_account_balance_on_change)
event.listen(Transaction, 'after_delete', update_account_balance_on_change)