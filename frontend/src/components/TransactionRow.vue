<script setup>
import { computed } from 'vue';
import { ArrowUp, ArrowDown, Repeat, CreditCard, Users, Edit2, Trash2 } from 'lucide-vue-next';

const props = defineProps({
  transaction: { type: Object, required: true },
  showActions: { type: Boolean, default: false },
  privacyMode: { type: Boolean, default: false }
});

const emit = defineEmits(['click', 'edit', 'delete']);

const formatCurrency = (val) => {
    if (props.privacyMode) return '••••';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}`;
};
</script>

<template>
  <div 
    @click="$emit('click', transaction)"
    class="group flex items-center justify-between p-3 transition-all cursor-pointer border-b border-[var(--border)]/30 last:border-0 hover:bg-[var(--bg-hover)] md:rounded-xl md:border md:border-transparent md:hover:border-[var(--border)] relative"
  >
    <div class="flex items-center gap-3 md:gap-4 overflow-hidden">
        <div 
            class="w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm border border-[var(--border)]/50 flex-shrink-0 transition-colors"
            :class="transaction.type === 'receita' 
                ? 'bg-[var(--color-success)]/10 text-[var(--color-success)]' 
                : 'bg-[var(--bg-app)] text-[var(--text-muted)]'"
        >
            <ArrowUp v-if="transaction.type === 'receita'" :size="16" class="md:w-5 md:h-5" />
            <ArrowDown v-else :size="16" class="md:w-5 md:h-5" />
        </div>

        <div class="flex flex-col overflow-hidden">
            <span class="text-xs md:text-sm font-bold text-[var(--text-main)] truncate block">
                {{ transaction.description }}
            </span>
            
            <div class="flex items-center gap-2 mt-0.5 flex-wrap">
                <span class="text-[9px] md:text-[11px] text-[var(--text-muted)] whitespace-nowrap">
                    {{ formatDate(transaction.date) }} • 
                    {{ transaction.payment_method === 'credito' ? 'Fatura' : (transaction.status === 'pendente' ? 'Agendado' : 'Pago') }}
                </span>
                
                <div v-if="transaction.is_recurring" class="flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[8px] md:text-[9px] font-bold uppercase tracking-wide text-[var(--color-primary)] bg-[var(--color-primary)]/10 border-[var(--color-primary)]/20">
                    <Repeat :size="10" /> <span class="hidden md:inline">Fixa</span>
                </div>
                
                <div v-if="transaction.installment_total > 1" class="flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[8px] md:text-[9px] font-bold uppercase tracking-wide text-[var(--color-primary)] bg-[var(--color-primary)]/10 border-[var(--color-primary)]/20">                  
                    <CreditCard :size="10" /> {{ transaction.installment_current }}/{{ transaction.installment_total }}
                </div>
                
                <div v-if="transaction.debtor_name" class="flex items-center gap-1 px-1.5 py-0.5 rounded-full border text-[8px] md:text-[9px] font-bold uppercase tracking-wide text-[var(--color-warning)] bg-[var(--color-warning)]/10 border-[var(--color-warning)]/20">
                    <Users :size="10" /> {{ transaction.debtor_name }}
                </div>
            </div>
        </div>
    </div>

    <div class="flex items-center gap-4 ml-2">
        <div v-if="showActions" class="hidden md:flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click.stop="$emit('edit', transaction)" class="p-1.5 text-[var(--text-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary)]/10 rounded-md transition-colors"><Edit2 :size="16" /></button>
            <button @click.stop="$emit('delete', transaction)" class="p-1.5 text-[var(--text-muted)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 rounded-md transition-colors"><Trash2 :size="16" /></button>
        </div>

        <span 
            class="text-xs md:text-sm font-bold font-numeric whitespace-nowrap" 
            :class="transaction.type === 'receita' ? 'text-[var(--color-success)]' : 'text-[var(--text-main)]'"
        >
            {{ transaction.type === 'despesa' ? '-' : '+' }} {{ formatCurrency(transaction.amount) }}
        </span>
    </div>
  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>