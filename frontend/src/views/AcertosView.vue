<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import SidebarDesktop from '../components/SidebarDesktop.vue'; 
import { 
    ChevronLeft, Check, X, Wallet, History, Trash2, 
    ArrowUpRight, ArrowDownLeft, AlertTriangle, Users 
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

const isLoading = ref(true);
const summary = ref({ total_receivable: 0, debtors: [] });

// Modais
const isPaymentModalOpen = ref(false);
const isHistoryModalOpen = ref(false);
const isDeleteModalOpen = ref(false);

// Dados Selecionados
const selectedDebtor = ref(null);
const debtorHistory = ref([]);
const paymentAmount = ref('');
const transactionToDelete = ref(null);

// --- CARREGAMENTO ---
const fetchDebts = async () => {
    isLoading.value = true;
    try {
        const res = await api.get('/debts/summary');
        summary.value = res.data;
    } catch (error) {
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

const fetchHistory = async (name) => {
    try {
        const res = await api.get(`/debts/${name}/history`);
        debtorHistory.value = res.data;
    } catch (error) {
        console.error("Erro ao buscar histórico", error);
    }
};

// --- AÇÕES ---
const openPaymentModal = (debtor) => {
    selectedDebtor.value = debtor;
    paymentAmount.value = (debtor.balance * 100).toFixed(0); 
    isPaymentModalOpen.value = true;
};

const openHistoryModal = async (debtor) => {
    selectedDebtor.value = debtor;
    debtorHistory.value = []; 
    isHistoryModalOpen.value = true;
    await fetchHistory(debtor.name);
};

const askToDelete = (tx) => {
    transactionToDelete.value = tx;
    isDeleteModalOpen.value = true;
};

const confirmDelete = async () => {
    if (!transactionToDelete.value) return;
    try {
        await api.delete(`/transactions/${transactionToDelete.value.id}`);
        debtorHistory.value = debtorHistory.value.filter(tx => tx.id !== transactionToDelete.value.id);
        fetchDebts(); 
        isDeleteModalOpen.value = false;
        transactionToDelete.value = null;
    } catch (error) {
        alert("Erro ao excluir.");
    }
};

const confirmPayment = async () => {
    if (!paymentAmount.value || paymentAmount.value <= 0) return;
    const valueToSend = paymentAmount.value / 100;

    try {
        await api.post(`/debts/${selectedDebtor.value.name}/pay`, { amount: valueToSend });
        isPaymentModalOpen.value = false;
        fetchDebts(); 
    } catch (error) {
        alert("Erro ao registrar pagamento.");
    }
};

// --- FORMATADORES ---
const displayAmount = computed({
    get: () => {
        if (!paymentAmount.value) return '';
        return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2 }).format(paymentAmount.value / 100);
    },
    set: (val) => {
        const clean = val.replace(/\D/g, '');
        paymentAmount.value = clean ? parseInt(clean) : '';
    }
});

const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
const formatDate = (dateStr) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}`;
}
const getItemsLabel = (count) => count === 1 ? 'item' : 'itens';

onMounted(fetchDebts);
</script>

<template>
  <div class="h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans transition-colors duration-300 flex overflow-hidden relative">
    
    <div class="hidden lg:flex h-full shrink-0 z-10">
        <SidebarDesktop />
    </div>

    <div class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
        
        <div class="lg:hidden px-4 py-4 flex items-center justify-between bg-[var(--bg-surface)] border-b border-[var(--border)] sticky top-0 z-20 shadow-sm shrink-0">
            <div class="flex items-center gap-3">
                <button @click="goBack" class="p-2 -ml-2 rounded-full hover:bg-[var(--bg-app)] transition-colors active:scale-95 text-[var(--text-main)]">
                    <ChevronLeft :size="22" />
                </button>
                <h1 class="text-lg font-bold tracking-tight">Acertos</h1>
            </div>
            <div class="text-right">
                <span class="text-[10px] text-[var(--text-muted)] uppercase font-bold block leading-none mb-0.5">Total</span>
                <span class="text-sm font-bold font-numeric text-[var(--color-primary)]">{{ formatCurrency(summary.total_receivable) }}</span>
            </div>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <Users :size="20" />
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-tight leading-tight">Acertos & Cobranças</h1>
                    <p class="text-[11px] text-[var(--text-muted)]">Gerencie quem te deve e registre recebimentos</p>
                </div>
             </div>
             
             <div class="bg-[var(--bg-app)] px-4 py-1.5 rounded-lg border border-[var(--border)] flex items-center gap-3">
                <span class="text-[11px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Total a Receber</span>
                <span class="text-lg font-bold font-numeric text-[var(--color-primary)]">{{ formatCurrency(summary.total_receivable) }}</span>
             </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-24 custom-scroll">
            
            <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div v-for="i in 4" :key="i" class="h-40 bg-[var(--bg-surface)] rounded-xl animate-pulse border border-[var(--border)]"></div>
            </div>
            
            <div v-else-if="summary.debtors.length === 0" class="flex flex-col items-center justify-center h-full opacity-50 pb-20">
                <div class="w-20 h-20 bg-[var(--bg-surface)] rounded-full flex items-center justify-center mb-4 border border-[var(--border)]">
                    <Wallet :size="40" class="text-[var(--text-muted)]" />
                </div>
                <p class="text-lg font-medium text-[var(--text-main)]">Nenhum acerto pendente.</p>
                <p class="text-sm text-[var(--text-muted)]">Tudo quite por aqui! 🎉</p>
            </div>

            <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
                
                <div v-for="debtor in summary.debtors" :key="debtor.name" 
                     class="relative overflow-hidden rounded-2xl border transition-all duration-300 group hover:-translate-y-1 hover:shadow-lg"
                     :class="debtor.is_fully_paid ? 'bg-[var(--bg-surface)]/40 border-[var(--border)] opacity-60' : 'bg-[var(--bg-surface)] border-[var(--border)] shadow-sm hover:border-[var(--color-primary)]/30'"
                >
                    <div v-if="debtor.is_fully_paid" class="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                        <div class="bg-[var(--color-success)]/10 border border-[var(--color-success)]/20 text-[var(--color-success)] px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-widest flex items-center gap-2 transform -rotate-12 backdrop-blur-sm shadow-sm">
                            <Check :size="16" stroke-width="3" /> Pago
                        </div>
                    </div>

                    <div class="p-5 flex flex-col h-full relative z-0">
                        
                        <div class="flex justify-between items-start mb-6">
                            <div class="flex items-center gap-3.5">
                                <div class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold transition-colors shadow-sm"
                                     :class="debtor.is_fully_paid ? 'bg-[var(--bg-app)] text-[var(--text-muted)]' : 'text-white'"
                                     :style="!debtor.is_fully_paid ? 'background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))' : ''">
                                    {{ debtor.name.charAt(0).toUpperCase() }}
                                </div>
                                <div>
                                    <h3 class="font-bold text-base text-[var(--text-main)] leading-tight mb-0.5">{{ debtor.name }}</h3>
                                    <div class="flex flex-col text-[11px] text-[var(--text-muted)]">
                                        <span>{{ debtor.count }} {{ getItemsLabel(debtor.count) }} pendentes</span>
                                    </div>
                                </div>
                            </div>
                            
                            <button @click.stop="openHistoryModal(debtor)" class="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--bg-app)] transition-colors opacity-100 lg:opacity-0 group-hover:opacity-100 active:scale-95">
                                <History :size="18" />
                            </button>
                        </div>

                        <div class="mt-auto pt-4 border-t border-[var(--border)]/50">
                            <div class="flex items-end justify-between">
                                <div>
                                    <span class="text-[10px] text-[var(--text-muted)] uppercase font-bold tracking-wider block mb-0.5">Resta Pagar</span>
                                    <span class="text-xl font-bold font-numeric tracking-tight" 
                                          :class="debtor.is_fully_paid ? 'text-[var(--text-muted)] line-through decoration-2' : 'text-[var(--text-main)]'">
                                        {{ formatCurrency(debtor.balance) }}
                                    </span>
                                </div>
                                
                                <button v-if="!debtor.is_fully_paid" 
                                        @click.stop="openPaymentModal(debtor)"
                                        class="h-9 px-4 text-white rounded-lg text-xs font-bold transition-all shadow-md active:scale-95 flex items-center gap-1.5"
                                        style="background-color: var(--color-primary); box-shadow: 0 4px 6px -1px rgba(var(--color-primary), 0.2);">
                                    Receber
                                </button>
                            </div>
                            
                            <div v-if="!debtor.is_fully_paid && debtor.total_paid > 0" class="mt-3 flex items-center gap-2">
                                <div class="flex-1 h-1.5 bg-[var(--bg-app)] rounded-full overflow-hidden">
                                    <div class="h-full bg-[var(--color-success)] rounded-full" :style="{ width: Math.min((debtor.total_paid / debtor.total_debt) * 100, 100) + '%' }"></div>
                                </div>
                                <span class="text-[9px] font-bold text-[var(--color-success)] whitespace-nowrap">
                                    Pago {{ formatCurrency(debtor.total_paid) }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <Teleport to="body">
        <div v-if="isPaymentModalOpen" class="fixed inset-0 z-[9990] flex items-end sm:items-center justify-center sm:p-4">
            <div @click="isPaymentModalOpen = false" class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"></div>
            <div class="relative w-full sm:max-w-[320px] bg-[var(--bg-surface)] rounded-t-2xl sm:rounded-2xl border-t sm:border border-[var(--border)] p-5 shadow-2xl animate-in slide-in-from-bottom-10 sm:slide-in-from-bottom-2 duration-200">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="font-bold text-[var(--text-main)]">Registrar Pagamento</h3>
                    <button @click="isPaymentModalOpen = false" class="text-[var(--text-muted)] hover:text-[var(--text-main)]"><X :size="20"/></button>
                </div>
                <div class="text-center mb-6">
                    <p class="text-xs text-[var(--text-muted)] mb-2">Quanto <strong>{{ selectedDebtor?.name }}</strong> pagou?</p>
                    <div class="flex items-center justify-center gap-1">
                        <span class="text-xl text-[var(--text-muted)]">R$</span>
                        <input v-model="displayAmount" type="tel" class="bg-transparent text-4xl font-bold text-[var(--text-main)] w-full text-center focus:outline-none placeholder-[var(--text-muted)]/30 font-numeric" placeholder="0,00" autofocus />
                    </div>
                    <p class="text-[10px] text-[var(--text-muted)] mt-2">
                        Faltam: <span class="text-[var(--color-danger)] font-bold">{{ formatCurrency(selectedDebtor?.balance) }}</span>
                    </p>
                </div>
                <button @click="confirmPayment" 
                        class="w-full py-3.5 rounded-xl text-white font-bold text-sm shadow-lg active:scale-95 transition-all hover:brightness-110"
                        style="background-color: var(--color-success); box-shadow: 0 10px 15px -3px rgba(var(--color-success), 0.2);">
                    Confirmar Recebimento
                </button>
            </div>
        </div>
    </Teleport>

    <Teleport to="body">
        <div v-if="isHistoryModalOpen" class="fixed inset-0 z-[9990] flex items-end sm:items-center justify-center sm:p-4">
            <div @click="isHistoryModalOpen = false" class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity"></div>
            <div class="relative w-full sm:max-w-[400px] bg-[var(--bg-surface)] rounded-t-2xl sm:rounded-2xl border-t sm:border border-[var(--border)] p-0 shadow-2xl flex flex-col max-h-[85vh] animate-in slide-in-from-bottom-10 sm:slide-in-from-bottom-2 duration-200">
                
                <div class="p-4 border-b border-[var(--border)] flex justify-between items-center bg-[var(--bg-app)]/50 rounded-t-2xl">
                    <div>
                        <h3 class="font-bold text-[var(--text-main)]">{{ selectedDebtor?.name }}</h3>
                        <p class="text-[10px] text-[var(--text-muted)]">Extrato de atividades</p>
                    </div>
                    <button @click="isHistoryModalOpen = false" class="p-1 rounded-full bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)]"><X :size="18"/></button>
                </div>

                <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scroll">
                    <div v-if="debtorHistory.length === 0" class="text-center py-8 text-[var(--text-muted)] text-xs">Carregando...</div>
                    
                    <div v-for="tx in debtorHistory" :key="tx.id" class="flex items-center justify-between p-3 rounded-xl border border-[var(--border)] bg-[var(--bg-app)]/30 hover:bg-[var(--bg-app)] transition-colors">
                        <div class="flex items-center gap-3">
                            <div class="p-2 rounded-full" :class="tx.type === 'income' ? 'bg-[var(--color-success)]/10 text-[var(--color-success)]' : 'bg-[var(--color-danger)]/10 text-[var(--color-danger)]'">
                                <ArrowDownLeft v-if="tx.type === 'income'" :size="16" />
                                <ArrowUpRight v-else :size="16" />
                            </div>
                            <div>
                                <p class="text-xs font-bold text-[var(--text-main)]">{{ tx.description }}</p>
                                <p class="text-[10px] text-[var(--text-muted)]">{{ formatDate(tx.date) }}</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <span class="text-xs font-bold whitespace-nowrap font-numeric" :class="tx.type === 'income' ? 'text-[var(--color-success)]' : 'text-[var(--text-main)]'">
                                {{ tx.type === 'income' ? '+' : '-' }} {{ formatCurrency(tx.amount) }}
                            </span>
                            <button @click="askToDelete(tx)" class="p-1.5 rounded-md text-[var(--text-muted)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 transition-colors">
                                <Trash2 :size="14" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

    <Teleport to="body">
        <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4">
            <div @click="isDeleteModalOpen = false" class="absolute inset-0 bg-black/60 backdrop-blur-[1px]"></div>
            <div class="relative bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-6 w-full max-w-[280px] shadow-2xl animate-in zoom-in-95 duration-200">
                <div class="flex flex-col items-center text-center">
                    <div class="w-12 h-12 rounded-full bg-[var(--color-danger)]/10 text-[var(--color-danger)] flex items-center justify-center mb-4">
                        <AlertTriangle :size="24" />
                    </div>
                    <h3 class="font-bold text-[var(--text-main)] mb-1">Apagar registro?</h3>
                    <p class="text-xs text-[var(--text-muted)] mb-5">
                        Essa ação não pode ser desfeita.
                    </p>
                    <div class="flex gap-3 w-full">
                        <button @click="isDeleteModalOpen = false" class="flex-1 py-2 rounded-xl border border-[var(--border)] text-xs font-bold text-[var(--text-main)] hover:bg-[var(--bg-app)]">Cancelar</button>
                        <button @click="confirmDelete" 
                                class="flex-1 py-2 rounded-xl text-white text-xs font-bold shadow-lg hover:brightness-110"
                                style="background-color: var(--color-danger); box-shadow: 0 4px 6px -1px rgba(var(--color-danger), 0.2);">
                            Apagar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>