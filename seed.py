import sys
import os

# Adiciona o diretório backend ao caminho do Python para encontrar o 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import SessionLocal, engine, Base
from app.models.tables import Category, Account, CreditCard

# Garante que as tabelas existem
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    print("🌱 Iniciando a plantação de dados (Seed)...")

    # 1. Criar Conta Padrão (Se não existir)
    if not db.query(Account).first():
        conta = Account(name="Conta Principal", type="corrente", current_balance=0.0)
        db.add(conta)
        print("✅ Conta Principal criada.")
    else:
        print("ℹ️ Conta já existe.")

    # 2. Criar Categorias Padrão
    categories = [
        {"name": "Alimentação", "icon": "coffee", "color": "#F59E0B", "type": "despesa"},
        {"name": "Transporte", "icon": "car", "color": "#3B82F6", "type": "despesa"},
        {"name": "Lazer", "icon": "gamepad", "color": "#EF4444", "type": "despesa"},
        {"name": "Moradia", "icon": "home", "color": "#6366F1", "type": "despesa"},
        {"name": "Contas", "icon": "zap", "color": "#10B981", "type": "despesa"},
        {"name": "Salário", "icon": "dollar-sign", "color": "#10B981", "type": "receita"},
    ]
    
    for cat in categories:
        if not db.query(Category).filter_by(name=cat["name"]).first():
            db.add(Category(**cat))
            print(f"✅ Categoria {cat['name']} criada.")

    # 3. Criar Cartões Padrão
    cards = [
        {"name": "Nubank", "limit": 10000.0, "closing_day": 20, "due_day": 27},
        {"name": "XP Visa", "limit": 50000.0, "closing_day": 5, "due_day": 12},
        {"name": "Inter", "limit": 8000.0, "closing_day": 15, "due_day": 22},
    ]

    for card in cards:
        if not db.query(CreditCard).filter_by(name=card["name"]).first():
            db.add(CreditCard(**card))
            print(f"✅ Cartão {card['name']} criado.")

    db.commit()
    print("\n🚀 Sucesso! O banco de dados foi populado.")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        db.close()