<script setup>
import { AlertTriangle, X } from 'lucide-vue-next';

defineProps({
    isOpen: Boolean,
    title: String,
    description: String,
    confirmText: { type: String, default: 'Confirmar' },
    cancelText: { type: String, default: 'Cancelar' },
    isDanger: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'confirm']);
</script>

<template>
    <div v-if="isOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/90 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

        <div class="relative w-full max-w-xs bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-2xl overflow-hidden animate-pop-in">
            
            <div class="p-6 flex flex-col items-center text-center">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                     :class="isDanger ? 'bg-[var(--color-danger)]/10 text-[var(--color-danger)]' : 'bg-[var(--color-primary)]/10 text-[var(--color-primary)]'">
                    <AlertTriangle :size="24" stroke-width="2.5" />
                </div>

                <h3 class="text-base font-bold text-[var(--text-main)] mb-2">{{ title }}</h3>
                <p class="text-xs text-[var(--text-muted)] leading-relaxed">{{ description }}</p>
            </div>

            <div class="grid grid-cols-2 border-t border-[var(--border)] divide-x divide-[var(--border)]">
                <button @click="$emit('close')" class="py-3.5 text-xs font-bold text-[var(--text-muted)] hover:bg-[var(--bg-app)] transition-colors">
                    {{ cancelText }}
                </button>
                <button @click="$emit('confirm')" 
                        class="py-3.5 text-xs font-bold transition-colors hover:bg-[var(--bg-app)]"
                        :class="isDanger ? 'text-[var(--color-danger)]' : 'text-[var(--color-primary)]'">
                    {{ confirmText }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.animate-pop-in { animation: popIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes popIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>