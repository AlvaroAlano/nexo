<script setup>
import { ref, watch, computed, nextTick } from 'vue';
import { 
    X, Check, Plus, Target, Plane, Car, Home, Laptop, 
    ShieldCheck, GraduationCap, Gamepad2, Gift, ArrowUp, ArrowDown
} from 'lucide-vue-next';

const props = defineProps({
    isOpen: Boolean,
    goals: { type: Array, default: () => [] },
    initialGoalId: Number
});

const emit = defineEmits(['close', 'confirm']);

const iconMap = { 'target': Target, 'plane': Plane, 'car': Car, 'home': Home, 'laptop': Laptop, 'shield': ShieldCheck, 'study': GraduationCap, 'game': Gamepad2, 'gift': Gift };

const selectedGoalId = ref(null);
const amount = ref('');
const inputRef = ref(null);
const operation = ref('deposit'); 

const presets = [50, 100, 200];

watch(() => props.isOpen, async (newVal) => {
    if (newVal) {
        amount.value = '';
        operation.value = 'deposit';
        if (props.initialGoalId) selectedGoalId.value = props.initialGoalId;
        else if (props.goals.length > 0) selectedGoalId.value = props.goals[0].id;
        await nextTick();
        if(inputRef.value) inputRef.value.focus();
    }
});

// Cores Semânticas
const themeColor = computed(() => operation.value === 'deposit' ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]');
const ringColor = computed(() => operation.value === 'deposit' ? 'ring-[var(--color-success)]' : 'ring-[var(--color-warning)]');
const btnColor = computed(() => operation.value === 'deposit' 
    ? 'bg-[var(--color-success)] hover:brightness-110 shadow-[var(--color-success)]/20' 
    : 'bg-[var(--color-warning)] hover:brightness-110 shadow-[var(--color-warning)]/20');

const handleInput = (event) => {
    let value = event.target.value.replace(/\D/g, '');
    if (!value) { amount.value = ''; return; }
    amount.value = (parseFloat(value) / 100).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
};

const addPreset = (val) => {
    let current = amount.value ? parseFloat(amount.value.replace(/\./g, '').replace(',', '.')) : 0;
    amount.value = (current + val).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    if(inputRef.value) inputRef.value.focus();
};

const confirm = () => {
    if (!amount.value || !selectedGoalId.value) return;
    const valueFloat = parseFloat(amount.value.replace(/\./g, '').replace(',', '.'));
    emit('confirm', { goalId: selectedGoalId.value, amount: valueFloat, type: operation.value });
    amount.value = ''; emit('close');
};
</script>

<template>
    <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/90 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

        <div class="relative w-full max-w-[340px] bg-[var(--bg-surface)] rounded-3xl shadow-2xl border border-[var(--border)] overflow-hidden flex flex-col animate-pop-in">
            
            <button @click="$emit('close')" class="absolute top-4 right-4 p-2 rounded-full text-[var(--text-muted)] hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors z-20">
                <X :size="20" />
            </button>

            <div class="pt-8 pb-2 flex flex-col items-center gap-4">
                <div class="bg-[var(--bg-app)] p-1 rounded-xl flex border border-[var(--border)]">
                    <button @click="operation = 'deposit'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
                        :class="operation === 'deposit' ? 'bg-[var(--color-success)] text-white shadow-md' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                        <ArrowDown :size="14" /> Guardar
                    </button>
                    <button @click="operation = 'withdraw'" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
                        :class="operation === 'withdraw' ? 'bg-[var(--color-warning)] text-white shadow-md' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                        <ArrowUp :size="14" /> Resgatar
                    </button>
                </div>
            </div>

            <div class="px-0 py-4">
                <div class="flex gap-5 overflow-x-auto px-6 scrollbar-hide snap-x justify-start py-4">
                    <button v-for="goal in goals" :key="goal.id" @click="selectedGoalId = goal.id"
                        class="flex flex-col items-center gap-3 group transition-all snap-center min-w-[64px]"
                        :class="selectedGoalId === goal.id ? 'opacity-100 scale-110' : 'opacity-40 hover:opacity-80 scale-95'">
                        <div class="w-14 h-14 rounded-full flex items-center justify-center text-white shadow-lg transition-all border-2 relative"
                             :class="[goal.color, selectedGoalId === goal.id ? `border-[var(--bg-surface)] ring-2 ring-offset-2 ring-offset-[var(--bg-surface)] ${ringColor}` : 'border-transparent']">
                            <component :is="iconMap[goal.icon] || Target" :size="24" />
                            <div v-if="selectedGoalId === goal.id" class="absolute -bottom-1 -right-1 rounded-full p-0.5 border-2 border-[var(--bg-surface)]" 
                                 :class="operation === 'deposit' ? 'bg-[var(--color-success)]' : 'bg-[var(--color-warning)]'">
                                <Check :size="10" stroke-width="4" class="text-white" />
                            </div>
                        </div>
                        <span class="text-[10px] font-bold text-center truncate max-w-[80px] leading-tight transition-colors"
                            :class="selectedGoalId === goal.id ? themeColor : 'text-[var(--text-muted)]'">{{ goal.name }}</span>
                    </button>
                </div>
            </div>

            <div class="px-6 pb-6 flex flex-col items-center">
                <p class="text-xs text-[var(--text-muted)] mb-3">
                    {{ operation === 'deposit' ? 'Quanto você quer guardar?' : 'Quanto deseja retirar?' }}
                </p>
                <div class="relative w-full flex justify-center items-center mb-6">
                    <span class="text-2xl font-bold mr-1 mb-1 transition-colors" :class="[themeColor, !amount ? 'opacity-30' : '']">R$</span>
                    <input ref="inputRef" :value="amount" @input="handleInput" type="tel" placeholder="0,00" 
                        class="w-full bg-transparent text-[var(--text-main)] text-center text-5xl font-bold focus:outline-none placeholder:text-[var(--text-muted)]/20 font-numeric py-1 caret-current" 
                        :class="themeColor" />
                </div>
                
                <div class="flex gap-2 w-full justify-center">
                    <button v-for="val in presets" :key="val" @click="addPreset(val)" 
                        class="px-3 py-1.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border)] text-[10px] font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] active:scale-95 transition-all flex items-center gap-0.5">
                        <Plus :size="10" /> {{ val }}
                    </button>
                </div>
            </div>

            <div class="p-4 bg-[var(--bg-app)] border-t border-[var(--border)]">
                <button @click="confirm" :disabled="!amount"
                    class="w-full py-4 rounded-2xl font-bold text-sm text-white flex items-center justify-center gap-2 transition-all shadow-lg active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="amount ? btnColor : 'bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-muted)]'">
                    <component :is="operation === 'deposit' ? ArrowDown : ArrowUp" v-if="amount" :size="20" stroke-width="3" />
                    {{ operation === 'deposit' ? 'Adicionar à meta' : 'Confirmar Resgate' }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.font-numeric { font-variant-numeric: tabular-nums; }
.animate-pop-in { animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes popIn { from { opacity: 0; transform: scale(0.9) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>