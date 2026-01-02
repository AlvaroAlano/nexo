<script setup>
import { ref, computed } from 'vue';
import { X, Trash2, Edit3, Calendar, Tag, Info, CheckCircle2 } from 'lucide-vue-next';
import api from '../services/api';

const props = defineProps({
  isOpen: Boolean,
  transaction: Object 
});

const emit = defineEmits(['close', 'deleted', 'edit', 'updated']);
const isLoading = ref(false);

const formatCurrency = (value) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
const formatDate = (dateString) => {
    if (!dateString) return '';
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day).toLocaleDateString('pt-BR');
};

const handleDelete = async () => {
    if (!confirm("Tem certeza que deseja excluir esta transação?")) return;
    isLoading.value = true;
    try {
        await api.delete(`/transactions/${props.transaction.id}`);
        emit('deleted');
        emit('close');
    } catch (error) {
        alert("Erro ao excluir.");
    } finally {
        isLoading.value = false;
    }
};

const handleEdit = () => {
    emit('edit', props.transaction);
    emit('close');
};

const handleConfirm = async () => {
    isLoading.value = true;
    try {
        await api.put(`/transactions/${props.transaction.id}`, { 
            status: 'pago' 
        });
        emit('updated'); 
        emit('close');
    } catch (error) {
        console.error(error);
        alert("Erro ao atualizar status.");
    } finally {
        isLoading.value = false;
    }
};

const statusTooltip = computed(() => {
    if (!props.transaction) return '';
    if (props.transaction.payment_method === 'credito') {
        return "Compras no crédito são pagas via Fatura.";
    }
    return "Ainda não debitado da conta.";
});
</script>

<template>
  <div v-if="isOpen && transaction" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div @click="$emit('close')" class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"></div>

    <div class="relative w-full max-w-[320px] bg-[var(--bg-surface)] rounded-2xl shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-200 overflow-hidden border border-[var(--border)]">
      
      <div class="h-24 flex items-center justify-center relative transition-colors duration-300" 
           :class="transaction.type === 'receita' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-danger)]'">
          <button @click="$emit('close')" class="absolute top-3 right-3 p-1 bg-black/20 rounded-full text-white hover:bg-black/30 transition-colors"><X :size="18" /></button>
          <div class="text-center text-white">
              <span class="text-xs font-bold opacity-80 uppercase">{{ transaction.type }}</span>
              <h2 class="text-3xl font-bold font-numeric tracking-tight">{{ formatCurrency(transaction.amount) }}</h2>
          </div>
      </div>

      <div class="p-5 space-y-4">
          <div class="text-center">
              <h3 class="text-lg font-bold text-[var(--text-main)] leading-tight">{{ transaction.description }}</h3>
              <p class="text-xs text-[var(--text-muted)] mt-1" v-if="transaction.payment_method === 'credito'">Cartão de Crédito</p>
          </div>

          <div class="space-y-3 py-2">
              <div class="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-app)] border border-[var(--border)]">
                  <div class="flex items-center gap-2 text-[var(--text-muted)]"><Calendar :size="16" /><span class="text-xs">Vencimento</span></div>
                  <span class="text-sm font-bold text-[var(--text-main)]">{{ formatDate(transaction.date) }}</span>
              </div>
              
              <div class="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-app)] border border-[var(--border)]">
                  <div class="flex items-center gap-2 text-[var(--text-muted)]"><Tag :size="16" /><span class="text-xs">Status</span></div>
                  
                  <div class="relative group cursor-help flex items-center gap-2">
                      <span class="text-xs font-bold px-2 py-1 rounded uppercase flex items-center gap-1.5 transition-colors" 
                            :class="transaction.status === 'pago' 
                                ? 'bg-[var(--color-success)]/10 text-[var(--color-success)]' 
                                : 'bg-[var(--color-warning)]/10 text-[var(--color-warning)]'">
                          {{ transaction.status }}
                          <Info v-if="transaction.status === 'pendente'" class="w-3 h-3 md:w-4 md:h-4" />
                      </span>

                      <div v-if="transaction.status === 'pendente'" class="absolute bottom-full right-0 mb-2 w-48 md:w-64 p-2 md:p-3 bg-[var(--bg-surface)] text-[var(--text-main)] text-[10px] md:text-xs rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 text-center border border-[var(--border)]">
                          {{ statusTooltip }}
                      </div>
                  </div>
              </div>
          </div>

          <div class="flex flex-col gap-3 mt-2">
              
              <button v-if="transaction.status === 'pendente' && transaction.payment_method !== 'credito'" 
                      @click="handleConfirm"
                      :disabled="isLoading"
                      class="w-full py-3.5 rounded-xl font-bold text-sm shadow-sm flex items-center justify-center gap-2 text-white transition-all active:scale-95 hover:brightness-110"
                      :class="transaction.type === 'receita' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-success)]'">
                  <CheckCircle2 :size="18" />
                  {{ transaction.type === 'receita' ? 'Confirmar Recebimento' : 'Efetivar Pagamento' }}
              </button>

              <div class="flex gap-3">
                  <button @click="handleDelete" class="flex-1 py-3 rounded-xl border border-[var(--color-danger)]/20 text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 font-bold text-xs flex items-center justify-center gap-2 transition-colors">
                      <Trash2 :size="16" /> Excluir
                  </button>
                  <button @click="handleEdit" class="flex-1 py-3 rounded-xl bg-[var(--bg-app)] text-[var(--text-main)] font-bold text-xs flex items-center justify-center gap-2 hover:brightness-95 transition-all border border-[var(--border)]">
                      <Edit3 :size="16" /> Editar
                  </button>
              </div>
          </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>