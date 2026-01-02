from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
# Importamos Account, User e Category
from app.models.tables import Account, User, Category
from app.api.v1.api import api_router

# Cria as tabelas no banco (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NEXO Financeiro",
    version="2.0.0"
)

# --- CONFIGURAÇÃO CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# --- FUNÇÃO DE INICIALIZAÇÃO (AGORA COM CATEGORIAS) ---
def init_db():
    db = SessionLocal()
    try:
        # 1. Verifica/Cria Usuário Padrão
        user = db.query(User).filter(User.email == "usuario@exemplo.com").first()
        if not user:
            print("👤 Criando usuário padrão...")
            user = User(
                email="usuario@exemplo.com",
                hashed_password="senha_temporaria", 
                full_name="Usuário Nexo"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Usuário criado: ID {user.id}")

        # 2. Verifica/Cria Conta Padrão
        account = db.query(Account).filter(Account.user_id == user.id).first()
        if not account:
            print("⚠️ Nenhuma conta encontrada. Criando 'Carteira' padrão...")
            default_account = Account(
                name="Carteira",
                type="carteira", 
                current_balance=0.0,
                user_id=user.id 
            )
            db.add(default_account)
            db.commit()
            print("✅ Conta 'Carteira' criada!")

        # 3. Cria Categorias Padrão (Se não existirem)
        # Verifica se já tem alguma categoria
        has_categories = db.query(Category).filter(Category.user_id == user.id).first()
        
        if not has_categories:
            print("📂 Criando categorias padrão...")
            default_categories = [
                # Despesas
                {"name": "Alimentação", "type": "expense", "icon": "Utensils", "color": "bg-orange-500"},
                {"name": "Moradia", "type": "expense", "icon": "Home", "color": "bg-blue-500"},
                {"name": "Transporte", "type": "expense", "icon": "Car", "color": "bg-zinc-500"},
                {"name": "Lazer", "type": "expense", "icon": "Coffee", "color": "bg-purple-500"},
                {"name": "Saúde", "type": "expense", "icon": "Heart", "color": "bg-rose-500"},
                {"name": "Compras", "type": "expense", "icon": "ShoppingCart", "color": "bg-pink-500"},
                # Receitas
                {"name": "Salário", "type": "income", "icon": "Briefcase", "color": "bg-emerald-500"},
                {"name": "Investimentos", "type": "income", "icon": "TrendingUp", "color": "bg-amber-500"},
                {"name": "Extra", "type": "income", "icon": "Zap", "color": "bg-teal-500"},
                # Investimento (Categoria de Saída para aporte)
                {"name": "Aporte", "type": "investment", "icon": "PieChart", "color": "bg-indigo-500"},
            ]

            for cat in default_categories:
                new_cat = Category(**cat, user_id=user.id)
                db.add(new_cat)
            
            db.commit()
            print("✅ Categorias criadas com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
    finally:
        db.close()

# Executa a verificação ao iniciar
init_db()

@app.get("/")
def read_root():
    return {"message": "Nexo API is running 🚀"}