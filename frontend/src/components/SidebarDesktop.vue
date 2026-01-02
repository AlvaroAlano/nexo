<script setup>
import { ref, onMounted, computed } from 'vue'; 
import { useRouter, useRoute } from 'vue-router';
import { useSettings } from '../composables/useSettings'; // Importando para controlar visibilidade
import { 
  LayoutDashboard, List, CreditCard, Settings, 
  Sun, Moon, PanelLeftClose, PanelLeftOpen,
  Target, Users // Novos ícones importados
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const isDark = ref(true);
const { enableDebts, enableGoals } = useSettings(); // Pegando configurações globais

const isExpanded = ref(localStorage.getItem('sidebar_expanded') === 'true');

const toggleTheme = () => {
  isDark.value = !isDark.value;
  document.documentElement.classList.toggle('dark', isDark.value);
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
};

const toggleSidebar = () => {
    isExpanded.value = !isExpanded.value;
    localStorage.setItem('sidebar_expanded', isExpanded.value);
};

const navigate = (path) => {
    router.push(path);
};

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true;
  } else {
    isDark.value = false;
  }
});

// --- LÓGICA DE GRUPOS ATIVOS ---
const isActive = (path) => route.path === path;

const isSettingsActive = computed(() => {
    // REMOVIDO '/cartoes' daqui para corrigir o bug de duplo destaque
    const settingsPaths = ['/settings', '/categorias', '/perfil']; 
    return settingsPaths.includes(route.path);
});

const isProfileActive = computed(() => {
    return route.path === '/perfil';
});
</script>

<template>
    <aside 
        class="flex flex-col bg-[var(--bg-surface)] border border-[var(--border)] z-20 flex-shrink-0 transition-all duration-300 shadow-2xl ml-4 my-4 rounded-2xl backdrop-blur-xl overflow-visible"
        :class="isExpanded ? 'w-64' : 'w-20'"
    >
        <div class="h-20 flex items-center relative transition-all duration-300" 
             :class="isExpanded ? 'px-6 justify-between' : 'justify-center flex-col gap-2 pt-4'">
            
            <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">
                <div class="w-8 h-8 min-w-[32px] rounded-lg flex items-center justify-center font-bold text-white text-xs shadow-lg transition-transform hover:scale-105" 
                     style="background-color: var(--color-primary); box-shadow: 0 4px 10px rgba(var(--color-primary), 0.3);">
                     N
                </div>
                <div class="flex flex-col transition-opacity duration-200" :class="isExpanded ? 'opacity-100' : 'opacity-0 w-0 hidden'">
                    <span class="font-bold text-sm tracking-widest text-[var(--text-main)]">NEXO</span>
                    <span class="text-[9px] text-[var(--text-muted)]">Finance</span>
                </div>
            </div>

            <button 
                @click="toggleSidebar"
                class="p-1.5 rounded-md text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-main)] transition-colors absolute"
                :class="isExpanded ? 'right-4 top-1/2 -translate-y-1/2' : 'relative mt-2'"
            >
                <PanelLeftClose v-if="isExpanded" :size="18" />
                <PanelLeftOpen v-else :size="18" />
            </button>
        </div>

        <div class="w-full h-px bg-[var(--border)] my-2 opacity-50"></div>
        
        <nav class="flex-1 px-3 py-4 space-y-2 overflow-y-auto custom-scroll overflow-x-hidden">
            
            <div class="relative group">
                <button @click="navigate('/dashboard')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isActive('/dashboard') ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isActive('/dashboard')" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <LayoutDashboard :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Dashboard
                    </span>
                </button>
                <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Dashboard</div>
            </div>

            <div class="relative group">
                <button @click="navigate('/transactions')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isActive('/transactions') ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isActive('/transactions')" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <List :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Transações
                    </span>
                </button>
                <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Transações</div>
            </div>

            <div class="relative group">
                <button @click="navigate('/cartoes')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isActive('/cartoes') ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isActive('/cartoes')" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <CreditCard :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Cartões
                    </span>
                </button>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Cartões</div>
            </div>

            <div v-if="enableDebts" class="relative group animate-in slide-in-from-left-2 duration-300">
                <button @click="navigate('/acertos')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isActive('/acertos') ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isActive('/acertos')" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <Users :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Acertos
                    </span>
                </button>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Acertos</div>
            </div>

            <div v-if="enableGoals" class="relative group animate-in slide-in-from-left-2 duration-300">
                <button @click="navigate('/metas')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isActive('/metas') ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isActive('/metas')" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <Target :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Metas
                    </span>
                </button>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Metas</div>
            </div>

            <div class="relative group">
                <button @click="navigate('/settings')" 
                    class="w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 relative group-hover:bg-[var(--bg-hover)]"
                    :class="[
                        isSettingsActive ? 'bg-[var(--bg-hover)] text-[var(--color-primary)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]',
                        isExpanded ? 'justify-start gap-3' : 'justify-center'
                    ]">
                    <div v-if="isSettingsActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-primary)] rounded-r-full transition-all"></div>
                    <Settings :size="20" class="transition-colors shrink-0" /> 
                    <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                          :class="isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'">
                        Ajustes
                    </span>
                </button>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Ajustes</div>
            </div>
        </nav>

        <div class="p-3 border-t border-[var(--border)] space-y-2 opacity-90">
            <button @click="toggleTheme" 
                class="w-full flex items-center p-2 rounded-xl text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-main)] transition-colors group relative"
                :class="isExpanded ? 'justify-start gap-3' : 'justify-center'">
                <div class="shrink-0 transition-transform group-hover:rotate-12">
                   <Sun v-if="!isDark" :size="20" /> <Moon v-else :size="20" />
                </div>
                <span class="font-medium text-sm whitespace-nowrap transition-all duration-300"
                      :class="isExpanded ? 'opacity-100' : 'opacity-0 w-0 hidden'">
                    {{ isDark ? 'Modo Escuro' : 'Modo Claro' }}
                </span>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)]">Trocar Tema</div>
            </button>

            <div class="flex items-center gap-3 p-2 rounded-xl transition-all cursor-pointer group relative border"
                 :class="[
                    isExpanded ? 'justify-start' : 'justify-center',
                    isProfileActive ? 'bg-[var(--color-primary-light)] border-[var(--color-primary)]' : 'border-transparent hover:bg-[var(--bg-hover)]'
                 ]" 
                 @click="navigate('/perfil')">
                <div class="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-xs shadow-md shrink-0 ring-2 transition-all"
                     style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));"
                     :class="isProfileActive ? 'ring-[var(--color-primary)] ring-offset-2 ring-offset-[var(--bg-surface)]' : 'ring-transparent'">
                    US
                </div>
                <div class="flex flex-col overflow-hidden transition-all duration-300" :class="isExpanded ? 'opacity-100 w-auto' : 'opacity-0 w-0 hidden'">
                    <span class="text-xs font-bold truncate transition-colors" :class="isProfileActive ? 'text-[var(--color-primary)]' : 'text-[var(--text-main)]'">Usuário Nexo</span>
                    <span class="text-[10px] text-[var(--text-muted)] truncate">usuario@exemplo.com</span>
                </div>
                 <div v-if="!isExpanded" class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-2 bg-[var(--bg-surface)] text-[var(--text-main)] text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-[var(--border)] text-left"><p class="font-bold">Usuário Nexo</p></div>
            </div>
        </div>
    </aside>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
</style>