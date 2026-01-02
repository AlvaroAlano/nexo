<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
    ChevronLeft, Target, Plus, Calendar, 
    TrendingUp, Trash2, GripVertical, Pencil,
    Plane, Car, Home, Laptop, ShieldCheck, GraduationCap, Gamepad2, Gift
} from 'lucide-vue-next';
import draggable from 'vuedraggable'; 

// Importa a Sidebar
import SidebarDesktop from '../components/SidebarDesktop.vue';

import NewGoalModal from '../components/NewGoalModal.vue';
import QuickDepositModal from '../components/QuickDepositModal.vue'; 
import ConfirmModal from '../components/ConfirmModal.vue';
import goalService from '../services/goals'; 

const router = useRouter();

// --- ESTADO ---
const isNewGoalModalOpen = ref(false);
const isDepositModalOpen = ref(false); 
const isDeleteModalOpen = ref(false); 
const isLoading = ref(true); 

const selectedGoalForDeposit = ref(null); 
const goalToEdit = ref(null); 
const goalToDeleteId = ref(null); 

const goals = ref([]);

const iconMap = { 'target': Target, 'plane': Plane, 'car': Car, 'home': Home, 'laptop': Laptop, 'shield': ShieldCheck, 'study': GraduationCap, 'game': Gamepad2, 'gift': Gift };

