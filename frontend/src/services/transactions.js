import api from './api';

export default {
  // Busca transações com filtros
  getAll(params) {
    return api.get('/transactions/', { params });
  },

  // Criação
  create(data) {
    return api.post('/transactions/', data);
  },

  // Atualização
  update(id, data) {
    return api.put(`/transactions/${id}`, data);
  },

  // Remoção
  delete(id) {
    return api.delete(`/transactions/${id}`);
  },

  // Busca opções auxiliares (Categorias e Cartões) para os selects
  getOptions() {
    return Promise.all([
      // Seus endpoints de opções ou listagem direta
      api.get('/categories/').catch(() => ({ data: [] })), 
      api.get('/credit-cards/').catch(() => ({ data: [] }))
    ]);
  }
};