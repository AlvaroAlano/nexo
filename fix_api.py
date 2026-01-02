import os

def fix_api_structure():
    print("🔧 Iniciando correção da estrutura da API...")

    # Caminho exato onde o api.py DEVE estar
    target_dir = os.path.join("backend", "app", "api", "v1")
    target_file = os.path.join(target_dir, "api.py")

    # Conteúdo do api.py
    api_content = """from fastapi import APIRouter
from app.api.v1.endpoints import transactions, credit_cards, dashboard, options

api_router = APIRouter()

# Registra as rotas individuais
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transações"])
api_router.include_router(credit_cards.router, prefix="/credit-cards", tags=["Cartões"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(options.router, prefix="/options", tags=["Opções (Selects)"])
"""

    # 1. Garante que a pasta existe
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"📂 Pasta criada: {target_dir}")

    # 2. Garante que os __init__.py existem em toda a cadeia
    # Sem isso, o Python não acha os módulos
    init_paths = [
        os.path.join("backend", "app", "__init__.py"),
        os.path.join("backend", "app", "api", "__init__.py"),
        os.path.join("backend", "app", "api", "v1", "__init__.py"),
        os.path.join("backend", "app", "api", "v1", "endpoints", "__init__.py"),
    ]

    for p in init_paths:
        if not os.path.exists(p):
            with open(p, "w") as f:
                pass # Cria arquivo vazio
            print(f"✅ Criado __init__.py faltante em: {p}")

    # 3. Escreve o arquivo api.py
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(api_content)
    
    print(f"✅ Arquivo api.py gerado corretamente em: {target_file}")
    print("\n👉 Tente rodar o uvicorn novamente agora.")

if __name__ == "__main__":
    fix_api_structure()