// --- CARREGAMENTO ---
const fetchGoals = async () => {
    try {
        isLoading.value = true;
        const response = await goalService.getAll();
        goals.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar metas:", error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchGoals);

const onOrderChange = async () => {
    const idList = goals.value.map(g => g.id);
    try {
        await goalService.reorder(idList);
    } catch (error) {
        console.error("Erro ao salvar ordem:", error);
    }
};

// --- CRUD ---
const openCreateModal = () => {
    goalToEdit.value = null;
    isNewGoalModalOpen.value = true;
};

const openEditModal = (goal) => {
    goalToEdit.value = { ...goal };
    isNewGoalModalOpen.value = true;
};

const handleSaveGoal = async (goalData) => {
    try {
        if (goalData.id && goals.value.some(g => g.id === goalData.id)) {
            const response = await goalService.update(goalData.id, goalData);
            const index = goals.value.findIndex(g => g.id === goalData.id);
            goals.value[index] = response.data;
        } else {
            const { id, ...payload } = goalData; 
            const response = await goalService.create(payload);
            goals.value.push(response.data);
        }
        isNewGoalModalOpen.value = false;
    } catch (error) {
        alert("Erro ao salvar meta");
    }
};

const confirmDelete = (id) => {
    goalToDeleteId.value = id;
    isDeleteModalOpen.value = true;
};

const handleDelete = async () => {
    if (goalToDeleteId.value) {
        try {
            await goalService.delete(goalToDeleteId.value);
            goals.value = goals.value.filter(g => g.id !== goalToDeleteId.value);
            isDeleteModalOpen.value = false;
            goalToDeleteId.value = null;
        } catch (error) {
            alert("Erro ao excluir meta");
        }
    }
};

const openDeposit = (goalId) => { selectedGoalForDeposit.value = goalId; isDepositModalOpen.value = true; };

const handleDeposit = async ({ goalId, amount, type }) => {
    try {
        let response;
        if (type === 'withdraw') response = await goalService.withdraw(goalId, amount);
        else response = await goalService.deposit(goalId, amount);
        
        const index = goals.value.findIndex(g => g.id === goalId);
        if (index !== -1) goals.value[index] = response.data;
        isDepositModalOpen.value = false;
        
    } catch (error) {
        if (error.response && error.response.status === 400) alert(error.response.data.detail);
        else alert("Erro ao realizar operação");
    }
};

// --- HELPERS ---
const totalSaved = computed(() => goals.value.reduce((acc, goal) => acc + goal.current_amount, 0));
const totalTarget = computed(() => goals.value.reduce((acc, goal) => acc + goal.target_amount, 0));
const generalProgress = computed(() => totalTarget.value === 0 ? 0 : (totalSaved.value / totalTarget.value) * 100);
const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
const formatDate = (dateString) => { 
    if (!dateString) return 'Sem data'; 
    const date = new Date(dateString); date.setMinutes(date.getMinutes() + date.getTimezoneOffset()); 
    return new Intl.DateTimeFormat('pt-BR', { month: 'short', year: 'numeric' }).format(date); 
};
const getProgress = (current, target) => target === 0 ? 0 : Math.min((current / target) * 100, 100);
const goBack = () => router.back();
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
                <h1 class="text-lg font-bold tracking-tight">Metas e Sonhos</h1>
            </div>
            <button @click="openCreateModal" class="p-2 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] active:bg-[var(--color-primary)]/20">
                <Plus :size="20" />
            </button>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <Target :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Metas e Sonhos</h1>
             </div>
             
             <button @click="openCreateModal" class="flex items-center gap-2 bg-[var(--color-primary)] hover:brightness-110 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-[var(--color-primary)]/20 active:scale-95">
                <Plus :size="16" /> Nova Meta
             </button>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-24 custom-scroll">
            <div class="w-full lg:max-w-5xl space-y-6">

                <div class="relative overflow-hidden rounded-2xl p-6 shadow-lg text-white transition-all duration-500"
                     style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));">
                    <div class="absolute -right-6 -top-6 text-white/10 pointer-events-none"><Target :size="140" /></div>
                    <div class="relative z-10">
                        <p class="text-sm font-medium text-white/90 mb-1 flex items-center gap-2"><TrendingUp :size="16" /> Total Acumulado</p>
                        <h2 class="text-3xl font-bold tracking-tight font-numeric mb-4">{{ formatCurrency(totalSaved) }}</h2>
                        <div class="flex justify-between text-xs text-white/90 mb-1.5 font-bold">
                            <span>Progresso Geral</span>
                            <span>{{ Math.round(generalProgress) }}%</span>
                        </div>
                        <div class="w-full bg-black/20 h-2 rounded-full overflow-hidden">
                            <div class="h-full bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)] transition-all duration-1000" :style="{ width: `${generalProgress}%` }"></div>
                        </div>
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="flex justify-between items-end px-1">
                         <div>
                             <h3 class="text-sm font-bold text-[var(--text-muted)] uppercase tracking-wider">Prioridades</h3>
                             <p class="text-[10px] text-[var(--text-muted)] mt-0.5">Segure e arraste para ordenar.</p>
                         </div>
                    </div>

                    <div v-if="isLoading" class="text-center py-10 text-[var(--text-muted)] animate-pulse">Carregando metas...</div>

                    <draggable 
                        v-else
                        v-model="goals" 
                        item-key="id" 
                        handle=".drag-handle" 
                        animation="200" 
                        ghost-class="ghost-card" 
                        class="space-y-3"
                        @end="onOrderChange"
                    >
                        <template #item="{ element: goal }">
                            <div class="bg-[var(--bg-surface)] rounded-2xl p-4 border border-[var(--border)] shadow-sm relative group flex gap-3 items-start transition-all hover:border-[var(--color-primary)]/30">
                                
                                <div class="drag-handle cursor-grab active:cursor-grabbing p-1 -ml-1 mt-1 text-[var(--text-muted)] opacity-40 hover:opacity-100">
                                    <GripVertical :size="20" />
                                </div>

                                <div class="flex-1 min-w-0">
                                    <div class="flex justify-between items-start mb-3">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-sm transition-colors duration-300 shrink-0" :class="goal.color">
                                                <component :is="iconMap[goal.icon] || Target" :size="18" />
                                            </div>
                                            <div class="min-w-0">
                                                <h4 class="font-bold text-[var(--text-main)] leading-tight truncate">{{ goal.name }}</h4>
                                                <div class="flex items-center gap-1.5 mt-0.5">
                                                    <Calendar :size="12" class="text-[var(--text-muted)]" />
                                                    <span class="text-xs text-[var(--text-muted)]">Alvo: {{ formatDate(goal.deadline) }}</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="flex items-center">
                                            <button @click.stop="openEditModal(goal)" class="text-[var(--text-muted)] hover:text-[var(--color-primary)] p-1.5 transition-colors opacity-60 hover:opacity-100 active:scale-95">
                                                <Pencil :size="16" />
                                            </button>
                                            <button @click.stop="confirmDelete(goal.id)" class="text-[var(--text-muted)] hover:text-[var(--color-danger)] p-1.5 transition-colors opacity-60 hover:opacity-100 active:scale-95">
                                                <Trash2 :size="16" />
                                            </button>
                                        </div>
                                    </div>

                                    <div class="space-y-2">
                                        <div class="flex justify-between items-end">
                                            <span class="text-xs font-medium text-[var(--text-muted)]">Faltam {{ formatCurrency(goal.target_amount - goal.current_amount) }}</span>
                                            <span class="text-sm font-bold text-[var(--text-main)]">{{ Math.round(getProgress(goal.current_amount, goal.target_amount)) }}%</span>
                                        </div>
                                        <div class="w-full bg-[var(--bg-app)] h-2.5 rounded-full overflow-hidden border border-[var(--border)]">
                                            <div class="h-full rounded-full transition-all duration-1000" :class="goal.color.replace('bg-', 'bg-')" :style="{ width: `${getProgress(goal.current_amount, goal.target_amount)}%` }"></div>
                                        </div>
                                    </div>

                                    <button @click.stop="openDeposit(goal.id)" class="mt-4 w-full py-2 bg-[var(--bg-app)] hover:bg-[var(--bg-hover)] border border-[var(--border)] rounded-lg text-xs font-bold text-[var(--color-success)] flex items-center justify-center gap-1 transition-colors active:scale-[0.98]">
                                        <Plus :size="14" /> Adicionar Depósito
                                    </button>
                                </div>
                            </div>
                        </template>
                    </draggable>
                </div>
                
                <div v-if="!isLoading && goals.length === 0" class="flex flex-col items-center justify-center py-20 text-center opacity-60 border-2 border-dashed border-[var(--border)] rounded-2xl">
                    <div class="w-16 h-16 bg-[var(--bg-surface)] rounded-full flex items-center justify-center mb-3 border border-[var(--border)]"><Target :size="32" class="text-[var(--text-muted)]" /></div>
                    <p class="text-sm font-medium text-[var(--text-muted)]">Comece criando sua primeira meta!</p>
                </div>

            </div>
        </div>
    </div>

    <NewGoalModal 
        :is-open="isNewGoalModalOpen" 
        :goal-to-edit="goalToEdit"
        @close="isNewGoalModalOpen = false" 
        @save="handleSaveGoal" 
    />
    
    <QuickDepositModal 
        :is-open="isDepositModalOpen" 
        :goals="goals"
        :initial-goal-id="selectedGoalForDeposit"
        @close="isDepositModalOpen = false"
        @confirm="handleDeposit"
    />

    <ConfirmModal 
        :is-open="isDeleteModalOpen"
        title="Excluir Meta?"
        description="Você vai perder todo o histórico de progresso deste objetivo. Essa ação não pode ser desfeita."
        confirm-text="Sim, excluir"
        :is-danger="true"
        @close="isDeleteModalOpen = false"
        @confirm="handleDelete"
    />

  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.ghost-card { opacity: 0.5; background: var(--bg-hover); border: 1px dashed var(--text-muted); }
</style>