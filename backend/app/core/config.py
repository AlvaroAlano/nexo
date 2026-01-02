from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexo 2.0"
    
    # --- A CORREÇÃO ESTÁ AQUI ---
    # Adicionamos um valor padrão (= "...") para ele não crashar se não achar o .env
    SECRET_KEY: str = "chave_secreta_temporaria_apenas_para_dev" 
    
    DATABASE_URL: str = "sqlite:///./nexo.db"

    # Configuração para ler o arquivo .env se ele existir
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()