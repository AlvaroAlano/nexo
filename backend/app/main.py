from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
# Importamos Account, User, Category e o Enum TransactionType
from app.models.tables import Account, User, Category, TransactionType
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
    "https://nexo-swart.vercel.app",  # <--- ADICIONE ESTA LINHA (Seu link da Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <--- Garanta que está usando a lista 'origins' aqui
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAÇÃO CORS (CORRIGIDA) ---
# Em desenvolvimento, liberamos TUDO ["*"] para evitar dor de cabeça com portas e IPs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <--- MUDANÇA CRÍTICA: Aceita qualquer origem (Frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Aceita GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],  # Aceita todos os headers
)

app.include_router(api_router, prefix="/api/v1")

# --- FUNÇÃO DE INICIALIZAÇÃO ---
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

        # 3. Verifica/Cria Categorias Padrão
        has_categories = db.query(Category).filter(Category.user_id == user.id).first()
        
        if not has_categories:
            print("📂 Criando categorias padrão...")
            # OBS: Atualizei os 'types' para bater com o Enum do banco (income, expense, transf)
            # "investment" não existe no Enum, então usamos "expense" (saída) ou "transf"
            default_categories = [
                # Despesas
                {"name": "Alimentação", "type": TransactionType.EXPENSE.value, "icon": "Utensils", "color": "bg-orange-500"},
                {"name": "Moradia", "type": TransactionType.EXPENSE.value, "icon": "Home", "color": "bg-blue-500"},
                {"name": "Transporte", "type": TransactionType.EXPENSE.value, "icon": "Car", "color": "bg-zinc-500"},
                {"name": "Lazer", "type": TransactionType.EXPENSE.value, "icon": "Coffee", "color": "bg-purple-500"},
                {"name": "Saúde", "type": TransactionType.EXPENSE.value, "icon": "Heart", "color": "bg-rose-500"},
                {"name": "Compras", "type": TransactionType.EXPENSE.value, "icon": "ShoppingCart", "color": "bg-pink-500"},
                # Receitas
                {"name": "Salário", "type": TransactionType.INCOME.value, "icon": "Briefcase", "color": "bg-emerald-500"},
                {"name": "Investimentos", "type": TransactionType.INCOME.value, "icon": "TrendingUp", "color": "bg-amber-500"},
                {"name": "Extra", "type": TransactionType.INCOME.value, "icon": "Zap", "color": "bg-teal-500"},
                # Investimento (Saída) - Ajustado para EXPENSE pois INVESTMENT não existe no Enum
                {"name": "Aporte", "type": TransactionType.EXPENSE.value, "icon": "PieChart", "color": "bg-indigo-500"},
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