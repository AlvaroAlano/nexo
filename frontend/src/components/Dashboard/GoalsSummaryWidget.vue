<script setup>
import { ref, computed, onMounted, onActivated } from 'vue';
import { Target, ChevronRight, Plus } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import QuickDepositModal from '../QuickDepositModal.vue'; 
import goalService from '../../services/goals'; 

const router = useRouter();
const goals = ref([]);
const isDepositModalOpen = ref(false);

const emit = defineEmits(['update']); 

const loadGoals = async () => {
    try {
        const response = await goalService.getAll();
        goals.value = response.data;
    } catch (error) {
        console.error("Erro ao carregar metas", error);
    }
};

onMounted(loadGoals);
onActivated(loadGoals);

const primaryGoal = computed(() => {
    if (!goals.value || goals.value.length === 0) return null;
    return goals.value[0]; 
});

const handleDeposit = async ({ goalId, amount, type }) => {
    try {
        let response;
        if (type === 'withdraw') {
            response = await goalService.withdraw(goalId, amount);
        } else {
            response = await goalService.deposit(goalId, amount);
        }
        
        const index = goals.value.findIndex(g => g.id === goalId);
        if (index !== -1) goals.value[index] = response.data;
        
        isDepositModalOpen.value = false;
        emit('update'); 
        
    } catch (error) {
        if (error.response && error.response.status === 400) {
            alert(error.response.data.detail || "Erro ao realizar operação");
        } else {
            alert("Erro ao realizar operação");
        }
    }
};

const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
const getProgress = (current, target) => target === 0 ? 0 : Math.min((current / target) * 100, 100);
</script>

<template>
  <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] shadow-sm p-4 w-full transition-all hover:border-[var(--color-primary)]/30">
    
    <div class="flex justify-between items-center mb-4">
      <div @click="router.push('/goals')" class="flex items-center gap-2 cursor-pointer group">
        <div class="p-1.5 rounded-lg transition-colors bg-[var(--bg-app)] text-[var(--text-muted)] group-hover:text-[var(--color-primary)]">
             <Target :size="16" class="text-current" />
        </div>
        <span class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider group-hover:text-[var(--color-primary)] transition-colors">
            Objetivo Principal
        </span>
      </div>
      <button @click="router.push('/goals')" class="text-[var(--text-muted)] hover:text-[var(--color-primary)] transition-colors">
        <ChevronRight :size="18" />
      </button>
    </div>

    <div v-if="primaryGoal" class="flex flex-col gap-3">
        <div class="flex justify-between items-end">
            <div>
                <h3 class="font-bold text-[var(--text-main)] text-sm leading-tight mb-0.5">{{ primaryGoal.name }}</h3>
                <p class="text-[10px] text-[var(--text-muted)]">Faltam {{ formatCurrency(primaryGoal.target_amount - primaryGoal.current_amount) }}</p>
            </div>
            <span class="font-bold text-sm" :class="primaryGoal.color ? primaryGoal.color.replace('bg-', 'text-') : 'text-[var(--color-primary)]'">
                {{ Math.round(getProgress(primaryGoal.current_amount, primaryGoal.target_amount)) }}%
            </span>
        </div>
        
        <div class="w-full bg-[var(--bg-app)] h-2 rounded-full overflow-hidden border border-[var(--border)]">
            <div class="h-full rounded-full transition-all duration-1000 shadow-sm"
                 :class="primaryGoal.color ? primaryGoal.color.replace('bg-', 'bg-') : 'bg-[var(--color-primary)]'"
                 :style="{ width: `${getProgress(primaryGoal.current_amount, primaryGoal.target_amount)}%` }">
            </div>
        </div>

        <button @click="isDepositModalOpen = true" 
                class="mt-1 w-full py-2 border border-dashed border-[var(--border)] rounded-lg text-xs font-medium text-[var(--text-muted)] hover:bg-[var(--bg-app)] hover:text-[var(--color-success)] hover:border-[var(--color-success)]/30 transition-all flex items-center justify-center gap-1 active:scale-[0.98]">
            <Plus :size="14" /> Adicionar Depósito
        </button>
    </div>

    <div v-else class="text-center py-4 cursor-pointer" @click="router.push('/goals')">
        <p class="text-xs text-[var(--text-muted)]">Nenhum objetivo definido.</p>
        <p class="text-[10px] text-[var(--color-primary)] font-bold mt-1">Criar agora</p>
    </div>

    <QuickDepositModal 
        :is-open="isDepositModalOpen" 
        :goals="goals" 
        :initial-goal-id="primaryGoal?.id"
        @close="isDepositModalOpen = false"
        @confirm="handleDeposit"
    />

  </div>
</template>