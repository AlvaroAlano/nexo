<script setup>
import { ref, watch, computed } from 'vue';
import { 
    X, Check, Target, Plane, Car, Home, Laptop, 
    ShieldCheck, GraduationCap, Gamepad2, Gift 
} from 'lucide-vue-next';

const props = defineProps({
    isOpen: Boolean,
    goalToEdit: Object
});

const emit = defineEmits(['close', 'save']);

const icons = [
    { name: 'target', component: Target }, { name: 'plane', component: Plane },
    { name: 'car', component: Car }, { name: 'home', component: Home },
    { name: 'laptop', component: Laptop }, { name: 'shield', component: ShieldCheck },
    { name: 'study', component: GraduationCap }, { name: 'game', component: Gamepad2 },
    { name: 'gift', component: Gift },
];

// Cores disponíveis para a META (podem ser fixas pois são "etiquetas")
const colors = [
    { name: 'Azul', value: 'bg-blue-500' }, { name: 'Roxo', value: 'bg-purple-500' },
    { name: 'Verde', value: 'bg-emerald-500' }, { name: 'Rosa', value: 'bg-rose-500' },
    { name: 'Laranja', value: 'bg-amber-500' }, { name: 'Cinza', value: 'bg-slate-500' },
];

const form = ref({ id: null, name: '', target_amount: '', current_amount: '', deadline: '', color: 'bg-blue-500', icon: 'target' });

const modalTitle = computed(() => props.goalToEdit ? 'Editar Meta' : 'Nova Meta');
const buttonText = computed(() => props.goalToEdit ? 'Salvar Alterações' : 'Criar Meta');

const formatCurrencyInput = (value) => {
    if (!value && value !== 0) return '';
    let numeric = String(value).replace(/\D/g, '');
    if (!numeric) return '';
    return (parseFloat(numeric) / 100).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        if (props.goalToEdit) {
            form.value = {
                ...props.goalToEdit,
                target_amount: formatCurrencyInput(props.goalToEdit.target_amount.toFixed(2)),
                current_amount: formatCurrencyInput(props.goalToEdit.current_amount.toFixed(2))
            };
        } else { resetForm(); }
    }
});

const handleInput = (field, event) => { form.value[field] = formatCurrencyInput(event.target.value); };

const save = () => {
    if (!form.value.name || !form.value.target_amount) return;
    const parseAmount = (str) => str ? parseFloat(String(str).replace(/\./g, '').replace(',', '.')) : 0;
    emit('save', {
        ...form.value,
        id: form.value.id || Date.now(), 
        target_amount: parseAmount(form.value.target_amount),
        current_amount: parseAmount(form.value.current_amount),
        deadline: form.value.deadline ? form.value.deadline : null 
    });
    if (!props.goalToEdit) resetForm(); 
    emit('close');
};

const resetForm = () => { form.value = { id: null, name: '', target_amount: '', current_amount: '', deadline: '', color: 'bg-blue-500', icon: 'target' }; };
</script>

