from fastapi import APIRouter
# Importando users e login que estavam faltando
from app.api.api_v1.endpoints import (
    transactions, 
    credit_cards, 
    dashboard, 
    options, 
    categories, 
    debts, 
    goals,
    users,  # <--- IMPORTANTE: Adicionado
    login   # <--- IMPORTANTE: Adicionado (Para o login funcionar)
)

api_router = APIRouter()

# --- ROTAS DE AUTENTICAÇÃO ---
api_router.include_router(login.router, tags=["login"]) # Rota /login/access-token
api_router.include_router(users.router, prefix="/users", tags=["users"]) # Rota /users/open

# --- ROTAS DO SISTEMA ---
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transações"])
api_router.include_router(credit_cards.router, prefix="/credit-cards", tags=["Cartões"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(options.router, prefix="/options", tags=["Opções (Selects)"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categorias"])
api_router.include_router(debts.router, prefix="/debts", tags=["Dividas"])
api_router.include_router(goals.router, prefix="/goals", tags=["Metas"])