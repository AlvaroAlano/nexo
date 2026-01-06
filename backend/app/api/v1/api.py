from fastapi import APIRouter
# CORREÇÃO: Usando 'v1' em vez de 'api_v1'
from app.api.v1.endpoints import (
    transactions, 
    credit_cards, 
    dashboard, 
    options, 
    categories, 
    debts, 
    goals,
    users,
    login
)

api_router = APIRouter()

# --- ROTAS DE AUTENTICAÇÃO ---
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# --- ROTAS DO SISTEMA ---
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transações"])
api_router.include_router(credit_cards.router, prefix="/credit-cards", tags=["Cartões"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(options.router, prefix="/options", tags=["Opções (Selects)"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categorias"])
api_router.include_router(debts.router, prefix="/debts", tags=["Dividas"])
api_router.include_router(goals.router, prefix="/goals", tags=["Metas"])