<script setup>
import { defineAsyncComponent, onMounted } from 'vue';

// Carregamento assíncrono para performance
const DashboardMobile = defineAsyncComponent(() => import('./DashboardMobile.vue'));
const DashboardDesktop = defineAsyncComponent(() => import('./DashboardDesktop.vue'));

onMounted(() => {
  // Garante que a classe dark esteja correta no HTML ao carregar
  const savedTheme = localStorage.getItem('theme');
  const html = document.documentElement;

  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    html.classList.add('dark');
  } else {
    html.classList.remove('dark');
  }
});
</script>

<template>
  <div class="h-screen w-full overflow-hidden bg-[var(--bg-app)] transition-colors duration-300">
    
    <div class="block lg:hidden h-full w-full">
        <DashboardMobile />
    </div>
    
    <div class="hidden lg:block h-full w-full">
        <DashboardDesktop />
    </div>

  </div>
</template>