<script setup>
import { computed } from 'vue';
import { Wallet, TrendingUp, TrendingDown, CreditCard } from 'lucide-vue-next';

const props = defineProps({
  summary: { type: Object, required: true },
  creditCardsSummary: { type: Object, default: () => ({ total_invoice: 0, total_limit: 1, total_debt: 0 }) },
  formatCurrency: { type: Function, required: true }
});

// Calcula porcentagem de uso do cartão para a barra visual
const cardUsagePercent = computed(() => {
    if (!props.creditCardsSummary.total_limit) return 0;
    return Math.min((props.creditCardsSummary.total_debt / props.creditCardsSummary.total_limit) * 100, 100);
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

    <div class="rounded-2xl p-5 flex flex-col justify-between h-28 overflow-hidden relative shadow-lg transition-transform hover:-translate-y-1"
         style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);">
         
         <div class="absolute inset-0 bg-white/10 pointer-events-none opacity-50 blur-xl"></div>

         <div class="flex justify-between items-start z-10">
            <span class="text-[10px] font-bold text-white/90 uppercase tracking-wider">Saldo em Contas</span>
            <Wallet :size="18" class="text-white/80" />
         </div>
         
         <h3 class="text-2xl font-bold font-numeric tracking-tight text-white z-10">
            {{ formatCurrency(summary.balance) }}
         </h3>
    </div>

    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 flex flex-col justify-between h-28 border border-[var(--border)] shadow-sm transition-transform hover:-translate-y-1 hover:border-[var(--color-success)]/30">
        <div class="flex justify-between items-start relative z-10">
            <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Receitas</span>
            <div class="w-7 h-7 rounded-full bg-[var(--color-success)]/10 flex items-center justify-center text-[var(--color-success)]">
                <TrendingUp :size="14" />
            </div>
        </div>
        <h3 class="text-2xl font-bold font-numeric text-[var(--color-success)] tracking-tight relative z-10">
            {{ formatCurrency(summary.month_income) }}
        </h3>
    </div>

    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 flex flex-col justify-between h-28 border border-[var(--border)] shadow-sm transition-transform hover:-translate-y-1 hover:border-[var(--color-danger)]/30">
        <div class="flex justify-between items-start relative z-10">
            <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Despesas</span>
            <div class="w-7 h-7 rounded-full bg-[var(--color-danger)]/10 flex items-center justify-center text-[var(--color-danger)]">
                <TrendingDown :size="14" />
            </div>
        </div>
        <h3 class="text-2xl font-bold font-numeric text-[var(--color-danger)] tracking-tight relative z-10">
            {{ formatCurrency(summary.month_expense) }}
        </h3>
    </div>

    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 flex flex-col justify-between h-28 border border-[var(--border)] shadow-sm transition-transform hover:-translate-y-1 hover:border-[var(--color-primary)]/30">
        <div class="flex justify-between items-start relative z-10 mb-1">
            <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Faturas Cartões</span>
            <CreditCard :size="18" class="text-[var(--text-muted)]" />
        </div>
        <div class="relative z-10">
            <h3 class="text-2xl font-bold font-numeric tracking-tight text-[var(--text-main)]">
                {{ formatCurrency(creditCardsSummary.total_invoice) }}
            </h3>
            
            <div class="flex items-center gap-2 mt-1.5">
                <div class="w-full bg-[var(--bg-app)] h-1.5 rounded-full overflow-hidden border border-[var(--border)]">
                    <div class="h-full rounded-full transition-all duration-1000 ease-out" 
                         :class="cardUsagePercent > 90 ? 'bg-[var(--color-danger)]' : 'bg-[var(--color-primary)]'"
                         :style="{ width: cardUsagePercent + '%' }">
                    </div>
                </div>
                <span class="text-[9px] font-bold text-[var(--text-muted)] whitespace-nowrap">
                    {{ Math.round(cardUsagePercent) }}% do Limite
                </span>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>