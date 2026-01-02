<script setup>
import { TrendingUp, ChevronRight, PieChart } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] shadow-sm p-4 w-full relative overflow-hidden transition-all hover:border-[var(--color-success)]/30">
    
    <div class="absolute -right-4 -bottom-4 opacity-5 pointer-events-none">
        <TrendingUp :size="100" />
    </div>

    <div class="flex justify-between items-start mb-2 relative z-10">
      <div class="flex items-center gap-2">
        <div class="p-1.5 bg-[var(--color-success)]/10 rounded-lg text-[var(--color-success)]">
          <PieChart :size="16" />
        </div>
        <span class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Investimentos</span>
      </div>
      <button @click="router.push('/investments')" class="text-[var(--text-muted)] hover:text-[var(--color-success)] transition-colors">
        <ChevronRight :size="18" />
      </button>
    </div>

    <div class="relative z-10 mt-3">
        <p class="text-[10px] text-[var(--text-muted)] mb-1">Patrimônio Total</p>
        <div class="flex items-center gap-3">
            <h3 class="text-xl font-bold text-[var(--text-main)] font-numeric">R$ 42.500,00</h3>
            <span class="bg-[var(--color-success)]/10 text-[var(--color-success)] text-[10px] font-bold px-1.5 py-0.5 rounded flex items-center gap-0.5 border border-[var(--color-success)]/20">
                <TrendingUp :size="10" /> +1.2%
            </span>
        </div>
    </div>
  </div>
</template>

<style scoped>
.font-numeric { font-variant-numeric: tabular-nums; }
</style>