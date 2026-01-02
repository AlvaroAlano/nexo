<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppFooter from './components/AppFooter.vue';

const route = useRoute();

// Lista de rotas onde o Footer (Menu Mobile) e estruturas globais NÃO devem aparecer
const isAuthRoute = computed(() => ['/', '/login', '/welcome'].includes(route.path));
</script>

<template>
  <div class="min-h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans antialiased">
    
    <router-view />

    <AppFooter v-if="!isAuthRoute" />
    
  </div>
</template>