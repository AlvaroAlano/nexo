import os
from pathlib import Path

# Estrutura do Projeto Nexo 2.0
structure = [
    "backend/app/api/v1/endpoints",
    "backend/app/api/dependencies",
    "backend/app/core",
    "backend/app/db",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "backend/alembic/versions",
]

files = {
    "backend/requirements.txt": """fastapi
uvicorn
sqlalchemy
alembic
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
httpx
""",
    "backend/app/main.py": "",
    "backend/app/core/config.py": "",
    "backend/app/db/session.py": "",
    "backend/app/db/base.py": "",
    "backend/.env": "PROJECT_NAME=Nexo 2.0\nDATABASE_URL=sqlite:///./nexo.db\nSECRET_KEY=troque_isso_por_um_hash_seguro_em_producao",
}

def create_structure():
    print("🚀 Iniciando setup do Nexo 2.0...")
    
    # Criar pastas
    for folder in structure:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        # Criar __init__.py em cada pasta python
        if "alembic" not in str(path):
            (path / "__init__.py").touch()
    
    # Criar arquivos base
    for file_path, content in files.items():
        path = Path(file_path)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"✅ Criado: {file_path}")
    
    print("\n🏁 Estrutura criada com sucesso!")
    print("👉 Próximo passo: Abra o terminal na pasta 'backend' e instale as dependências.")

if __name__ == "__main__":
    create_structure()