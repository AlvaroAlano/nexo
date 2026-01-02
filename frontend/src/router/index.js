import { createRouter, createWebHistory } from 'vue-router'
import Welcome from '../views/Welcome.vue'
import Dashboard from '../views/Dashboard.vue'

// Importando as Views (certifique-se de ter criado os arquivos)
import GoalsView from '../views/GoalsView.vue'
import InvestmentsView from '../views/InvestmentsView.vue'

const routes = [
    {
        path: '/',
        name: 'Welcome',
        component: Welcome
    },
    {
        path: '/login',
        redirect: '/'
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/SettingsView.vue')
    },

    // --- ROTAS AUXILIARES ---
    {
        path: '/perfil',
        name: 'Profile',
        component: () => import('../views/ProfileView.vue')
    },
    {
        path: '/categorias',
        name: 'Categories',
        component: () => import('../views/CategoriesView.vue')
    },
    {
        path: '/cartoes',
        name: 'Cards',
        component: () => import('../views/CardsView.vue')
    },
    {
        path: '/acertos',
        name: 'Debts',
        component: () => import('../views/AcertosView.vue')
    },
    {
        path: '/metas',
        name: 'Metas',
        component: () => import('../views/GoalsView.vue')
    },
    {
        path: '/transactions',
        name: 'Transactions',
        component: () => import('../views/TransactionsView.vue')
    },

    // --- NOVAS ROTAS (Metas & Investimentos) ---
    {
        path: '/goals',
        name: 'Goals',
        component: GoalsView
    },
    {
        path: '/investments',
        name: 'Investments',
        component: InvestmentsView
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router