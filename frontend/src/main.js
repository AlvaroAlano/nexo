import { createApp } from 'vue'
import { createPinia } from 'pinia' // <--- IMPORTANTE
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate' // <--- IMPORTANTE
import './style.css'
import App from './App.vue'
import router from './router'
import VueApexCharts from "vue3-apexcharts";

const app = createApp(App)
const pinia = createPinia() // Cria a instância do Pinia

// Ativa o plugin de "memória" (persistência) no Pinia
pinia.use(piniaPluginPersistedstate) 

app.use(pinia) // <--- Conecta o Pinia no App
app.use(router)
app.use(VueApexCharts)

app.mount('#app')