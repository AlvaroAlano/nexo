import axios from 'axios';
import { useAuthStore } from '../stores/auth'; // <--- Importamos a Store que criamos

const api = axios.create({
  // Atualizei o fallback para o seu Render oficial. 
  // Assim, se não tiver variável de ambiente, ele usa a produção direto (funciona na Vercel e no Local).
  baseURL: import.meta.env.VITE_API_URL || 'https://nexo-api-2pdl.onrender.com/api/v1',
});

// --- O SEGREDO DO LOGIN ---
// Antes de qualquer requisição sair do celular...
api.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  
  // Se o usuário tiver um token salvo (graças à persistência do Pinia)...
  if (authStore.token) {
    // ...nós anexamos o token no cabeçalho da requisição.
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  
  return config;
});

export default api;