<template>
    <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

        <div class="relative w-full max-w-[340px] bg-[var(--bg-surface)] rounded-3xl shadow-2xl border border-[var(--border)] overflow-hidden flex flex-col animate-pop-in max-h-[90vh]">
            
            <div class="px-5 py-4 border-b border-[var(--border)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
                <h3 class="font-bold text-base text-[var(--text-main)]">{{ modalTitle }}</h3>
                <button @click="$emit('close')" class="p-1 -mr-2 rounded-full hover:bg-[var(--bg-surface)] text-[var(--text-muted)] transition-colors"><X :size="20" /></button>
            </div>

            <div class="p-5 space-y-5 overflow-y-auto custom-scroll">
                
                <div class="space-y-1.5">
                    <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Nome da Meta</label>
                    <input v-model="form.name" type="text" placeholder="Ex: Viagem, Notebook..." class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-[var(--text-main)] rounded-xl py-3 px-4 focus:outline-none focus:border-[var(--color-primary)] transition-all font-medium text-sm placeholder-[var(--text-muted)]" autofocus />
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1.5">
                        <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Valor Alvo</label>
                        <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] font-bold text-xs">R$</span>
                            <input :value="form.target_amount" @input="handleInput('target_amount', $event)" type="tel" placeholder="0,00" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-[var(--text-main)] rounded-xl py-3 pl-9 pr-3 focus:outline-none focus:border-[var(--color-primary)] transition-all font-numeric font-bold text-sm" />
                        </div>
                    </div>
                    <div class="space-y-1.5">
                        <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Prazo</label>
                        <input v-model="form.deadline" type="date" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-[var(--text-main)] rounded-xl py-3 px-3 focus:outline-none focus:border-[var(--color-primary)] transition-all text-sm font-medium icon-invert" />
                    </div>
                </div>

                <div class="space-y-1.5 pt-2 border-t border-[var(--border)] border-dashed mt-2">
                    <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">{{ goalToEdit ? 'Ajustar Saldo Atual' : 'Já tem algo guardado?' }}</label>
                    <div class="relative">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-success)] font-bold text-xs">R$</span>
                        <input :value="form.current_amount" @input="handleInput('current_amount', $event)" type="tel" placeholder="0,00" class="w-full bg-[var(--bg-app)] border border-[var(--border)] text-[var(--color-success)] rounded-xl py-3 pl-9 pr-3 focus:outline-none focus:border-[var(--color-success)] ring-1 ring-transparent focus:ring-[var(--color-success)]/20 transition-all font-numeric font-bold text-sm" />
                    </div>
                </div>

                <div class="pt-2">
                    <label class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1 mb-2 block">Personalização</label>
                    
                    <div class="space-y-3">
                        <div class="grid grid-cols-5 gap-2">
                            <button v-for="item in icons" :key="item.name" @click="form.icon = item.name"
                                class="aspect-square rounded-xl flex items-center justify-center transition-all border border-[var(--border)] hover:bg-[var(--bg-hover)]"
                                :class="form.icon === item.name ? 'bg-[var(--color-primary)]/10 text-[var(--color-primary)] border-[var(--color-primary)]/50 ring-2 ring-[var(--color-primary)]/20' : 'text-[var(--text-muted)] bg-[var(--bg-app)]'">
                                <component :is="item.component" :size="20" />
                            </button>
                        </div>

                        <div class="flex flex-wrap gap-3 justify-center bg-[var(--bg-app)] p-3 rounded-xl border border-[var(--border)]">
                            <button v-for="color in colors" :key="color.name" @click="form.color = color.value"
                                class="w-8 h-8 rounded-full flex items-center justify-center transition-all border-2"
                                :class="[color.value, form.color === color.value ? 'border-[var(--bg-surface)] scale-110 shadow-lg ring-2 ring-[var(--text-main)]' : 'border-transparent opacity-40 hover:opacity-100']">
                                <Check v-if="form.color === color.value" :size="14" class="text-white" stroke-width="4" />
                            </button>
                        </div>
                    </div>
                </div>

            </div>

            <div class="p-4 border-t border-[var(--border)] bg-[var(--bg-app)] flex gap-3 shrink-0">
                <button @click="$emit('close')" class="flex-1 py-3 rounded-xl font-bold text-xs text-[var(--text-muted)] hover:bg-[var(--bg-surface)] transition-colors">Cancelar</button>
                <button @click="save" class="flex-1 py-3 rounded-xl font-bold text-xs text-white shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2" :class="form.color.replace('text-', 'bg-')">
                    <Check :size="16" stroke-width="3" /> {{ buttonText }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.animate-pop-in { animation: popIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes popIn { from { transform: scale(0.95) translateY(10px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
.dark .icon-invert { color-scheme: dark; }
</style>