import sys
import os
from datetime import date, timedelta

# Adiciona diretório ao path para encontrar o módulo 'app'
sys.path.append(os.getcwd())

from app.db.session import SessionLocal, engine, Base
# Importa as classes que definimos no arquivo acima
from app.models.tables import Transaction, CreditCard, Category, Account, CreditCardBill, TransactionType, BillStatus

def populate():
    # 1. Limpa e Recria as tabelas (Garante que a estrutura nova seja aplicada)
    print("🧹 Recriando tabelas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("🏷️ Criando Categorias...")
        cat_salario = Category(name="Salário", type="receita", icon="dollar-sign", color="#10B981")
        cat_alim = Category(name="Alimentação", type="despesa", icon="shopping-cart", color="#F59E0B")
        cat_transp = Category(name="Transporte", type="despesa", icon="truck", color="#3B82F6")
        cat_lazer = Category(name="Lazer", type="despesa", icon="smile", color="#8B5CF6")
        
        db.add_all([cat_salario, cat_alim, cat_transp, cat_lazer])
        db.commit() # Commit para gerar os IDs

        print("🏦 Criando Conta e Cartão...")
        conta_nu = Account(name="NuConta", type="corrente", current_balance=150.00)
        db.add(conta_nu)
        
        cartao_black = CreditCard(name="Nubank Ultravioleta", limit=20000.0, closing_day=25, due_day=5)
        db.add(cartao_black)
        db.commit()

        print("📄 Criando Fatura Atual...")
        hoje = date.today()
        fatura_atual = CreditCardBill(
            card_id=cartao_black.id,
            month=hoje.month,
            year=hoje.year,
            status=BillStatus.OPEN
        )
        db.add(fatura_atual)
        db.commit()

        print("💰 Criando Transações...")
        transacoes = [
            # RECEITA
            Transaction(
                description="Salário Mensal",
                amount=8500.00,
                date=hoje - timedelta(days=5),
                type=TransactionType.INCOME,
                category_id=cat_salario.id,
                account_id=conta_nu.id
            ),
            
            # DESPESA (Débito)
            Transaction(
                description="Almoço Restaurante",
                amount=65.90,
                date=hoje,
                type=TransactionType.EXPENSE,
                category_id=cat_alim.id,
                account_id=conta_nu.id
            ),

            # DESPESA (Crédito - Parcelada)
            Transaction(
                description="iPhone 15 Pro",
                amount=650.00,
                date=hoje,
                type=TransactionType.EXPENSE,
                bill_id=fatura_atual.id, # Conecta na Fatura, não no cartão
                category_id=cat_lazer.id,
                is_installment=True,
                installment_current=2,
                installment_total=10
            ),
        ]

        db.add_all(transacoes)
        db.commit()
        print("✅ Sucesso! Banco populado.")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()