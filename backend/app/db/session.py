from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool  # <--- IMPORTANTE: Importar isso
from app.core.config import settings

# Configuração específica para SQLite (thread check)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Se for Postgres (Supabase), usamos NullPool para não segurar conexões e travar o banco
# Se for SQLite (local), usamos o padrão.
pool_config = {}
if "sqlite" not in settings.DATABASE_URL:
    pool_config["poolclass"] = NullPool

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    **pool_config # <--- Aplica a configuração de pool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

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