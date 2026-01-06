<script setup>
import { CheckCircle2 } from 'lucide-vue-next';
</script>

<template>
  <div class="h-full flex flex-col items-center justify-center text-center px-8 relative">
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div class="w-64 h-64 bg-[var(--color-primary)] opacity-10 rounded-full animate-ping [animation-duration:3s]"></div>
    </div>

    <div class="relative w-24 h-24 mb-10">
      <div class="absolute inset-0 border-4 border-[var(--color-primary)] opacity-20 rounded-full"></div>
      <div class="absolute inset-0 border-4 border-[var(--color-primary)] border-t-transparent rounded-full animate-spin"></div>
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-12 h-12 bg-[var(--color-primary)] rounded-full flex items-center justify-center shadow-lg shadow-[var(--color-primary)]/40">
          <span class="text-xl font-bold text-white">N</span>
        </div>
      </div>
    </div>

    <h2 class="text-2xl font-bold mb-3 animate-pulse text-[var(--text-main)]">Preparando o NEXO...</h2>
    <p class="text-[var(--text-muted)] text-base max-w-[200px]">Organizando suas contas e previsões.</p>
    
    <div class="mt-16 flex items-center gap-3 px-5 py-3 bg-[var(--bg-surface)] rounded-full border border-[var(--border)] shadow-sm">
      <CheckCircle2 :size="16" class="text-[var(--color-success)]" />
      <span class="text-xs text-[var(--text-muted)] font-medium">Conexão segura estabelecida</span>
    </div>
  </div>
</template>