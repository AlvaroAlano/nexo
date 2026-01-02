import os
import sys
import shutil

# Configurações de caminhos
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
DB_FILENAME = 'nexo.db'

# Adiciona backend ao path para importar os models
sys.path.append(BACKEND_DIR)

from app.db.session import engine, Base, SessionLocal
from app.models.tables import Category, Account, CreditCard

def reset_and_seed():
    print("🧹 INICIANDO LIMPEZA TOTAL...")

    # 1. Definir caminhos dos arquivos
    db_root_path = os.path.join(ROOT_DIR, DB_FILENAME)
    db_backend_path = os.path.join(BACKEND_DIR, DB_FILENAME)

    # 2. Apagar bancos antigos (Root e Backend)
    # Importante: Tentamos fechar qualquer conexão pendente antes de deletar
    engine.dispose() 
    
    if os.path.exists(db_root_path):
        try:
            os.remove(db_root_path)
            print("🗑️  Banco antigo na raiz deletado.")
        except PermissionError:
            print("⚠️ Não foi possível deletar o da raiz agora (talvez já esteja deletado ou em uso).")

    if os.path.exists(db_backend_path):
        try:
            os.remove(db_backend_path)
            print("🗑️  Banco antigo no backend deletado.")
        except PermissionError:
            print("❌ ERRO CRÍTICO: O servidor 'uvicorn' ainda está rodando? PARE O SERVIDOR e tente de novo.")
            return

    # 3. Criar Tabelas Novas (Cria nexo.db na raiz)
    print("🏗️  Criando nova estrutura de tabelas...")
    Base.metadata.create_all(bind=engine)

    # 4. Popular Dados (Seed)
    print("🌱 Semeando dados iniciais...")
    db = SessionLocal()
    try:
        # Conta
        conta = Account(name="Conta Principal", type="corrente", current_balance=0.0)
        db.add(conta)

        # Categorias
        categories = [
            {"name": "Alimentação", "icon": "coffee", "color": "#F59E0B", "type": "despesa"},
            {"name": "Transporte", "icon": "car", "color": "#3B82F6", "type": "despesa"},
            {"name": "Lazer", "icon": "gamepad", "color": "#EF4444", "type": "despesa"},
            {"name": "Moradia", "icon": "home", "color": "#6366F1", "type": "despesa"},
            {"name": "Contas", "icon": "zap", "color": "#10B981", "type": "despesa"},
            {"name": "Salário", "icon": "dollar-sign", "color": "#10B981", "type": "receita"},
            {"name": "Investimento", "icon": "trending-up", "color": "#8B5CF6", "type": "receita"},
        ]
        for cat in categories:
            db.add(Category(**cat))

        # --- ALTERAÇÃO AQUI: COMENTEI A CRIAÇÃO DOS CARTÕES ---
        # cards = [
        #     {"name": "Nubank", "limit": 10000.0, "closing_day": 20, "due_day": 27, "color": "#820AD1"},
        #     {"name": "XP Visa", "limit": 50000.0, "closing_day": 5, "due_day": 12, "color": "#111111"},
        #     {"name": "Inter", "limit": 8000.0, "closing_day": 15, "due_day": 22, "color": "#FF7A00"},
        # ]
        # for card in cards:
        #     db.add(CreditCard(**card))
    
            print("⚠️ Cartões padrão não foram criados (Lista limpa).")

            db.commit()
            print("✅ Dados inseridos com sucesso.")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        return
    finally:
        db.close()
        # --- O PULO DO GATO ESTÁ AQUI ---
        # Forçamos o SQLAlchemy a soltar o arquivo para podermos movê-lo
        engine.dispose() 

    # 5. MOVER O ARQUIVO PARA O LUGAR CERTO
    if os.path.exists(db_root_path):
        print("🚚 Movendo banco de dados para a pasta 'backend'...")
        try:
            shutil.move(db_root_path, db_backend_path)
            print("✅ BANCO DE DADOS POSICIONADO CORRETAMENTE!")
        except Exception as e:
            print(f"❌ Erro ao mover arquivo: {e}")
            print("   -> Tente mover o arquivo 'nexo.db' manualmente para dentro da pasta 'backend'.")
    else:
        print("❌ Erro estranho: O arquivo nexo.db não foi criado na raiz.")

    print("\n🎉 TUDO PRONTO! Agora seu sistema vai rodar liso.")
    print("👉 Execute: 'cd backend' e depois 'uvicorn app.main:app --reload'")

if __name__ == "__main__":
    reset_and_seed()