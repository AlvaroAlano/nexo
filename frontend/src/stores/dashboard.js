import { defineStore } from 'pinia'
import api from '../services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null,   // Saldo, Receitas, Despesas
    upcoming: [],    // Contas a pagar
    chart: null,     // Dados do gráfico
    isLoading: false
  }),
  
  actions: {
    async fetchAllData() {
      this.isLoading = true
      try {
        // Pega data atual para filtrar o dashboard
        const today = new Date()
        const month = today.getMonth() + 1
        const year = today.getFullYear()
        
        // Tenta buscar os dados.
        // NOTA: Se você ainda não criou a rota '/dashboard/full-load' no backend, 
        // ele vai dar erro aqui, mas o try/catch garante que o app entra mesmo assim.
        const { data } = await api.get(`/dashboard/full-load?month=${month}&year=${year}`)
        
        this.summary = data.summary
        this.upcoming = data.upcoming
        this.chart = data.chart
        
      } catch (error) {
        console.warn("Não foi possível pré-carregar o dashboard (talvez a rota full-load não exista ainda). Entrando mesmo assim.", error)
        // Não jogamos o erro pra cima (throw) para não travar o login do usuário
      } finally {
        this.isLoading = false
      }
    }
  },
  
  persist: true // Salva no celular
})