import api from './api';

export default {
    // Listar todas
    getAll: () => api.get('/goals/'),
    
    // Criar
    create: (data) => api.post('/goals/', data),
    
    // Atualizar (Serve para Editar e Depositar)
    update: (id, data) => api.put(`/goals/${id}`, data),
    
    // Deletar
    delete: (id) => api.delete(`/goals/${id}`),
    
    // Reordenar (Drag & Drop)
    reorder: (idList) => api.post('/goals/reorder', idList),

    // NOVO MÉTODO ESPECÍFICO PARA DEPÓSITO
    deposit: (id, amount) => api.post(`/goals/${id}/deposit`, { amount }),

    withdraw: (id, amount) => api.post(`/goals/${id}/withdraw`, { amount })
};