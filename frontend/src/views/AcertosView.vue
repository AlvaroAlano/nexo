<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import debtService from '../services/debts';
import api from '../services/api'; // Para buscar contas
import SidebarDesktop from '../components/SidebarDesktop.vue'; 
import { 
    ChevronLeft, Check, X, Wallet, History, Trash2, 
    ArrowUpRight, ArrowDownLeft, AlertTriangle, Users, MessageCircle, Loader2 
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

const isLoading = ref(true);
const summary = ref({ total_receivable: 0, debtors: [] });
const accounts = ref([]); // Lista de contas para receber o dinheiro

// Modais
const isPaymentModalOpen = ref(false);
const isHistoryModalOpen = ref(false);
const isDeleteModalOpen = ref(false);
const isLoadingHistory = ref(false);

// Dados Selecionados
const selectedDebtor = ref(null);
const debtorHistory = ref([]);
const debtorToDelete = ref(null);

// Form Pagamento
const paymentForm = ref({
    amount: '',
    date: new Date().toISOString().split('T')[0],
    method: 'pix',
    accountId: ''
});

// --- CARREGAMENTO ---
const fetchDebts = async () => {
    isLoading.value = true;
    try {
        const res = await debtService.getSummary();
        summary.value = res.data;
    } catch (error) {
        // Erro já logado no service
    } finally {
        isLoading.value = false;
    }
};

const fetchAccounts = async () => {
    try {
        const res = await api.get('/accounts/');
        accounts.value = res.data;
        // Seleciona a primeira conta por padrão se houver
        if (accounts.value.length > 0) paymentForm.value.accountId = accounts.value[0].id;
    } catch (e) {
        console.error("Erro ao buscar contas", e);
    }
};

const fetchHistory = async (name) => {
    isLoadingHistory.value = true;
    try {
        const res = await debtService.getHistory(name);
        debtorHistory.value = res.data;
    } catch (error) {
        alert("Erro ao carregar histórico");
    } finally {
        isLoadingHistory.value = false;
    }
};

// --- AÇÕES ---
const openPaymentModal = (debtor) => {
    selectedDebtor.value = debtor;
    // Preenche com o valor total devido por padrão
    paymentForm.value.amount = debtor.total.toFixed(2); 
    isPaymentModalOpen.value = true;
    
    // Garante que temos as contas carregadas
    if (accounts.value.length === 0) fetchAccounts();
};

const openHistoryModal = (debtor) => {
    selectedDebtor.value = debtor;
    isHistoryModalOpen.value = true;
    fetchHistory(debtor.name);
};

const openDeleteModal = (debtor) => {
    debtorToDelete.value = debtor;
    isDeleteModalOpen.value = true;
};

// --- CONFIRMAÇÃO DO PAGAMENTO (CORRIGIDA) ---
const confirmPayment = async () => {
    // 1. Sanitização do Valor (Resolve o problema do parseFloat)
    let rawAmount = String(paymentForm.value.amount).replace(',', '.');
    const amount = parseFloat(rawAmount);

    // Validações
    if (isNaN(amount) || amount <= 0) return alert("Valor inválido.");
    if (!paymentForm.value.accountId) return alert("Selecione a conta de destino.");

    try {
        // Envia payload COMPLETO (nome, valor, método, conta, data)
        await debtService.settleDebt({
            debtor_name: selectedDebtor.value.name,
            amount: amount,
            date: paymentForm.value.date,
            payment_method: paymentForm.value.method,
            account_id: paymentForm.value.accountId
        });

        isPaymentModalOpen.value = false;
        fetchDebts(); // Atualiza a tela
    } catch (error) {
        alert("Erro ao registrar pagamento.");
    }
};

const confirmDelete = async () => {
    if (!debtorToDelete.value) return;
    try {
        await debtService.deleteDebt(debtorToDelete.value.name);
        isDeleteModalOpen.value = false;
        fetchDebts();
    } catch (error) {
        alert("Erro ao apagar registros.");
    }
};

const openWhatsapp = (debtor) => {
    const link = debtService.getWhatsappLink(debtor.name, debtor.total);
    window.open(link, '_blank');
};

const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
const formatDate = (dateStr) => {
    if (!dateStr) return '';
    // Fix para timezone: criar data com T00:00:00 para garantir dia correto
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('pt-BR');
};

onMounted(fetchDebts);
</script>

<template>
  <div class="h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans flex overflow-hidden">
    
    <div class="hidden lg:flex h-full shrink-0 z-10">
        <SidebarDesktop />
    </div>

    <div class="flex-1 flex flex-col h-full relative overflow-hidden">
        
        <header class="px-4 py-4 md:px-8 md:py-6 bg-[var(--bg-surface)] border-b border-[var(--border)] flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
                <button @click="goBack" class="lg:hidden p-2 -ml-2 rounded-full hover:bg-[var(--bg-app)] text-[var(--text-main)]">
                    <ChevronLeft :size="24" />
                </button>
                <div>
                    <h1 class="text-xl font-bold tracking-tight flex items-center gap-2">
                        <Users :size="20" class="text-purple-500" /> Acertos & Cobranças
                    </h1>
                    <p class="text-xs text-[var(--text-muted)] hidden md:block">Gerencie quem te deve e quem você pagou.</p>
                </div>
            </div>
            
            <div class="bg-purple-500/10 px-4 py-2 rounded-xl border border-purple-500/20 flex flex-col items-end">
                <span class="text-[10px] uppercase font-bold text-purple-500 tracking-wider">Total a Receber</span>
                <span class="text-lg font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(summary.total_receivable) }}</span>
            </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 md:p-8 custom-scroll">
            
            <div v-if="isLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div v-for="i in 3" :key="i" class="h-32 bg-[var(--bg-surface)] rounded-2xl animate-pulse border border-[var(--border)]"></div>
            </div>

            <div v-else-if="summary.debtors.length === 0" class="flex flex-col items-center justify-center h-64 text-[var(--text-muted)] opacity-60">
                <div class="w-16 h-16 bg-[var(--bg-surface)] rounded-full flex items-center justify-center mb-4 border border-[var(--border)]">
                    <Check :size="32" class="text-emerald-500" />
                </div>
                <p class="text-lg font-medium">Tudo certo por aqui!</p>
                <p class="text-sm">Ninguém te deve nada no momento.</p>
            </div>

            <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3 content-start">
                <div v-for="debtor in summary.debtors" :key="debtor.name" 
                     class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)] shadow-sm hover:border-purple-500/30 transition-all group relative overflow-hidden">
                    
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-md">
                                {{ debtor.name.charAt(0).toUpperCase() }}
                            </div>
                            <div>
                                <h3 class="font-bold text-lg leading-tight">{{ debtor.name }}</h3>
                                <p class="text-xs text-[var(--text-muted)]">{{ debtor.transaction_count || 'Vários' }} registros</p>
                            </div>
                        </div>
                        <button @click="openWhatsapp(debtor)" class="p-2 rounded-full bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500 hover:text-white transition-all" title="Cobrar no WhatsApp">
                            <MessageCircle :size="18" />
                        </button>
                    </div>

                    <div class="mb-5">
                        <span class="text-[10px] text-[var(--text-muted)] uppercase font-bold">Valor em aberto</span>
                        <p class="text-2xl font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(debtor.total) }}</p>
                    </div>

                    <div class="flex gap-2 mt-auto">
                        <button @click="openPaymentModal(debtor)" class="flex-1 py-2.5 bg-[var(--text-main)] text-[var(--bg-app)] rounded-xl font-bold text-xs hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
                            <Wallet :size="14" /> Receber
                        </button>
                        <button @click="openHistoryModal(debtor)" class="px-3 py-2.5 border border-[var(--border)] rounded-xl hover:bg-[var(--bg-app)] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors" title="Ver Histórico">
                            <History :size="18" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <Teleport to="body">
        <div v-if="isPaymentModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="isPaymentModalOpen = false"></div>
            <div class="bg-[var(--bg-surface)] w-full max-w-sm rounded-3xl p-6 relative z-10 border border-[var(--border)] shadow-2xl animate-in zoom-in-95 duration-200">
                <button @click="isPaymentModalOpen = false" class="absolute top-4 right-4 text-[var(--text-muted)] hover:text-[var(--text-main)]"><X :size="20"/></button>
                
                <h2 class="text-lg font-bold mb-1">Receber de {{ selectedDebtor?.name }}</h2>
                <p class="text-xs text-[var(--text-muted)] mb-4">O valor entrará como saldo na sua conta.</p>

                <div class="bg-[var(--bg-app)] rounded-xl p-4 mb-3 border border-[var(--border)]">
                    <p class="text-[10px] uppercase font-bold text-[var(--text-muted)] mb-1">Valor Recebido</p>
                    <div class="flex items-center gap-2">
                        <span class="text-xl font-bold text-[var(--color-success)]">R$</span>
                        <input v-model="paymentForm.amount" type="number" step="0.01" class="bg-transparent text-2xl font-bold w-full focus:outline-none text-[var(--text-main)] font-numeric" autofocus />
                    </div>
                </div>

                <div class="mb-3">
                    <label class="text-[10px] uppercase font-bold text-[var(--text-muted)] ml-1 block mb-1">Onde entrou o dinheiro?</label>
                    <select v-model="paymentForm.accountId" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-sm rounded-xl p-3 focus:outline-none focus:border-[var(--color-primary)]">
                        <option value="" disabled>Selecione a conta</option>
                        <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
                    </select>
                </div>

                <div class="grid grid-cols-2 gap-3 mb-5">
                    <div>
                        <label class="text-[10px] uppercase font-bold text-[var(--text-muted)] ml-1 block mb-1">Método</label>
                        <select v-model="paymentForm.method" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-sm rounded-xl p-2.5 focus:outline-none">
                            <option value="pix">Pix</option>
                            <option value="dinheiro">Dinheiro</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase font-bold text-[var(--text-muted)] ml-1 block mb-1">Data</label>
                        <input v-model="paymentForm.date" type="date" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-sm rounded-xl p-2.5 focus:outline-none" />
                    </div>
                </div>

                <button @click="confirmPayment" class="w-full py-3 rounded-xl bg-[var(--color-success)] text-white font-bold shadow-lg shadow-emerald-500/20 hover:brightness-110 transition-all">
                    Confirmar Recebimento
                </button>
            </div>
        </div>
    </Teleport>

    <Teleport to="body">
        <div v-if="isHistoryModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="isHistoryModalOpen = false"></div>
            <div class="bg-[var(--bg-surface)] w-full max-w-md rounded-3xl relative z-10 border border-[var(--border)] shadow-2xl flex flex-col max-h-[80vh] animate-in slide-in-from-bottom-4 duration-300">
                
                <div class="p-5 border-b border-[var(--border)] flex justify-between items-center">
                    <div>
                        <h2 class="font-bold text-lg">Histórico: {{ selectedDebtor?.name }}</h2>
                        <p class="text-xs text-[var(--text-muted)]">Extrato de dívidas e pagamentos.</p>
                    </div>
                    <button @click="openDeleteModal(selectedDebtor)" class="p-2 text-rose-500 hover:bg-rose-500/10 rounded-lg transition-colors" title="Apagar tudo">
                        <Trash2 :size="18" />
                    </button>
                </div>

                <div class="flex-1 overflow-y-auto p-4 custom-scroll space-y-3 relative min-h-[200px]">
                    <div v-if="isLoadingHistory" class="absolute inset-0 flex flex-col items-center justify-center bg-[var(--bg-surface)] z-10">
                        <Loader2 class="animate-spin text-[var(--color-primary)] mb-2" :size="32" />
                        <span class="text-xs text-[var(--text-muted)]">Buscando movimentações...</span>
                    </div>

                    <template v-else>
                        <div v-for="item in debtorHistory" :key="item.id" class="flex items-center justify-between p-3 rounded-xl border border-[var(--border)] bg-[var(--bg-app)]/30">
                            <div class="flex items-center gap-3">
                                <div class="p-2 rounded-full" :class="item.type === 'expense' ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'">
                                    <ArrowUpRight v-if="item.type === 'expense'" :size="16" />
                                    <ArrowDownLeft v-else :size="16" />
                                </div>
                                <div>
                                    <p class="text-sm font-bold text-[var(--text-main)]">{{ item.description }}</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">{{ formatDate(item.date) }}</p>
                                </div>
                            </div>
                            <span class="font-bold text-sm font-numeric" :class="item.type === 'expense' ? 'text-rose-500' : 'text-emerald-500'">
                                {{ item.type === 'expense' ? '+' : '-' }} {{ formatCurrency(item.amount) }}
                            </span>
                        </div>
                        <div v-if="debtorHistory.length === 0" class="text-center py-4 text-[var(--text-muted)] text-sm">Nenhum registro encontrado.</div>
                    </template>
                </div>

                <div class="p-4 border-t border-[var(--border)]">
                     <button @click="isHistoryModalOpen = false" class="w-full py-3 rounded-xl border border-[var(--border)] font-bold text-sm hover:bg-[var(--bg-app)]">Fechar</button>
                </div>
            </div>
        </div>
    </Teleport>

    <Teleport to="body">
        <div v-if="isDeleteModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="isDeleteModalOpen = false"></div>
            <div class="bg-[var(--bg-surface)] w-full max-w-xs rounded-3xl p-6 relative z-10 border border-[var(--color-danger)]/30 shadow-2xl animate-in zoom-in-95">
                <div class="flex flex-col items-center text-center">
                    <div class="w-12 h-12 rounded-full bg-[var(--color-danger)]/10 text-[var(--color-danger)] flex items-center justify-center mb-4">
                        <AlertTriangle :size="24" />
                    </div>
                    <h3 class="font-bold text-[var(--text-main)] mb-1">Apagar registros?</h3>
                    <p class="text-xs text-[var(--text-muted)] mb-5">
                        Isso removerá todas as pendências de <b>{{ debtorToDelete?.name }}</b>. O histórico financeiro será preservado, mas a dívida será zerada.
                    </p>
                    <div class="flex gap-3 w-full">
                        <button @click="isDeleteModalOpen = false" class="flex-1 py-2 rounded-xl border border-[var(--border)] text-xs font-bold hover:bg-[var(--bg-app)]">Cancelar</button>
                        <button @click="confirmDelete" class="flex-1 py-2 rounded-xl bg-[var(--color-danger)] text-white text-xs font-bold shadow-lg hover:brightness-110">Apagar</button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>