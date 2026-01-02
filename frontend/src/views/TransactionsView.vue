<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

// Componentes
import SidebarDesktop from '../components/SidebarDesktop.vue';
import TransactionRow from '../components/TransactionRow.vue';
import TransactionDetailsModal from '../components/TransactionDetailsModal.vue';
import NewTransactionModal from '../components/NewTransactionModal.vue';

// Ícones
import { 
  ChevronLeft, ChevronRight, Search, Plus, 
  ArrowUpCircle, ArrowDownCircle, FileSpreadsheet,
  Filter, ChevronDown, ChevronUp, Tag, CreditCard
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

// --- ESTADO ---
const transactions = ref([]);
const categories = ref([]); // Lista de categorias para o filtro
const isLoading = ref(true);

// Filtros
const rawSearchTerm = ref('');
const debouncedSearchTerm = ref('');
const filterType = ref('all'); // 'all', 'expense', 'income'
const filterCategory = ref(''); // ID da categoria ou ''
const filterPayment = ref(''); // 'credito', 'debito', 'pix' or ''

const currentDate = ref(new Date());
const collapsedDates = ref(new Set()); // Para controlar quais grupos estão fechados

// Modais
const isModalOpen = ref(false);
const isDetailsModalOpen = ref(false);
const selectedTransaction = ref(null);
const transactionToEdit = ref(null);

// --- DEBOUNCE DA BUSCA (Performance) ---
let searchTimeout;
watch(rawSearchTerm, (newVal) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        debouncedSearchTerm.value = newVal;
    }, 300); // Espera 300ms antes de filtrar
});

// --- CÁLCULOS & FORMATADORES ---
const currentMonthLabel = computed(() => {
    const label = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(currentDate.value);
    return label.charAt(0).toUpperCase() + label.slice(1);
});

const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

// --- API ---
const fetchCategories = async () => {
    try {
        const res = await api.get('/categories/');
        categories.value = res.data;
    } catch (error) {
        console.error("Erro ao carregar categorias", error);
    }
};

const fetchTransactions = async () => {
    isLoading.value = true;
    try {
        const month = currentDate.value.getMonth() + 1;
        const year = currentDate.value.getFullYear();
        
        const response = await api.get(`/transactions/?limit=1000&month=${month}&year=${year}`);
        transactions.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar transações:", error);
    } finally {
        isLoading.value = false;
    }
};

const changeMonth = (delta) => {
    const newDate = new Date(currentDate.value);
    newDate.setMonth(newDate.getMonth() + delta);
    currentDate.value = newDate;
    fetchTransactions();
};

// --- LÓGICA DE FILTRAGEM ---
const filteredTransactions = computed(() => {
    return transactions.value.filter(tx => {
        // 1. Texto (Debounced)
        const term = debouncedSearchTerm.value.toLowerCase();
        const matchesSearch = !term || 
                              tx.description.toLowerCase().includes(term) ||
                              (tx.category && tx.category.name.toLowerCase().includes(term)) ||
                              tx.amount.toString().includes(term);
        
        // 2. Tipo
        const matchesType = filterType.value === 'all' 
                            ? true 
                            : (filterType.value === 'income' ? tx.type === 'income' : tx.type === 'expense');

        // 3. Categoria
        const matchesCategory = !filterCategory.value || (tx.category_id === filterCategory.value);

        // 4. Forma de Pagamento
        const matchesPayment = !filterPayment.value || (tx.payment_method === filterPayment.value);

        return matchesSearch && matchesType && matchesCategory && matchesPayment;
    });
});

// --- AGRUPAMENTO (CLUSTERS) ---
const groupedTransactions = computed(() => {
    const groups = {};
    filteredTransactions.value.forEach(tx => {
        const dateKey = tx.date; 
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(tx);
    });

    // Ordena datas (mais recente primeiro)
    const sortedKeys = Object.keys(groups).sort((a, b) => new Date(b) - new Date(a));

    return sortedKeys.map(date => ({
        date,
        label: getRelativeDateLabel(date),
        items: groups[date]
    }));
});

// --- RESUMO INTELIGENTE (Baseado no Filtro) ---
const monthSummary = computed(() => {
    const txs = filteredTransactions.value;
    const income = txs.filter(t => t.type === 'income').reduce((acc, t) => acc + t.amount, 0);
    const expense = txs.filter(t => t.type === 'expense').reduce((acc, t) => acc + t.amount, 0);
    return { income, expense, balance: income - expense, count: txs.length };
});

const getRelativeDateLabel = (dateStr) => {
    const inputDate = new Date(dateStr + 'T00:00:00');
    const today = new Date(); today.setHours(0,0,0,0);
    const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1);

    if (inputDate.getTime() === today.getTime()) return 'Hoje';
    if (inputDate.getTime() === yesterday.getTime()) return 'Ontem';
    return new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long', weekday: 'short' }).format(inputDate);
};

