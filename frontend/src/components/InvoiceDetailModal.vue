<script setup>
import { ref, computed } from 'vue';
import { X, CreditCard, Calendar, List, PieChart, ArrowUpRight } from 'lucide-vue-next';

const props = defineProps({
  isOpen: Boolean,
  card: Object,
  month: Number,
  year: Number
});

const emit = defineEmits(['close']);

const activeTab = ref('invoice'); // 'invoice' ou 'limits'

// Helpers
const formatCurrency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit' }).format(date);
};

const transactions = computed(() => props.card?.transactions || []);

// Cálculos de Porcentagem
const limitPercent = computed(() => {
    if (!props.card || !props.card.limit) return 0;
    return Math.min(((props.card.total_debt || 0) / props.card.limit) * 100, 100);
});

const availableLimit = computed(() => {
    return (props.card?.limit || 0) - (props.card?.total_debt || 0);
});
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-[9999] flex items-end sm:items-center justify-center sm:p-4">
        
        <div @click="emit('close')" class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity animate-in fade-in duration-200"></div>
        
        <div class="relative w-full sm:max-w-[420px] bg-[var(--bg-surface)] rounded-t-3xl sm:rounded-3xl border-t sm:border border-[var(--border)] shadow-2xl flex flex-col max-h-[90vh] animate-in slide-in-from-bottom-10 sm:zoom-in-95 duration-200">
            
            <div class="relative overflow-hidden p-6 pb-2">
                <div class="absolute left-0 top-6 bottom-0 w-1.5 rounded-r-full" :style="{ backgroundColor: card?.color || '#333' }"></div>
                
                <div class="flex justify-between items-start pl-4">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <div class="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white shadow-sm"
                                 :style="{ backgroundColor: card?.color || '#333' }">
                                {{ card?.name?.substring(0,1).toUpperCase() }}
                            </div>
                            <span class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">{{ card?.name }}</span>
                        </div>
                        <h2 class="text-2xl font-bold text-[var(--text-main)] font-numeric">
                            {{ formatCurrency(card?.invoice || 0) }}
                        </h2>
                        <p class="text-xs text-[var(--text-muted)] mt-1 flex items-center gap-1">
                            <Calendar :size="12" />
                            Vence dia <span class="text-[var(--text-main)] font-bold">{{ card?.due_day }}</span> de Dezembro
                        </p>
                    </div>
                    <button @click="emit('close')" class="p-2 rounded-full text-[var(--text-muted)] hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                        <X :size="20" />
                    </button>
                </div>

                <div class="flex gap-6 mt-6 border-b border-[var(--border)] pl-4">
                    <button 
                        @click="activeTab = 'invoice'"
                        class="pb-2 text-xs font-bold transition-all relative"
                        :class="activeTab === 'invoice' ? 'text-[var(--text-main)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
                    >
                        Extrato
                        <div v-if="activeTab === 'invoice'" class="absolute bottom-0 left-0 right-0 h-0.5 rounded-t-full" :style="{ backgroundColor: card?.color || 'var(--text-main)' }"></div>
                    </button>
                    <button 
                        @click="activeTab = 'limits'"
                        class="pb-2 text-xs font-bold transition-all relative"
                        :class="activeTab === 'limits' ? 'text-[var(--text-main)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
                    >
                        Limites
                        <div v-if="activeTab === 'limits'" class="absolute bottom-0 left-0 right-0 h-0.5 rounded-t-full" :style="{ backgroundColor: card?.color || 'var(--text-main)' }"></div>
                    </button>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto p-4 custom-scroll bg-[var(--bg-app)]/30 min-h-[300px]">
                
                <div v-if="activeTab === 'invoice'" class="space-y-4">
                    
                    <div v-if="!transactions || transactions.length === 0" class="flex flex-col items-center justify-center py-12 opacity-50">
                        <List :size="40" class="mb-3 text-[var(--text-muted)]" />
                        <p class="text-sm text-[var(--text-muted)]">Nenhuma compra nesta fatura.</p>
                    </div>

                    <div v-else class="space-y-2">
                        <div v-for="(tx, index) in transactions" :key="index" 
                             class="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] shadow-sm">
                            <div class="flex items-center gap-3">
                                <div class="p-2 rounded-full bg-[var(--bg-app)] text-[var(--text-muted)]">
                                    <CreditCard :size="16" />
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-[var(--text-main)]">{{ tx.description }}</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">{{ formatDate(tx.date) }}</p>
                                </div>
                            </div>
                            <span class="text-xs font-bold text-[var(--text-main)]">
                                {{ formatCurrency(tx.amount) }}
                            </span>
                        </div>
                    </div>
                </div>

                <div v-else class="space-y-6 pt-2">
                    
                    <div class="p-5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] shadow-sm relative overflow-hidden">
                        <div class="flex justify-between items-end mb-4 relative z-10">
                            <div>
                                <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Disponível</span>
                                <h3 class="text-2xl font-bold text-[var(--color-success)] font-numeric">{{ formatCurrency(availableLimit) }}</h3>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Usado</span>
                                <p class="text-sm font-bold text-[var(--text-main)]">{{ formatCurrency(card?.total_debt || 0) }}</p>
                            </div>
                        </div>

                        <div class="h-2 w-full bg-[var(--bg-app)] rounded-full overflow-hidden mb-2 border border-[var(--border)]">
                            <div class="h-full rounded-full transition-all duration-1000 ease-out"
                                 :style="{ width: limitPercent + '%', backgroundColor: card?.color || '#6366f1' }">
                            </div>
                        </div>
                        <div class="flex justify-between text-[10px] text-[var(--text-muted)]">
                            <span>0%</span>
                            <span>{{ Math.round(limitPercent) }}% usado</span>
                            <span>100%</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div class="p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] flex flex-col items-center justify-center text-center gap-1">
                            <ArrowUpRight :size="18" class="text-[var(--text-muted)] mb-1" />
                            <span class="text-[10px] text-[var(--text-muted)] uppercase">Limite Total</span>
                            <span class="text-sm font-bold text-[var(--text-main)]">{{ formatCurrency(card?.limit || 0) }}</span>
                        </div>
                        <div class="p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] flex flex-col items-center justify-center text-center gap-1">
                            <PieChart :size="18" class="text-[var(--text-muted)] mb-1" />
                            <span class="text-[10px] text-[var(--text-muted)] uppercase">Fecha Dia</span>
                            <span class="text-sm font-bold text-[var(--text-main)]">{{ card?.closing_day }}</span>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </div>
  </Teleport>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>