<script setup>
import { ref, computed } from 'vue';
import { ChevronDown, ChevronUp } from 'lucide-vue-next';

const props = defineProps({
  card: { type: Object, required: true },
  privacyMode: { type: Boolean, default: false }
});

const isOpen = ref(false);

const formatCurrency = (val) => {
    if (props.privacyMode) return '••••';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
};

// Cálculos
const limit = props.card.limit || 0;
const used = props.card.total_debt || 0;
const available = limit - used;

const invoicePercent = computed(() => {
    if (!limit) return 0;
    return Math.min(((props.card.invoice || 0) / limit) * 100, 100);
});

const debtPercent = computed(() => {
    if (!limit) return 0;
    return Math.min((used / limit) * 100, 100);
});

// Cores dinâmicas baseadas nas variáveis CSS
const debtColorClass = computed(() => {
    const ratio = used / (limit || 1);
    return ratio > 0.9 ? 'bg-[var(--color-danger)]' : 'bg-[var(--color-primary)]';
});
</script>

<template>
  <div 
    class="rounded-xl border border-[var(--border)] bg-[var(--bg-surface)] overflow-hidden transition-all duration-300 group hover:border-[var(--text-muted)]/30 cursor-pointer"
    :class="isOpen ? 'shadow-md border-[var(--color-primary)]/30' : 'shadow-sm'"
  >
      
      <div class="p-3 flex items-center justify-between active:bg-[var(--bg-app)] transition-colors">
          
          <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-sm font-bold text-xs"
                   :style="{ backgroundColor: card.color || '#333' }">
                  {{ card.name.substring(0,1).toUpperCase() }}
              </div>
              <div class="flex flex-col">
                  <span class="text-xs font-bold text-[var(--text-main)]">{{ card.name }}</span>
                  <span v-if="!isOpen" class="text-[10px] text-[var(--text-muted)] font-medium">
                     Disp: <span class="text-[var(--color-success)]">{{ formatCurrency(available) }}</span>
                  </span>
              </div>
          </div>

          <div class="flex items-center gap-3">
              <div v-if="!isOpen" class="text-right">
                  <span class="block text-[10px] font-bold text-[var(--text-muted)] uppercase">Fatura</span>
                  <span class="text-xs font-bold text-[var(--text-main)]">{{ formatCurrency(card.invoice || 0) }}</span>
              </div>
              
              <button 
                  @click.stop="isOpen = !isOpen"
                  class="p-1.5 rounded-full hover:bg-[var(--bg-app)] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors z-10"
              >
                  <component :is="isOpen ? ChevronUp : ChevronDown" :size="18" />
              </button>
          </div>
      </div>

      <div v-if="isOpen" @click.stop class="px-4 pb-4 pt-0 animate-in slide-in-from-top-2 duration-200 cursor-default">
          
          <div class="h-px w-full bg-[var(--border)] mb-4 opacity-50"></div>

          <div class="mb-4">
              <div class="flex justify-between items-end mb-1.5">
                  <div class="flex items-center gap-1.5">
                      <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase">Fatura Atual</span>
                  </div>
                  <span class="text-xs font-bold font-numeric text-[var(--text-main)]">
                      {{ formatCurrency(card.invoice || 0) }}
                  </span>
              </div>
              <div class="w-full bg-[var(--bg-app)] h-2 rounded-full overflow-hidden border border-[var(--border)]">
                  <div class="h-full rounded-full bg-[var(--color-success)]" :style="{ width: Math.max(invoicePercent, 2) + '%' }"></div>
              </div>
          </div>

          <div class="mb-4">
              <div class="flex justify-between items-end mb-1.5">
                  <div class="flex items-center gap-1.5">
                      <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase">Limite Tomado</span>
                  </div>
                  <span class="text-xs font-bold font-numeric text-[var(--text-muted)]">
                      {{ formatCurrency(used) }} <span class="font-normal text-[9px]">de {{ formatCurrency(limit) }}</span>
                  </span>
              </div>
              <div class="w-full bg-[var(--bg-app)] h-2 rounded-full overflow-hidden border border-[var(--border)]">
                  <div class="h-full rounded-full" :class="debtColorClass" :style="{ width: Math.max(debtPercent, 2) + '%' }"></div>
              </div>
          </div>

          <div class="flex justify-between items-center bg-[var(--bg-app)]/50 p-2 rounded-lg border border-[var(--border)]">
              <div class="text-center flex-1 border-r border-[var(--border)]">
                  <span class="text-[9px] text-[var(--text-muted)] uppercase block">Fecha dia</span>
                  <span class="text-xs font-bold text-[var(--text-main)]">{{ card.closing_day }}</span>
              </div>
              <div class="text-center flex-1">
                  <span class="text-[9px] text-[var(--text-muted)] uppercase block">Vence dia</span>
                  <span class="text-xs font-bold text-[var(--color-danger)]">{{ card.due_day }}</span>
              </div>
          </div>

      </div>

  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>