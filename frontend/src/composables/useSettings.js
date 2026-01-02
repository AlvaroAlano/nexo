import { ref, watch } from 'vue';

// Estado global (fora da função para ser único)
const enableDebts = ref(localStorage.getItem('enable_debts') !== 'false');
const enableGoals = ref(localStorage.getItem('enable_goals') !== 'false'); // Novo
const enableInvestments = ref(localStorage.getItem('enable_investments') !== 'false'); // Novo

// Observadores para salvar automaticamente
watch(enableDebts, (val) => localStorage.setItem('enable_debts', val));
watch(enableGoals, (val) => localStorage.setItem('enable_goals', val));
watch(enableInvestments, (val) => localStorage.setItem('enable_investments', val));

export function useSettings() {
    return {
        enableDebts,
        enableGoals,
        enableInvestments
    };
}