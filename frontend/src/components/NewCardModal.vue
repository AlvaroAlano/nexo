<script setup>
import { ref, computed, watch } from 'vue';
import { X, CreditCard, Calendar, Check } from 'lucide-vue-next';
import api from '../services/api';

const props = defineProps({ 
  isOpen: Boolean,
  cardToEdit: Object 
});

const emit = defineEmits(['close', 'success']);

const name = ref('');
const limit = ref(''); 
const closingDay = ref('');
const dueDay = ref('');
const color = ref('#2563EB'); // Default agora é um azul (ou use uma das cores da lista)
const isLoading = ref(false);

const colors = [
  '#2563EB', '#820AD1', '#F9DD16', '#EC7000', '#CC092F', '#10B981', '#18181B', '#64748B'
];

const isEditing = computed(() => !!props.cardToEdit);

watch(() => props.cardToEdit, (newCard) => {
  if (newCard) {
    name.value = newCard.name;
    limit.value = Math.round(newCard.limit * 100); 
    closingDay.value = newCard.closing_day;
    dueDay.value = newCard.due_day;
    color.value = newCard.color || '#2563EB';
  } else {
    resetForm();
  }
});

watch(() => props.isOpen, (isOpen) => {
    if (!isOpen && !props.cardToEdit) resetForm();
});

const resetForm = () => {
    name.value = ''; 
    limit.value = ''; 
    closingDay.value = ''; 
    dueDay.value = '';
    color.value = '#2563EB';
};

const displayLimit = computed({
  get: () => {
    if (!limit.value) return '';
    return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2 }).format(limit.value / 100);
  },
  set: (val) => {
    const clean = val.replace(/\D/g, '');
    limit.value = clean ? parseInt(clean) : '';
  }
});

const handleSubmit = async () => {
  if (!name.value || !limit.value || !closingDay.value || !dueDay.value) {
      alert("Preencha todos os campos!");
      return;
  }
  
  isLoading.value = true;
  
  const payload = {
    name: name.value,
    limit: limit.value / 100, 
    closing_day: parseInt(closingDay.value),
    due_day: parseInt(dueDay.value),
    color: color.value
  };

  try {
    if (isEditing.value) {
        await api.put(`/credit-cards/${props.cardToEdit.id}`, payload);
    } else {
        await api.post('/credit-cards/', payload);
    }
    
    emit('success');
    emit('close'); 
    resetForm();   
  } catch (error) {
    console.error(error);
    alert("Erro ao salvar cartão.");
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <Teleport to="body">
      <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        
        <div @click="$emit('close')" class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"></div>

        <div class="relative w-full max-w-[360px] bg-[var(--bg-surface)] rounded-3xl shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-200 border border-[var(--border)] z-[10000]">
          
          <div class="px-5 py-4 border-b border-[var(--border)] flex justify-between items-center bg-[var(--bg-app)]/50 rounded-t-3xl">
            <h2 class="text-xs font-bold text-[var(--text-main)] uppercase tracking-wider">
                {{ isEditing ? 'Editar Cartão' : 'Novo Cartão' }}
            </h2>
            <button @click="$emit('close')" class="text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors"><X :size="20" /></button>
          </div>

          <div class="p-5 space-y-5">
            
            <div>
              <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-1.5 block px-1">Nome do Cartão</label>
              <div class="bg-[var(--bg-app)] rounded-xl px-4 py-3.5 flex items-center gap-3 border border-[var(--border)] focus-within:border-[var(--color-primary)] transition-colors">
                  <CreditCard :size="18" :style="{ color: color }" />
                  <input v-model="name" type="text" placeholder="Ex: Nubank, XP..." class="flex-1 bg-transparent text-sm font-medium text-[var(--text-main)] placeholder-[var(--text-muted)] focus:outline-none" autofocus />
              </div>
            </div>

            <div>
              <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-1.5 block px-1">Limite Total</label>
              <div class="bg-[var(--bg-app)] rounded-xl px-4 py-3.5 flex items-center gap-3 border border-[var(--border)] focus-within:border-[var(--color-primary)] transition-colors">
                  <span class="text-[var(--text-muted)] font-bold text-sm">R$</span>
                  <input v-model="displayLimit" type="tel" placeholder="0,00" class="flex-1 bg-transparent text-xl font-bold text-[var(--text-main)] placeholder-[var(--text-muted)] focus:outline-none font-numeric" />
              </div>
            </div>

            <div class="flex gap-4">
              <div class="flex-1">
                  <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-1.5 block px-1">Dia Fechamento</label>
                  <div class="bg-[var(--bg-app)] rounded-xl px-3 py-3.5 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)]">
                    <Calendar :size="16" class="text-[var(--text-muted)]" />
                    <input v-model="closingDay" type="number" placeholder="Dia" min="1" max="31" class="w-full bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none" />
                  </div>
              </div>
              <div class="flex-1">
                  <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-1.5 block px-1">Dia Vencimento</label>
                  <div class="bg-[var(--bg-app)] rounded-xl px-3 py-3.5 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)]">
                    <Calendar :size="16" class="text-[var(--text-muted)]" />
                    <input v-model="dueDay" type="number" placeholder="Dia" min="1" max="31" class="w-full bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none" />
                  </div>
              </div>
            </div>

            <div>
                <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-2 block px-1">Cor do Cartão</label>
                <div class="flex flex-wrap gap-3 justify-center bg-[var(--bg-app)] p-4 rounded-xl border border-[var(--border)]">
                    <button 
                        v-for="c in colors" :key="c"
                        @click="color = c"
                        class="w-8 h-8 rounded-full transition-all flex items-center justify-center shadow-sm hover:scale-110 active:scale-95 relative"
                        :style="{ 
                            backgroundColor: c, 
                            border: color === c ? '2px solid var(--bg-surface)' : '2px solid transparent',
                            boxShadow: color === c ? '0 0 0 2px var(--text-main)' : 'none'
                        }"
                    >
                        <div v-if="color === c" class="absolute inset-0 flex items-center justify-center">
                            <Check :size="14" :class="['#F9DD16', '#E1E1E6'].includes(c) ? 'text-black' : 'text-white'" class="drop-shadow-md" />
                        </div>
                    </button>
                </div>
            </div>

            <button @click="handleSubmit" :disabled="isLoading" 
                class="w-full py-3.5 rounded-xl font-bold text-sm text-white shadow-lg mt-2 transition-all active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                style="background-color: var(--color-primary); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);"
            >
                <span v-if="isLoading" class="flex items-center gap-2">
                  Salvando...
                </span>
                <span v-else>{{ isEditing ? 'Atualizar Cartão' : 'Criar Cartão' }}</span>
            </button>

          </div>
        </div>
      </div>
  </Teleport>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
</style>