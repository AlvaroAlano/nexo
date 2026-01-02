<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { 
    X, Calendar, Tag, CreditCard, AlignLeft, ArrowUpCircle, 
    ArrowDownCircle, Repeat, User, Users, Wallet, ScanLine, Loader2
} from 'lucide-vue-next';
import transactionService from '../services/transactions';
import { useSettings } from '../composables/useSettings'; 

const props = defineProps({
  isOpen: Boolean,
  transactionToEdit: Object
});

const emit = defineEmits(['close', 'success']);
const { enableDebts } = useSettings(); 

// --- REFS DE UI ---
const amountInput = ref(null); // Referência para o input de valor

// --- ESTADOS DO FORMULÁRIO ---
const type = ref('despesa'); 
const amount = ref('');
const description = ref('');
const date = ref(new Date().toISOString().split('T')[0]);
const categoryId = ref('');
const paymentMethod = ref('pix'); 
const cardId = ref('');
const installments = ref(1);

// Recorrência
const isFixed = ref(false); 
const recurrencePeriod = ref('mensal');

// Acertos (Quem comprou)
const debtorType = ref('eu'); 
const debtorName = ref('');

// Estados de UI e Dados
const isSubmitting = ref(false);     // Loading do botão Salvar
const isLoadingOptions = ref(false); // Loading dos selects (categorias/cartões)
const categories = ref([]);
const cards = ref([]);

// --- COMPUTEDS ---
const isEditing = computed(() => !!props.transactionToEdit);

const displayAmount = computed({
  get: () => {
    if (!amount.value) return '';
    return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2 }).format(amount.value / 100);
  },
  set: (val) => {
    let clean = val.replace(/\D/g, '');
    if (clean.length > 11) clean = clean.slice(0, 11);
    amount.value = clean ? parseInt(clean) : '';
  }
});

const themeColor = computed(() => type.value === 'receita' ? 'var(--color-success)' : 'var(--color-danger)');
const btnClass = computed(() => type.value === 'receita' 
    ? 'bg-[var(--color-success)] shadow-[var(--color-success)]/20' 
    : 'bg-[var(--color-danger)] shadow-[var(--color-danger)]/20');

const filteredCategories = computed(() => {
    const targetType = type.value === 'despesa' ? 'expense' : (type.value === 'receita' ? 'income' : 'investment');
    return categories.value.filter(c => c.type === targetType);
});

// --- CARREGAMENTO ---
const loadOptions = async () => {
  isLoadingOptions.value = true;
  try {
    const [catsRes, cardsRes] = await transactionService.getOptions();
    categories.value = Array.isArray(catsRes.data) ? catsRes.data : (catsRes.data.items || []);
    cards.value = Array.isArray(cardsRes.data) ? cardsRes.data : (cardsRes.data.items || []);
  } catch (e) { 
      console.error("Erro ao carregar opções:", e); 
  } finally {
      isLoadingOptions.value = false;
  }
};

// --- WATCHERS ---

// 1. Preencher, Limpar e Focar ao Abrir
watch(() => props.isOpen, async (val) => {
  if (val) {
    // Carrega dados
    await loadOptions();
    
    // Edição
    if (props.transactionToEdit) {
        populateForm(props.transactionToEdit);
        if (paymentMethod.value === 'credito' && cardId.value) {
            const cardExists = cards.value.some(c => c.id === cardId.value);
            if (!cardExists) cardId.value = ''; 
        }
    }

    // UX: Foco automático no valor (Melhoria)
    await nextTick();
    setTimeout(() => {
        amountInput.value?.focus();
    }, 100); // Pequeno delay para garantir que a animação CSS terminou
  } else {
    setTimeout(() => resetForm(), 200);
  }
});

// 2. Monitorar edição
watch(() => props.transactionToEdit, (tx) => {
  if (tx && props.isOpen) populateForm(tx);
});

// 3. Resetar campos de crédito
watch(paymentMethod, (newVal) => {
   if (newVal !== 'credito') {
      installments.value = 1;
      cardId.value = '';
   }
});

// 4. Resetar categoria
watch(type, () => categoryId.value = '');