// --- AÇÕES UI ---
const toggleGroup = (date) => {
    if (collapsedDates.value.has(date)) collapsedDates.value.delete(date);
    else collapsedDates.value.add(date);
};

const exportToCSV = () => {
    if (filteredTransactions.value.length === 0) return alert("Nada para exportar");
    const headers = ["Data", "Descrição", "Valor", "Tipo", "Categoria", "Forma Pagamento"];
    const rows = filteredTransactions.value.map(tx => [
        tx.date, `"${tx.description}"`, tx.amount.toFixed(2),
        tx.type === 'income' ? 'Receita' : 'Despesa',
        tx.category?.name || 'Sem categoria', tx.payment_method
    ]);
    const csvContent = [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `extrato_nexo_${currentDate.value.getMonth()+1}.csv`);
    document.body.appendChild(link); link.click(); document.body.removeChild(link);
};

const openDetails = (tx) => { selectedTransaction.value = tx; isDetailsModalOpen.value = true; };
const openEditModal = (tx) => { transactionToEdit.value = tx; isModalOpen.value = true; };
const handleUpdate = () => { fetchTransactions(); isModalOpen.value = false; isDetailsModalOpen.value = false; };
const handleDelete = async (tx) => {
    if(!confirm('Excluir transação?')) return;
    try { await api.delete(`/transactions/${tx.id}`); handleUpdate(); } catch (e) { alert('Erro ao excluir'); }
};

