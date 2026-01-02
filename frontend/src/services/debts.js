import api from './api';

export default {
  // Resumo com tratamento de erro
  async getSummary() {
    try {
      return await api.get('/debts/summary');
    } catch (error) {
      console.error("Erro ao buscar resumo de dívidas:", error);
      throw error;
    }
  },

  // Histórico
  async getHistory(name) {
    try {
      return await api.get(`/debts/${encodeURIComponent(name)}/history`);
    } catch (error) {
      console.error("Erro ao buscar histórico:", error);
      throw error;
    }
  },

  // Registrar pagamento (Payload completo)
  async settleDebt(data) {
    // data deve conter: { debtor_name, amount, payment_method, account_id, date }
    try {
      return await api.post('/debts/payment', data);
    } catch (error) {
      console.error("Erro ao registrar pagamento:", error);
      throw error;
    }
  },

  async deleteDebt(name) {
    try {
      return await api.delete(`/debts/${encodeURIComponent(name)}`);
    } catch (error) {
      console.error("Erro ao apagar dívida:", error);
      throw error;
    }
  },

  getWhatsappLink(debtorName, totalAmount) {
    const amountStr = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalAmount);
    const text = `Opa ${debtorName}, tudo bem? 😊\n\nSó passando pra lembrar daquele valor de *${amountStr}* referente às nossas contas.\n\nQuando der, me dá um toque! Valeu!`;
    return `https://wa.me/?text=${encodeURIComponent(text)}`;
  }
};