// --- HELPERS ---
const populateForm = (tx) => {
    type.value = tx.type;
    amount.value = Math.round(tx.amount * 100); 
    description.value = tx.description;
    date.value = tx.date;
    categoryId.value = tx.category_id || '';
    paymentMethod.value = tx.payment_method || 'pix';
    cardId.value = tx.card_id || ''; 
    installments.value = tx.installment_total || 1;
    isFixed.value = tx.is_recurring || false; 
    recurrencePeriod.value = tx.frequency || 'mensal';
    
    if (tx.debtor_name) {
        debtorType.value = 'outro';
        debtorName.value = tx.debtor_name;
    } else {
        debtorType.value = 'eu';
        debtorName.value = '';
    }
};

const resetForm = () => {
  type.value = 'despesa';
  amount.value = '';
  description.value = '';
  date.value = new Date().toISOString().split('T')[0];
  categoryId.value = '';
  paymentMethod.value = 'pix';
  cardId.value = '';
  installments.value = 1;
  isFixed.value = false;
  recurrencePeriod.value = 'mensal';
  debtorType.value = 'eu';
  debtorName.value = '';
};

const handleScanReceipt = () => {
    alert("Funcionalidade de IA (OCR) em breve! 📸");
};

// --- SUBMIT ---
const handleSubmit = async () => {
  if (!amount.value || !description.value || !date.value) {
      alert("Preencha valor, descrição e data."); return;
  }
  if (paymentMethod.value === 'credito' && !cardId.value) {
      alert("Selecione um cartão de crédito."); return;
  }
  if (enableDebts.value && debtorType.value === 'outro' && !debtorName.value.trim()) {
      alert("Digite o nome de quem comprou."); return;
  }

  isSubmitting.value = true;

  const isCredit = paymentMethod.value === 'credito';
  let finalInstallments = (isCredit && installments.value) ? parseInt(installments.value) : 1;
  if (finalInstallments < 1) finalInstallments = 1;

  const finalDebtorName = (enableDebts.value && debtorType.value === 'outro') ? debtorName.value.trim() : null;

  const payload = {
    type: type.value,
    amount: amount.value / 100, 
    description: description.value,
    date: date.value,
    category_id: categoryId.value ? parseInt(categoryId.value) : null,
    payment_method: paymentMethod.value,
    card_id: (isCredit && cardId.value) ? parseInt(cardId.value) : null,
    installment_total: finalInstallments,
    is_installment: isCredit && finalInstallments > 1,
    is_recurring: isFixed.value, 
    frequency: isFixed.value ? recurrencePeriod.value : null,
    debtor_name: finalDebtorName
  };

  try {
    if (isEditing.value) {
        await transactionService.update(props.transactionToEdit.id, payload);
    } else {
        await transactionService.create(payload);
    }
    emit('success');
    emit('close'); 
  } catch (error) {
    console.error("Erro ao salvar:", error);
    alert("Erro ao processar. Verifique os dados."); 
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <div @click="$emit('close')" class="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity"></div>

    <div class="relative w-full max-w-[380px] bg-[var(--bg-surface)] rounded-3xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden border border-[var(--border)] animate-in zoom-in-95 duration-200">
      
      <div class="px-5 pt-4 pb-2 flex justify-between items-center bg-[var(--bg-surface)] z-10 shrink-0">
        <h2 class="text-xs font-bold text-[var(--text-main)] uppercase tracking-widest opacity-70">
            {{ isEditing ? 'Editar Lançamento' : 'Nova Transação' }}
        </h2>
        
        <div class="flex items-center gap-2">
            <button v-if="!isEditing" @click="handleScanReceipt" class="p-2 rounded-full bg-[var(--bg-app)] text-[var(--color-primary)] hover:bg-[var(--color-primary)]/10 transition-colors" title="Escanear Nota (IA)">
                <ScanLine :size="18" />
            </button>
            <button @click="$emit('close')" class="p-1.5 rounded-full hover:bg-[var(--bg-app)] text-[var(--text-muted)] transition-colors">
                <X :size="20" />
            </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto custom-scroll px-5 pt-0 pb-4 space-y-5">
        
        <div class="flex p-1 bg-[var(--bg-app)] rounded-xl border border-[var(--border)] relative shrink-0 mt-2">
            <button @click="type = 'despesa'" class="flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all relative z-10"
                :class="type === 'despesa' ? 'text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                <ArrowDownCircle :size="16" /> Despesa
                <div v-if="type === 'despesa'" class="absolute inset-0 bg-[var(--color-danger)] rounded-lg -z-10 animate-in fade-in zoom-in-95 duration-200"></div>
            </button>
            <button @click="type = 'receita'" class="flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all relative z-10"
                :class="type === 'receita' ? 'text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                <ArrowUpCircle :size="16" /> Receita
                <div v-if="type === 'receita'" class="absolute inset-0 bg-[var(--color-success)] rounded-lg -z-10 animate-in fade-in zoom-in-95 duration-200"></div>
            </button>
        </div>

        <div class="text-center py-1">
            <p class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-1">Valor da transação</p>
            <div class="flex items-center justify-center gap-1 scale-110">
                <span class="text-2xl font-bold opacity-50 mb-1" :style="{ color: themeColor }">R$</span>
                <input 
                       ref="amountInput"
                       v-model="displayAmount" 
                       type="tel" 
                       placeholder="0,00" 
                       class="bg-transparent text-5xl font-bold text-center w-full focus:outline-none placeholder-[var(--text-muted)]/20 font-numeric py-0 tracking-tight" 
                       :style="{ color: themeColor }"
                />
            </div>
        </div>

        <div class="space-y-3">
            <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-3 border border-[var(--border)] focus-within:border-[var(--color-primary)] focus-within:bg-[var(--bg-surface)] transition-all shadow-sm">
                <AlignLeft :size="18" class="text-[var(--text-muted)]" />
                <input v-model="description" type="text" placeholder="Descrição (ex: Mercado)" class="flex-1 bg-transparent text-sm font-medium text-[var(--text-main)] placeholder-[var(--text-muted)] focus:outline-none" />
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)] focus-within:bg-[var(--bg-surface)] transition-all shadow-sm relative">
                    <Tag :size="16" class="text-[var(--text-muted)]" />
                    <select v-if="!isLoadingOptions" v-model="categoryId" class="w-full bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none dark-scheme-select cursor-pointer">
                       <option value="" disabled>Categoria</option>
                       <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                    </select>
                    <div v-else class="text-xs text-[var(--text-muted)] flex items-center gap-2">
                        <Loader2 class="animate-spin" :size="12" /> Carregando...
                    </div>
                </div>

                <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)] focus-within:bg-[var(--bg-surface)] transition-all shadow-sm">
                    <Calendar :size="16" class="text-[var(--text-muted)]" />
                    <input v-model="date" type="date" class="w-full bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none dark-scheme-select cursor-pointer" />
                </div>
            </div>
        </div>

        <div v-if="type === 'despesa' && enableDebts" class="space-y-2 animate-in fade-in duration-300">
            <p class="text-[10px] text-[var(--text-muted)] font-bold uppercase px-1 ml-1">Para quem é a compra?</p>
            <div class="flex gap-2">
                <button @click="debtorType = 'eu'" class="flex-1 py-2 rounded-xl border flex items-center justify-center gap-2 text-xs font-bold transition-all"
                        :class="debtorType === 'eu' 
                            ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)] text-[var(--color-primary)]' 
                            : 'border-[var(--border)] bg-[var(--bg-app)]/30 text-[var(--text-muted)]'">
                    <User :size="14" /> Para mim
                </button>
                <button @click="debtorType = 'outro'" class="flex-1 py-2 rounded-xl border flex items-center justify-center gap-2 text-xs font-bold transition-all"
                        :class="debtorType === 'outro' 
                            ? 'border-[var(--color-warning)] bg-[var(--color-warning)]/10 text-[var(--color-warning)]' 
                            : 'border-[var(--border)] bg-[var(--bg-app)]/30 text-[var(--text-muted)]'">
                    <Users :size="14" /> Para outro
                </button>
            </div>
            
            <div v-if="debtorType === 'outro'" class="animate-in slide-in-from-top-1 duration-200">
                <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-2 border border-[var(--color-warning)]/30">
                    <Users :size="16" class="text-[var(--color-warning)]" />
                    <input v-model="debtorName" type="text" placeholder="Nome da pessoa (ex: João)" class="flex-1 bg-transparent text-sm font-medium text-[var(--text-main)] placeholder-[var(--text-muted)] focus:outline-none" />
                </div>
            </div>
        </div>

        <div class="space-y-2">
            <p class="text-[10px] text-[var(--text-muted)] font-bold uppercase px-1 ml-1">Forma de Pagamento</p>
            <div class="grid grid-cols-2 gap-2">
                <button @click="paymentMethod = 'pix'" class="py-2.5 rounded-xl border flex items-center justify-center gap-2 text-xs font-bold transition-all"
                        :class="paymentMethod === 'pix' 
                            ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)] text-[var(--color-primary)]' 
                            : 'border-[var(--border)] bg-[var(--bg-app)]/30 text-[var(--text-muted)] hover:bg-[var(--bg-app)]'">
                    <Wallet :size="14" /> Saldo / Pix
                </button>
                <button @click="paymentMethod = 'credito'" class="py-2.5 rounded-xl border flex items-center justify-center gap-2 text-xs font-bold transition-all"
                        :class="paymentMethod === 'credito' 
                            ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)] text-[var(--color-primary)]' 
                            : 'border-[var(--border)] bg-[var(--bg-app)]/30 text-[var(--text-muted)] hover:bg-[var(--bg-app)]'">
                    <CreditCard :size="14" /> Crédito
                </button>
            </div>

            <div v-if="paymentMethod === 'credito'" class="space-y-2.5 animate-in slide-in-from-top-1 duration-200 pt-1">
                <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)] transition-all">
                    <CreditCard :size="16" class="text-[var(--text-muted)]" />
                    <select v-if="!isLoadingOptions" v-model="cardId" class="w-full bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none dark-scheme-select cursor-pointer">
                        <option value="" disabled>Selecione o Cartão</option>
                        <option v-for="card in cards" :key="card.id" :value="card.id">{{ card.name }}</option>
                    </select>
                    <div v-else class="text-xs text-[var(--text-muted)] flex items-center gap-2">
                        <Loader2 class="animate-spin" :size="12" /> Carregando...
                    </div>
                </div>
                <div class="bg-[var(--bg-app)]/50 rounded-xl px-3 py-3 flex items-center gap-2 border border-[var(--border)] focus-within:border-[var(--color-primary)] transition-all">
                    <span class="text-xs font-bold text-[var(--text-muted)]">Parcelas:</span>
                    <input v-model="installments" type="number" min="1" max="24" class="flex-1 bg-transparent text-sm font-medium text-[var(--text-main)] focus:outline-none font-numeric" />
                    <span class="text-xs text-[var(--text-muted)] font-bold" v-if="amount && installments > 1">
                        {{ (amount/100/installments).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'}) }}/mês
                    </span>
                </div>
            </div>
        </div>

        <div class="rounded-xl border border-[var(--border)] bg-[var(--bg-app)]/30 overflow-hidden transition-all duration-300" 
             :class="isFixed ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)]' : ''">
            
            <div class="flex items-center justify-between p-3 cursor-pointer select-none" @click="isFixed = !isFixed">
                <div class="flex items-center gap-2">
                    <div class="p-1 rounded bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border)]">
                        <Repeat :size="12" />
                    </div>
                    <div><p class="text-xs font-bold text-[var(--text-main)]">Recorrência (Fixa)</p></div>
                </div>
                <div class="relative inline-block w-8 h-4 bg-[var(--border)] rounded-full transition-colors" :class="isFixed ? 'bg-[var(--color-primary)]' : ''">
                    <span class="absolute left-1 top-1 w-2 h-2 bg-white rounded-full transition-transform" :class="isFixed ? 'translate-x-4' : 'translate-x-0'"></span>
                </div>
            </div>

            <div v-if="isFixed" class="px-3 pb-3 animate-in slide-in-from-top-2">
                <div class="bg-[var(--bg-surface)] rounded-xl px-3 py-2 flex items-center gap-2 border border-[var(--border)]">
                    <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase">Frequência:</span>
                    <select v-model="recurrencePeriod" class="flex-1 bg-transparent text-xs font-bold text-[var(--text-main)] focus:outline-none dark-scheme-select text-right cursor-pointer">
                        <option value="semanal">Semanal</option>
                        <option value="mensal">Mensal</option>
                        <option value="anual">Anual</option>
                    </select>
                </div>
            </div>
        </div>

      </div>

      <div class="p-5 pt-3 bg-[var(--bg-surface)] border-t border-[var(--border)] z-20 shrink-0">
        <button @click="handleSubmit" :disabled="isSubmitting" 
                class="w-full py-3.5 rounded-xl font-bold text-sm text-white transition-all active:scale-95 flex items-center justify-center gap-2 shadow-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed"
                :class="btnClass">
            <Loader2 v-if="isSubmitting" class="animate-spin" :size="20" />
            <span v-else>{{ isEditing ? 'Salvar Alterações' : 'Confirmar Transação' }}</span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
.dark-scheme-select { color-scheme: dark; }
.dark-scheme-select option { background-color: #1e1e1e; color: white; }
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>