onMounted(() => {
    fetchTransactions();
    fetchCategories();
});
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
                <div class="flex flex-col">
                    <h1 class="text-lg font-bold tracking-tight leading-none">Extrato</h1>
                    <span class="text-[10px] text-[var(--text-muted)]">{{ currentMonthLabel }}</span>
                </div>
            </div>
            <button @click="isModalOpen = true" class="p-2 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] active:bg-[var(--color-primary)]/20">
                <Plus :size="20" />
            </button>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm z-30">
             <div class="flex items-center gap-4">
                <h1 class="text-lg font-bold tracking-tight text-[var(--text-main)]">Extrato & Auditoria</h1>
                
                <div class="flex items-center gap-2 bg-[var(--bg-app)] px-1 py-1 rounded-lg border border-[var(--border)] shadow-inner">
                    <button @click="changeMonth(-1)" class="p-1.5 hover:bg-[var(--bg-surface)] rounded-md hover:text-[var(--color-primary)] transition-colors"><ChevronLeft :size="16"/></button>
                    <span class="text-xs font-bold min-w-[100px] text-center capitalize">{{ currentMonthLabel }}</span>
                    <button @click="changeMonth(1)" class="p-1.5 hover:bg-[var(--bg-surface)] rounded-md hover:text-[var(--color-primary)] transition-colors"><ChevronRight :size="16"/></button>
                </div>
             </div>
             
             <div class="flex items-center gap-3">
                 <button @click="exportToCSV" class="flex items-center gap-2 text-[var(--text-muted)] hover:text-[var(--text-main)] px-3 py-2 rounded-lg text-xs font-bold transition-all border border-transparent hover:border-[var(--border)] hover:bg-[var(--bg-app)]">
                    <FileSpreadsheet :size="16" /> <span class="hidden xl:inline">Exportar CSV</span>
                 </button>
                 <button @click="isModalOpen = true" class="flex items-center gap-2 bg-[var(--color-primary)] hover:brightness-110 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-lg active:scale-95">
                    <Plus :size="16" /> Nova Transação
                 </button>
             </div>
        </header>

        <div class="px-4 lg:px-6 pt-4 pb-0 shrink-0">
            <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl p-4 flex justify-between items-center shadow-sm">
                <div class="flex flex-col">
                    <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Resultado ({{ monthSummary.count }} itens)</span>
                    <div class="flex items-baseline gap-2">
                        <span class="text-lg md:text-xl font-bold font-numeric" :class="monthSummary.balance >= 0 ? 'text-[var(--text-main)]' : 'text-[var(--color-danger)]'">
                            {{ formatCurrency(monthSummary.balance) }}
                        </span>
                    </div>
                </div>
                <div class="flex gap-4 md:gap-8 text-right">
                    <div class="hidden sm:block">
                        <span class="text-[10px] font-bold text-[var(--color-success)] uppercase block">Entradas</span>
                        <span class="text-sm font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(monthSummary.income) }}</span>
                    </div>
                    <div class="hidden sm:block">
                        <span class="text-[10px] font-bold text-[var(--color-danger)] uppercase block">Saídas</span>
                        <span class="text-sm font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(monthSummary.expense) }}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="px-4 lg:px-6 pt-4 pb-2 flex flex-col gap-3 shrink-0">
            <div class="relative w-full group">
                <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-[var(--color-primary)] transition-colors" />
                <input 
                    v-model="rawSearchTerm" 
                    type="text" 
                    placeholder="Buscar por descrição ou valor..." 
                    class="w-full pl-9 pr-4 py-2.5 bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl text-sm focus:outline-none focus:border-[var(--color-primary)] transition-colors placeholder-[var(--text-muted)] shadow-sm"
                >
            </div>
            
            <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide items-center">
                <div class="flex bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] p-1 shrink-0">
                    <button @click="filterType = 'all'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all" :class="filterType === 'all' ? 'bg-[var(--text-main)] text-[var(--bg-surface)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">Todos</button>
                    <button @click="filterType = 'income'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1" :class="filterType === 'income' ? 'bg-[var(--color-success)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--color-success)]'"><ArrowDownCircle :size="12"/> Entradas</button>
                    <button @click="filterType = 'expense'" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1" :class="filterType === 'expense' ? 'bg-[var(--color-danger)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--color-danger)]'"><ArrowUpCircle :size="12"/> Saídas</button>
                </div>

                <div class="w-px h-6 bg-[var(--border)] shrink-0 mx-1"></div>

                <div class="relative shrink-0">
                    <select v-model="filterCategory" class="appearance-none bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-main)] text-xs font-bold rounded-xl pl-8 pr-8 py-2.5 focus:outline-none focus:border-[var(--color-primary)] cursor-pointer">
                        <option value="">Todas Categorias</option>
                        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                    </select>
                    <Tag :size="14" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                    <ChevronDown :size="14" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                </div>

                <div class="relative shrink-0">
                    <select v-model="filterPayment" class="appearance-none bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-main)] text-xs font-bold rounded-xl pl-8 pr-8 py-2.5 focus:outline-none focus:border-[var(--color-primary)] cursor-pointer">
                        <option value="">Todos Pagamentos</option>
                        <option value="credito">Cartão de Crédito</option>
                        <option value="debito">Débito</option>
                        <option value="pix">Pix</option>
                        <option value="dinheiro">Dinheiro</option>
                    </select>
                    <CreditCard :size="14" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                    <ChevronDown :size="14" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                </div>
            </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 custom-scroll">
            
            <div v-if="isLoading" class="space-y-4">
                <div v-for="i in 3" :key="i" class="space-y-2">
                    <div class="h-4 w-20 bg-[var(--bg-surface)] rounded animate-pulse"></div>
                    <div class="h-16 bg-[var(--bg-surface)] rounded-xl animate-pulse border border-[var(--border)]"></div>
                </div>
            </div>

            <div v-else-if="groupedTransactions.length === 0" class="flex flex-col items-center justify-center h-64 text-[var(--text-muted)] opacity-60">
                <div class="w-16 h-16 bg-[var(--bg-surface)] rounded-full flex items-center justify-center mb-3 border border-[var(--border)]">
                    <Search :size="32" />
                </div>
                <p class="text-sm font-medium">Nenhuma transação encontrada.</p>
                <p class="text-xs">Tente ajustar os filtros.</p>
            </div>

            <div v-else class="space-y-6 pb-20">
                <div v-for="group in groupedTransactions" :key="group.date" class="animate-in slide-in-from-bottom-2 duration-500">
                    
                    <button @click="toggleGroup(group.date)" class="w-full flex items-center gap-3 mb-2 px-1 py-2 sticky top-0 z-10 bg-[var(--bg-app)]/95 backdrop-blur-sm group hover:opacity-80 transition-opacity">
                        <div class="w-2 h-2 rounded-full" :class="collapsedDates.has(group.date) ? 'bg-[var(--text-muted)]' : 'bg-[var(--color-primary)]'"></div>
                        <h3 class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider capitalize flex-1 text-left">
                            {{ group.label }}
                        </h3>
                        <div class="bg-[var(--bg-surface)] border border-[var(--border)] px-2 py-0.5 rounded text-[9px] font-bold text-[var(--text-muted)]">
                            {{ collapsedDates.has(group.date) ? `${group.items.length} itens` : 'Ocultar' }}
                        </div>
                    </button>

                    <div v-show="!collapsedDates.has(group.date)" class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm divide-y divide-[var(--border)]/50">
                        <TransactionRow 
                            v-for="tx in group.items" 
                            :key="tx.id" 
                            :transaction="tx" 
                            :showActions="true"
                            @click="openDetails"
                            @edit="openEditModal"
                            @delete="handleDelete"
                        />
                    </div>
                </div>
            </div>
        </div>
    </div>

    <NewTransactionModal :isOpen="isModalOpen" :transactionToEdit="transactionToEdit" @close="isModalOpen = false; transactionToEdit = null" @success="handleUpdate" />
    <TransactionDetailsModal :isOpen="isDetailsModalOpen" :transaction="selectedTransaction" @close="isDetailsModalOpen = false" @deleted="handleUpdate" @edit="openEditModal" @updated="handleUpdate" />

  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>