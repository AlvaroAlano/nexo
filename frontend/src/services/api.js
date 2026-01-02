import axios from 'axios';

// "Truque" de mestre:
// Se existir uma variável de ambiente (na Vercel), usa ela.
// Se não existir (no seu PC), usa o localhost padrão.
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
});

export default api;