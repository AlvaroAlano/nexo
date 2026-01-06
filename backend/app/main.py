from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, SessionLocal
# IMPORTANTE: Importar a Base correta onde os modelos estão registrados
from app.db.base_class import Base 

# Importação limpa via __init__.py que criamos no Passo 3
from app.models import Account, User, Category, TransactionType

from app.api.v1.api import api_router

# Cria as tabelas no banco usando a Base correta
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CONFIGURAÇÃO CORS ---
# Em desenvolvimento, aceitamos tudo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# --- INICIALIZAÇÃO DO BANCO (SEED) ---
def init_db():
    db = SessionLocal()
    try:
        # 1. Verifica/Cria Usuário Padrão
        user = db.query(User).filter(User.email == "usuario@exemplo.com").first()
        if not user:
            print("👤 Criando usuário padrão...")
            # Importante: A senha aqui não está criptografada com hash correto na sua versão original.
            # Para testes rápidos ok, mas o ideal seria usar get_password_hash do security.py
            from app.core.security import get_password_hash
            
            user = User(
                email="usuario@exemplo.com",
                hashed_password=get_password_hash("123456"), # Senha: 123456
                full_name="Usuário Nexo"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Usuário criado: ID {user.id}")

        # 2. Verifica/Cria Conta Padrão
        account = db.query(Account).filter(Account.user_id == user.id).first()
        if not account:
            print("💰 Criando conta 'Carteira'...")
            default_account = Account(
                name="Carteira",
                type="carteira", 
                current_balance=0.0,
                user_id=user.id 
            )
            db.add(default_account)
            db.commit()

        # 3. Verifica/Cria Categorias Padrão
        has_categories = db.query(Category).filter(Category.user_id == user.id).first()
        if not has_categories:
            print("📂 Criando categorias padrão...")
            default_categories = [
                {"name": "Alimentação", "type": TransactionType.EXPENSE.value, "icon": "Utensils", "color": "bg-orange-500"},
                {"name": "Salário", "type": TransactionType.INCOME.value, "icon": "Briefcase", "color": "bg-emerald-500"},
                # ... adicione as outras se quiser ...
            ]
            for cat in default_categories:
                new_cat = Category(**cat, user_id=user.id)
                db.add(new_cat)
            db.commit()
            print("✅ Dados iniciais carregados!")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
    finally:
        db.close()

# Executa ao iniciar
init_db()

@app.get("/")
def read_root():
    return {"message": "Nexo API is running 🚀"}