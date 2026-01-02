# migrate_debtors.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import SQLALCHEMY_DATABASE_URL
from app.models.tables import Transaction, Debtor, Base

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def migrate():
    print("🚀 Iniciando migração de Devedores (Preservando Acentos)...")
    Base.metadata.create_all(bind=engine)

    transactions = db.query(Transaction).filter(
        Transaction.debtor_name.isnot(None),
        Transaction.debtor_name != "",
        Transaction.debtor_id.is_(None)
    ).all()

    if not transactions:
        print("✅ Nada para migrar.")
        return

    print(f"📦 Processando {len(transactions)} transações...")
    
    # Cache: { "chave_normalizada-user_id": objeto_devedor }
    debtor_map = {} 

    for tx in transactions:
        if not tx.user_id: continue

        # Normalização Suave: Tira espaços, põe minúsculo, MAS MANTÉM ACENTOS
        # " João " -> "joão"
        # "Mãe" -> "mãe" (diferente de "mae")
        raw_name = tx.debtor_name.strip()
        normalized_key = f"{raw_name.lower()}-{tx.user_id}"
        
        if normalized_key not in debtor_map:
            # Tenta buscar no banco pelo nome exato ou normalizado
            # Aqui buscamos pelo nome "bonito" (raw_name) para garantir
            existing = db.query(Debtor).filter(
                Debtor.name == raw_name, 
                Debtor.user_id == tx.user_id
            ).first()
            
            if existing:
                debtor_map[normalized_key] = existing
            else:
                new_debtor = Debtor(name=raw_name, user_id=tx.user_id)
                db.add(new_debtor)
                db.flush()
                debtor_map[normalized_key] = new_debtor
                print(f"   👤 Devedor criado: {raw_name}")

        # Vincula
        debtor = debtor_map[normalized_key]
        tx.debtor_id = debtor.id

    db.commit()
    print("✅ Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate()