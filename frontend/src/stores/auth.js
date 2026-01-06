import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,      // Dados do usuário (nome, id)
    token: null,     // Token de acesso (JWT)
    dashboardData: null // Cache do dashboard (para abrir rápido!)
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    setLoginData(user, token) {
      this.user = user
      this.token = token
    },
    
    setDashboardData(data) {
      this.dashboardData = data
    },

    logout() {
      this.user = null
      this.token = null
      this.dashboardData = null
    }
  },
  
  // A MÁGICA: Isso diz "Salve tudo isso no localStorage do navegador"
  persist: true 
})