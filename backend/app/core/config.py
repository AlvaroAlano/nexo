from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexo Finance"
    
    # --- VARIÁVEIS CRÍTICAS DE SEGURANÇA E API ---
    API_V1_STR: str = "/api/v1"
    # IMPORTANTE: Em produção real, isso viria do .env. 
    # Deixamos fixo aqui APENAS para garantir que o deploy funcione agora.
    SECRET_KEY: str = "sua_chave_secreta_super_segura_e_aleatoria_123"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    USERS_OPEN_REGISTRATION: bool = True
    
    # --- DATABASE ---
    # O Render injeta a DATABASE_URL automaticamente, mas deixamos um fallback local
    DATABASE_URL: str = "sqlite:///./nexo.db"

    # --- CORS (FRONTEND) ---
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignora variáveis extras do Render para não dar erro
    )

settings = Settings()