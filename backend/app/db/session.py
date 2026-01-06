from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Configuração para SQLite (evita erro de thread)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Configuração de Pool de Conexão (Postgres vs SQLite)
pool_config = {}
if "sqlite" not in settings.DATABASE_URL:
    # No Postgres do Render/Supabase, usamos NullPool para evitar conexões presas
    pool_config["poolclass"] = NullPool

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True, # Verifica se o banco está vivo antes de conectar
    **pool_config
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# REMOVIDO: class Base(DeclarativeBase)
# MOTIVO: A Base deve vir de app.db.base_class para ser única no projeto.