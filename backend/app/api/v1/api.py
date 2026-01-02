from fastapi import APIRouter
# Adicione 'goals' na importação
from app.api.v1.endpoints import transactions, credit_cards, dashboard, options, categories, debts, goals

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["Transações"])
api_router.include_router(credit_cards.router, prefix="/credit-cards", tags=["Cartões"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(options.router, prefix="/options", tags=["Opções (Selects)"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categorias"])
api_router.include_router(debts.router, prefix="/debts", tags=["Dividas"])

# ADICIONE ESTA LINHA NO FINAL:
api_router.include_router(goals.router, prefix="/goals", tags=["Metas"])