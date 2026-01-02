from datetime import date, timedelta
from dateutil.relativedelta import relativedelta # Precisa instalar: pip install python-dateutil

class CreditCardEngine:
    
    @staticmethod
    def calculate_bill_reference(transaction_date: date, closing_day: int) -> dict:
        """
        Define a qual Mês/Ano de referência uma compra pertence,
        baseado no dia de fechamento do cartão.
        """
        
        # Se a compra foi feita DEPOIS do fechamento, ela vai para o mês seguinte
        # Ex: Fechamento dia 20. Compra dia 21/05 -> Fatura de Junho (06)
        if transaction_date.day > closing_day:
            reference_date = transaction_date + relativedelta(months=1)
        else:
            # Ex: Fechamento dia 20. Compra dia 15/05 -> Fatura de Maio (05)
            reference_date = transaction_date

        return {
            "month": reference_date.month,
            "year": reference_date.year
        }

    @staticmethod
    def generate_installments(transaction_date: date, amount: float, total_installments: int, closing_day: int):
        """
        Gera uma lista de parcelas projetadas para o futuro.
        """
        installment_value = round(amount / total_installments, 2)
        installments = []

        # Calcula a referência da 1ª parcela
        first_bill = CreditCardEngine.calculate_bill_reference(transaction_date, closing_day)
        start_date = date(first_bill['year'], first_bill['month'], 1)

        for i in range(total_installments):
            # Adiciona meses para cada parcela subsequente
            current_bill_date = start_date + relativedelta(months=i)
            
            installments.append({
                "number": i + 1,
                "total": total_installments,
                "amount": installment_value,
                "bill_month": current_bill_date.month,
                "bill_year": current_bill_date.year,
                # Isso aqui é ouro: saberemos exatamente em qual fatura cairá
            })
            
        return installments