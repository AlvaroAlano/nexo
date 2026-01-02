from datetime import date
from app.services.credit_card_service import CreditCardEngine

def testar_cartao():
    print("--- 🧪 TESTE DA ENGINE DE CARTÃO ---")
    
    # CENÁRIO: Cartão Nubank (Fecha dia 20)
    fechamento = 20
    
    # 1. Compra antes do fechamento (Dia 15/05) -> Esperado: Fatura Maio
    compra1 = date(2025, 5, 15)
    ref1 = CreditCardEngine.calculate_bill_reference(compra1, fechamento)
    print(f"🛒 Compra {compra1} (Fecha dia {fechamento}) -> Fatura: {ref1['month']}/{ref1['year']}")
    
    # 2. Compra DEPOIS do fechamento (Dia 25/05) -> Esperado: Fatura Junho
    compra2 = date(2025, 5, 25)
    ref2 = CreditCardEngine.calculate_bill_reference(compra2, fechamento)
    print(f"🛒 Compra {compra2} (Fecha dia {fechamento}) -> Fatura: {ref2['month']}/{ref2['year']}")
    
    # 3. Parcelamento (Compra de R$ 1000 em 5x no dia 25/05)
    # Como foi dia 25 (pós-fechamento), a 1ª parcela já deve cair em JUNHO
    print("\n--- 📦 SIMULAÇÃO DE PARCELAMENTO ---")
    parcelas = CreditCardEngine.generate_installments(compra2, 1000.00, 5, fechamento)
    
    for p in parcelas:
        print(f"Parcela {p['number']}/{p['total']} de R$ {p['amount']} -> Cai na fatura de: {p['bill_month']}/{p['bill_year']}")

if __name__ == "__main__":
    testar_cartao()