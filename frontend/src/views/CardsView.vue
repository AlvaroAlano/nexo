<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

// Componentes
import SidebarDesktop from '../components/SidebarDesktop.vue';
import NewCardModal from '../components/NewCardModal.vue';

// Ícones
import { 
    ChevronLeft, CreditCard, Plus, Calendar, 
    Trash2, AlertCircle, Edit2 
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

// --- ESTADOS ---
const cards = ref([]);
const isLoading = ref(true);
const isModalOpen = ref(false);
const cardToEdit = ref(null); 

// --- AÇÕES ---
const fetchCards = async () => {
    isLoading.value = true;
    try {
        const response = await api.get('/credit-cards/');
        cards.value = Array.isArray(response.data) ? response.data : (response.data.items || []);
    } catch (error) {
        console.error("Erro ao buscar cartões:", error);
    } finally {
        isLoading.value = false;
    }
};

const openNewCardModal = () => {
    cardToEdit.value = null; 
    isModalOpen.value = true;
};

const openEditCardModal = (card) => {
    cardToEdit.value = card; 
    isModalOpen.value = true;
};

const deleteCard = async (card) => {
    if (!confirm(`Tem certeza que deseja excluir o cartão "${card.name}"? As transações vinculadas podem perder a referência.`)) return;

    try {
        await api.delete(`/credit-cards/${card.id}`);
        cards.value = cards.value.filter(c => c.id !== card.id);
    } catch (error) {
        alert("Erro ao excluir cartão. Tente novamente.");
    }
};

// --- HELPERS VISUAIS ---
const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
};

const getLimitPercentage = (card) => {
    if (!card.limit || card.limit === 0) return 0;
    const used = card.total_debt || card.invoice || 0; 
    return Math.min((used / card.limit) * 100, 100);
};

// Cores da barra de progresso baseadas no uso
const getProgressBarColor = (percentage) => {
    if (percentage > 90) return 'bg-[var(--color-danger)]';
    if (percentage > 70) return 'bg-[var(--color-warning)]';
    return 'bg-[var(--color-success)]';
};

onMounted(() => {
    fetchCards();
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
                <h1 class="text-lg font-bold tracking-tight">Meus Cartões</h1>
            </div>
            <button @click="openNewCardModal" class="p-2 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] active:bg-[var(--color-primary)]/20">
                <Plus :size="20" />
            </button>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <CreditCard :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Gestão de Cartões</h1>
             </div>
             
             <button @click="openNewCardModal" class="flex items-center gap-2 bg-[var(--color-primary)] hover:brightness-110 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-[var(--color-primary)]/20 active:scale-95">
                <Plus :size="16" /> Novo Cartão
             </button>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-32 lg:pb-8 custom-scroll">
            <div class="w-full lg:max-w-4xl space-y-4">
                
                <div v-if="isLoading" class="text-center py-10 text-[var(--text-muted)] animate-pulse">
                    <p class="text-sm">Carregando seus cartões...</p>
                </div>

                <div v-else-if="cards.length === 0" class="p-10 border-2 border-dashed border-[var(--border)] rounded-xl flex flex-col items-center justify-center text-[var(--text-muted)] bg-[var(--bg-surface)]/50">
                    <CreditCard :size="48" class="mb-4 opacity-20" />
                    <p class="mb-4">Nenhum cartão cadastrado.</p>
                    <button @click="openNewCardModal" class="text-[var(--color-primary)] font-bold text-sm hover:underline">
                        Cadastrar o primeiro
                    </button>
                </div>

                <div v-else class="grid grid-cols-1 gap-4">
                    <div v-for="card in cards" :key="card.id" 
                         class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl p-4 md:p-5 flex flex-col md:flex-row gap-5 md:items-center hover:border-[var(--color-primary)]/30 transition-all shadow-sm group relative overflow-hidden">
                        
                        <div class="absolute left-0 top-0 bottom-0 w-1" :style="{ backgroundColor: card.color || '#333' }"></div>

                        <div class="flex items-center gap-4 min-w-[200px]">
                            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-sm shrink-0"
                                 :style="{ backgroundColor: card.color || '#333' }">
                                <CreditCard :size="24" />
                            </div>
                            <div>
                                <h3 class="font-bold text-base text-[var(--text-main)]">{{ card.name }}</h3>
                                <p class="text-xs text-[var(--text-muted)]">Final {{ card.last_digits || '****' }}</p>
                            </div>
                        </div>

                        <div class="flex-1 w-full">
                            <div class="flex justify-between items-end mb-2">
                                <span class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wide">Limite Utilizado</span>
                                <div class="text-right">
                                    <span class="text-sm font-bold text-[var(--text-main)] mr-1">{{ formatCurrency(card.total_debt || 0) }}</span>
                                    <span class="text-xs text-[var(--text-muted)]">de {{ formatCurrency(card.limit) }}</span>
                                </div>
                            </div>
                            <div class="w-full bg-[var(--bg-app)] h-2.5 rounded-full overflow-hidden border border-[var(--border)]">
                                <div class="h-full rounded-full transition-all duration-1000 relative" 
                                     :class="getProgressBarColor(getLimitPercentage(card))"
                                     :style="{ width: getLimitPercentage(card) + '%' }">
                                     <div class="absolute inset-0 bg-white/20"></div>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-center justify-between md:justify-end gap-4 min-w-[220px] pt-3 md:pt-0 border-t md:border-t-0 border-[var(--border)]/50">
                            <div class="flex gap-4">
                                <div class="flex flex-col items-start md:items-end">
                                    <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-0.5 flex items-center gap-1">
                                        <Calendar :size="10" /> Fecha
                                    </span>
                                    <span class="text-sm font-bold text-[var(--text-main)]">{{ card.closing_day }}</span>
                                </div>
                                <div class="flex flex-col items-start md:items-end">
                                    <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase mb-0.5 flex items-center gap-1">
                                        <AlertCircle :size="10" /> Vence
                                    </span>
                                    <span class="text-sm font-bold text-[var(--color-danger)]">{{ card.due_day }}</span>
                                </div>
                            </div>
                            
                            <div class="pl-2 border-l border-[var(--border)] ml-2 flex items-center gap-1">
                                <button @click="openEditCardModal(card)" 
                                        class="p-2 text-[var(--text-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary)]/10 rounded-lg transition-colors"
                                        title="Editar Cartão">
                                    <Edit2 :size="18" />
                                </button>
                                <button @click="deleteCard(card)" 
                                        class="p-2 text-[var(--text-muted)] hover:text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 rounded-lg transition-colors"
                                        title="Excluir Cartão">
                                    <Trash2 :size="18" />
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>

        <NewCardModal 
            :isOpen="isModalOpen" 
            :cardToEdit="cardToEdit"
            @close="isModalOpen = false" 
            @success="fetchCards" 
        />

    </div>
  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>