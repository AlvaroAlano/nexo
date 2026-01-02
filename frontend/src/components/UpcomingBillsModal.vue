<script setup>
import { X, Calendar, AlertCircle, ArrowRight, CalendarCheck, CreditCard } from 'lucide-vue-next';

const props = defineProps({
  isOpen: Boolean,
  bills: Array
});

const emit = defineEmits(['close', 'select']);

const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

// Lógica de Cores Semântica
const getDaysText = (dateString) => {
  const today = new Date(); today.setHours(0,0,0,0);
  const target = new Date(dateString);
  const targetLocal = new Date(target.getUTCFullYear(), target.getUTCMonth(), target.getUTCDate());
  const diffTime = targetLocal - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return { text: 'Venceu', color: 'text-[var(--color-danger)] font-bold' }; 
  if (diffDays === 0) return { text: 'Vence Hoje', color: 'text-[var(--color-warning)] font-bold' }; 
  if (diffDays === 1) return { text: 'Amanhã', color: 'text-[var(--color-warning)] font-bold' }; 
  return { text: `Em ${diffDays} dias`, color: 'text-[var(--text-muted)]' };
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    const [y, m, d] = dateString.split('-');
    return `${d}/${m}`;
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div @click="$emit('close')" class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"></div>

    <div class="relative w-full max-w-[360px] bg-[var(--bg-surface)] rounded-2xl shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-200 border border-[var(--border)] max-h-[80vh] overflow-hidden">
      
      <div class="px-4 py-3 border-b border-[var(--border)] flex justify-between items-center bg-[var(--bg-app)]">
        <div class="flex items-center gap-2 text-[var(--text-main)]">
            <CalendarCheck :size="18" class="text-[var(--color-primary)]" />
            <h2 class="text-xs font-bold uppercase tracking-wider">Próximos 7 Dias</h2>
        </div>
        <button @click="$emit('close')" class="text-[var(--text-muted)] hover:text-[var(--text-main)]"><X :size="18" /></button>
      </div>

      <div class="p-3 overflow-y-auto custom-scroll space-y-2">
          <div v-if="bills.length === 0" class="flex flex-col items-center justify-center py-6 text-[var(--text-muted)] opacity-70">
              <AlertCircle :size="24" class="mb-2" />
              <p class="text-xs">Nenhuma conta prevista.</p>
          </div>

          <div 
            v-for="bill in bills" 
            :key="bill.id" 
            @click="$emit('select', bill)"
            class="flex items-center justify-between p-2.5 rounded-xl border border-[var(--border)] bg-[var(--bg-app)] active:scale-[0.98] transition-transform cursor-pointer hover:bg-[var(--bg-hover)] group"
          >
              <div class="flex items-center gap-3 overflow-hidden">
                  
                  <div class="flex flex-col items-center justify-center w-9 h-9 rounded-lg border border-[var(--border)] shrink-0 transition-colors"
                       :class="bill.type === 'card' 
                           ? 'bg-[var(--color-primary)]/10 text-[var(--color-primary)] border-[var(--color-primary)]/20' 
                           : 'bg-[var(--bg-surface)] text-[var(--text-muted)]'">
                      
                      <CreditCard v-if="bill.type === 'card'" :size="16" />
                      <template v-else>
                          <span class="text-[8px] font-bold uppercase leading-none">{{ formatDate(bill.date).split('/')[1] }}</span>
                          <span class="text-sm font-bold leading-none mt-0.5">{{ formatDate(bill.date).split('/')[0] }}</span>
                      </template>
                  </div>

                  <div class="flex flex-col overflow-hidden">
                      <span class="text-sm font-bold text-[var(--text-main)] truncate group-hover:text-[var(--color-primary)] transition-colors">
                          {{ bill.description }}
                      </span>
                      <div class="flex items-center gap-2">
                          <span class="text-[10px] font-medium" :class="getDaysText(bill.date).color">
                              {{ getDaysText(bill.date).text }}
                          </span>
                          <span v-if="bill.type === 'card'" class="text-[9px] bg-[var(--color-primary)]/10 text-[var(--color-primary)] px-1 rounded border border-[var(--color-primary)]/10">
                              FATURA
                          </span>
                      </div>
                  </div>
              </div>
              
              <div class="flex items-center gap-1">
                  <span class="text-sm font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(bill.amount) }}</span>
                  <ArrowRight :size="14" class="text-[var(--text-muted)] opacity-50" />
              </div>
          </div>
      </div>

      <div class="p-3 border-t border-[var(--border)] bg-[var(--bg-surface)]">
          <button @click="$emit('close')" class="w-full py-3 rounded-xl bg-[var(--bg-app)] text-[var(--text-main)] font-bold text-xs hover:brightness-95 transition-all border border-[var(--border)] uppercase tracking-wide hover:bg-[var(--bg-hover)]">
              Fechar
          </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>