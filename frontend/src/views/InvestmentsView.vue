<script setup>
import { TrendingUp } from 'lucide-vue-next';
import SidebarDesktop from '../components/SidebarDesktop.vue';
import { useRouter } from 'vue-router';
import { ChevronLeft } from 'lucide-vue-next';

const router = useRouter();
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
                <h1 class="text-lg font-bold tracking-tight">Investimentos</h1>
            </div>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <TrendingUp :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Carteira de Investimentos</h1>
             </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-24 custom-scroll flex items-center justify-center">
            
            <div class="text-center opacity-60 max-w-sm">
                <div class="w-16 h-16 bg-[var(--bg-surface)] rounded-full flex items-center justify-center mx-auto mb-4 border border-[var(--border)] shadow-sm">
                    <TrendingUp :size="32" class="text-[var(--text-muted)]" />
                </div>
                <h2 class="text-lg font-bold text-[var(--text-main)] mb-1">Em breve</h2>
                <p class="text-sm text-[var(--text-muted)]">Estamos construindo um módulo completo para você acompanhar seu patrimônio.</p>
            </div>

        </div>
    </div>
  </div>
</template>