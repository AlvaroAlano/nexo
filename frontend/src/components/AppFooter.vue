<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Home, FileText, CreditCard, Settings } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const navItems = [
  { name: 'Início', icon: Home, path: '/dashboard' },
  { name: 'Extrato', icon: FileText, path: '/transactions', disabled: true },
  { name: 'Cartões', icon: CreditCard, path: '/cards-view', disabled: true }, 
  { name: 'Ajustes', icon: Settings, path: '/settings' },
];

const activeItemIndex = computed(() => {
  const settingsSubPages = ['/cartoes', '/categorias', '/perfil'];
  
  if (settingsSubPages.includes(route.path)) {
    return 3; 
  }

  const index = navItems.findIndex(item => item.path === route.path);
  return index === -1 ? 0 : index;
});

const bubbleStyle = computed(() => {
  const widthPercentage = 100 / navItems.length; 
  const translateX = activeItemIndex.value * 100;

  return {
    width: `${widthPercentage}%`,
    transform: `translateX(${translateX}%)`,
  };
});

const navigateTo = (item) => {
  if (item.disabled) return;
  router.push(item.path);
};
</script>

<template>
  <nav class="fixed bottom-3 left-4 right-4 h-14 lg:hidden
    bg-[var(--bg-surface)]
    border border-[var(--border)]
    rounded-full 
    shadow-[var(--shadow-card)] 
    flex items-center justify-center z-50 p-1 transition-colors duration-300">
    
    <div class="relative w-full h-full flex items-center justify-between overflow-hidden rounded-full">
      
      <div 
        class="absolute top-0 bottom-0 left-0 rounded-full transition-transform duration-500 cubic-bezier z-0"
        :style="bubbleStyle"
      >
        <div class="w-full h-full rounded-full 
          bg-[var(--bg-app)]
          border border-[var(--border)]
          shadow-inner">
        </div>
      </div>

      <button
        v-for="(item, index) in navItems"
        :key="item.path"
        @click="navigateTo(item)"
        class="flex-1 h-full flex flex-col items-center justify-center z-10 gap-0.5 focus:outline-none transition-opacity duration-300"
        :class="{ 
          'cursor-default opacity-40': item.disabled, 
          'cursor-pointer hover:opacity-100': !item.disabled 
        }"
      >
        <component 
          :is="item.icon" 
          :size="20" 
          stroke-width="2.5"
          class="transition-all duration-300"
          :class="index === activeItemIndex 
            ? 'text-[var(--color-primary)] scale-105 drop-shadow-sm' 
            : 'text-[var(--text-muted)]'"
        />
        
        <span 
          class="text-[9px] font-bold transition-colors duration-300 tracking-wide"
          :class="index === activeItemIndex 
            ? 'text-[var(--text-main)]' 
            : 'text-[var(--text-muted)]'"
        >
          {{ item.name }}
        </span>
      </button>

    </div>
  </nav>
</template>

<style scoped>
.cubic-bezier {
  transition-timing-function: cubic-bezier(0.25, 0.8, 0.25, 1);
}
button {
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}
</style>