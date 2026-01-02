from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Configuração específica para SQLite (thread check)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Nova forma de declarar Base no SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass

# --- A PEÇA QUE FALTAVA ---
def get_db():
    """
    Gera uma sessão de banco de dados para cada requisição 
    e garante que ela seja fechada ao final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()