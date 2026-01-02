from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from dateutil.relativedelta import relativedelta

from app.db.session import get_db
from app.models.tables import Transaction, Account, CreditCardBill, CreditCard, User
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.api.security import get_current_user 

router = APIRouter()

# --- HELPER: ATUALIZAÇÃO SEGURA DE SALDO ---
def update_account_balance(account: Account, amount: float, type: str, operation: str = "create"):
    """
    operation: 'create' (novo lançamento) ou 'delete' (remoção/estorno)
    """
    is_expense = type in ["despesa", "expense", "saida"]
    is_income = type in ["receita", "income", "entrada"]

    if operation == "create":
        if is_expense:
            account.current_balance -= amount
        elif is_income:
            account.current_balance += amount
            
    elif operation == "delete":
        # Estorno (inverso)
        if is_expense:
            account.current_balance += amount 
        elif is_income:
            account.current_balance -= amount 

# 1. CRIAR TRANSAÇÃO
@router.post("/", response_model=List[TransactionResponse])
def create_transaction(
    transaction: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --- CORREÇÃO AUTOMÁTICA DE CONTA ---
    # Se não foi enviado account_id e não é cartão de crédito,
    # buscamos a conta 'Carteira' (ou a primeira conta do usuário)
    if not transaction.account_id and transaction.payment_method != 'credito':
        default_account = db.query(Account).filter(Account.user_id == current_user.id).first()
        if default_account:
            transaction.account_id = default_account.id
    # ------------------------------------

    created_transactions = []

    # 1. Lógica para PARCELAMENTO
    if transaction.is_installment and transaction.installment_total > 1:
        import uuid
        group_id = str(uuid.uuid4())
        
        base_date = transaction.date
        base_amount = transaction.amount / transaction.installment_total 

        for i in range(transaction.installment_total):
            current_date = base_date + relativedelta(months=i)
            
            new_tx = Transaction(
                description=f"{transaction.description} ({i+1}/{transaction.installment_total})",
                amount=base_amount, 
                date=current_date,
                type=transaction.type,
                payment_method=transaction.payment_method,
                category_id=transaction.category_id,
                account_id=transaction.account_id,
                is_installment=True,
                installment_current=i+1,
                installment_total=transaction.installment_total,
                installment_group_id=group_id,
                debtor_name=transaction.debtor_name,
                user_id=current_user.id 
            )

            # Lógica de Cartão vs Conta
            if transaction.payment_method == 'credito' and transaction.card_id:
                bill = get_or_create_bill(db, transaction.card_id, current_date.month, current_date.year)
                new_tx.bill_id = bill.id
                new_tx.status = 'pendente'
            else:
                # Se for conta corrente e a data for hoje ou passado, atualiza saldo
                if transaction.account_id and current_date <= date.today():
                    account = db.query(Account).filter(Account.id == transaction.account_id).first()
                    if account:
                        update_account_balance(account, base_amount, transaction.type, "create")

            db.add(new_tx)
            created_transactions.append(new_tx)

    # 2. Lógica Transação ÚNICA
    else:
        new_tx = Transaction(
            description=transaction.description,
            amount=transaction.amount,
            date=transaction.date,
            type=transaction.type,
            payment_method=transaction.payment_method,
            category_id=transaction.category_id,
            account_id=transaction.account_id,
            is_recurring=transaction.is_recurring,
            frequency=transaction.frequency,
            debtor_name=transaction.debtor_name,
            user_id=current_user.id
        )

        if transaction.payment_method == 'credito' and transaction.card_id:
            bill = get_or_create_bill(db, transaction.card_id, transaction.date.month, transaction.date.year)
            new_tx.bill_id = bill.id
            new_tx.status = 'pendente'
        else:
            if transaction.account_id:
                account = db.query(Account).filter(Account.id == transaction.account_id).first()
                if account:
                    update_account_balance(account, transaction.amount, transaction.type, "create")

        db.add(new_tx)
        created_transactions.append(new_tx)

    db.commit()
    for tx in created_transactions:
        db.refresh(tx)
        
    return created_transactions

# 2. LISTAR
@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    limit: int = 100, 
    month: int = None, 
    year: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id) 

    if month and year:
        import calendar
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        query = query.filter(Transaction.date >= start_date, Transaction.date <= end_date)

    return query.order_by(desc(Transaction.date), desc(Transaction.id)).limit(limit).all()

# 3. EDITAR (A ROTA QUE FALTAVA)
@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # A. Busca a transação antiga
    db_tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id).first()
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # B. Estorna o saldo antigo (se afetou conta)
    if db_tx.account_id and db_tx.payment_method != 'credito':
        account = db.query(Account).filter(Account.id == db_tx.account_id).first()
        if account:
            update_account_balance(account, db_tx.amount, db_tx.type, "delete")

    # C. Atualiza os dados do objeto
    update_data = transaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tx, key, value)

    # D. Aplica o novo saldo
    # Nota: Se mudou o valor, aplica o novo valor. Se mudou o tipo, a lógica do helper cuida disso.
    if db_tx.account_id and db_tx.payment_method != 'credito':
        account = db.query(Account).filter(Account.id == db_tx.account_id).first()
        if account:
            update_account_balance(account, db_tx.amount, db_tx.type, "create")

    db.commit()
    db.refresh(db_tx)
    return db_tx

# 4. DELETAR
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id, 
        Transaction.user_id == current_user.id
    ).first()
    
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # Estorna o saldo ao deletar
    if tx.account_id and tx.payment_method != 'credito':
         account = db.query(Account).filter(Account.id == tx.account_id).first()
         if account:
             update_account_balance(account, tx.amount, tx.type, "delete")

    db.delete(tx)
    db.commit()
    return {"message": "Transação excluída"}

def get_or_create_bill(db: Session, card_id: int, month: int, year: int):
    bill = db.query(CreditCardBill).filter(
        CreditCardBill.card_id == card_id,
        CreditCardBill.month == month,
        CreditCardBill.year == year
    ).first()

    if not bill:
        bill = CreditCardBill(card_id=card_id, month=month, year=year, status="aberta")
        db.add(bill)
        db.commit()
        db.refresh(bill)
    
    return bill