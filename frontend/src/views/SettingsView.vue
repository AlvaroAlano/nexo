<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 
import SidebarDesktop from '../components/SidebarDesktop.vue'; 
import { useSettings } from '../composables/useSettings'; 

import { 
  ChevronLeft, Moon, Sun, Monitor, CreditCard, 
  Target, TrendingUp, Tag, User, ChevronRight, LogOut, Settings as SettingsIcon
} from 'lucide-vue-next';

const router = useRouter();
const { enableDebts, enableGoals, enableInvestments } = useSettings(); 

const themeMode = ref('dark'); 

const goBack = () => router.back();
const navigateTo = (routePath) => router.push(routePath);

const handleLogout = () => {
    localStorage.removeItem('token'); 
    localStorage.removeItem('user');
    router.push('/login');
};

const setTheme = (mode) => {
    themeMode.value = mode;
    localStorage.setItem('theme', mode);
    
    const html = document.documentElement;
    html.classList.remove('dark');

    if (mode === 'dark') {
        html.classList.add('dark');
    } else if (mode === 'system') {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            html.classList.add('dark');
        }
    }
};

onMounted(() => {
    const savedTheme = localStorage.getItem('theme') || 'system';
    setTheme(savedTheme);
});
</script>

<template>
  <div class="h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans transition-colors duration-300 flex overflow-hidden relative">
    
    <div class="hidden lg:flex h-full shrink-0 z-10">
        <SidebarDesktop />
    </div>

    <div class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
        
        <div class="lg:hidden px-4 py-4 flex items-center gap-3 bg-[var(--bg-surface)] border-b border-[var(--border)] sticky top-0 z-20 shadow-sm shrink-0">
            <button @click="goBack" class="p-2 -ml-2 rounded-full hover:bg-[var(--bg-app)] transition-colors active:scale-95 text-[var(--text-main)]">
                <ChevronLeft :size="22" />
            </button>
            <h1 class="text-lg font-bold tracking-tight">Configurações</h1>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <SettingsIcon :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Ajustes do Sistema</h1>
             </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-32 lg:pb-8 custom-scroll">
            <div class="w-full lg:max-w-4xl space-y-6">

                <section class="space-y-2">
                    <h2 class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Perfil</h2>
                    <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] overflow-hidden active:scale-[0.99] transition-transform" @click="router.push('/perfil')">
                        <div class="p-3 flex items-center gap-3 hover:bg-[var(--bg-hover)] transition-colors cursor-pointer">
                            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md"
                                 style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));">
                                US
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-bold text-[var(--text-main)] truncate">Usuário Nexo</p>
                                <p class="text-xs text-[var(--text-muted)] truncate">usuario@exemplo.com</p>
                            </div>
                            <ChevronRight :size="16" class="text-[var(--text-muted)]" />
                        </div>
                    </div>
                </section>

                <section class="space-y-2">
                    <h2 class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Aparência</h2>
                    <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] overflow-hidden">
                        <div class="p-3.5 flex items-center justify-between hover:bg-[var(--bg-hover)] transition-colors">
                            <div class="flex items-center gap-3">
                                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                                    <Sun :size="16" />
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-[var(--text-main)]">Tema do App</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">Visual claro ou escuro</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center gap-1 bg-[var(--bg-app)] p-1 rounded-lg border border-[var(--border)]">
                                <button @click="setTheme('light')" 
                                    class="p-1.5 rounded-md transition-all flex items-center justify-center"
                                    :class="themeMode === 'light' ? 'bg-[var(--bg-surface)] text-[var(--color-warning)] shadow-sm border border-[var(--border)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
                                    title="Claro">
                                    <Sun :size="16" />
                                </button>
                                
                                <button @click="setTheme('dark')" 
                                    class="p-1.5 rounded-md transition-all flex items-center justify-center"
                                    :class="themeMode === 'dark' ? 'bg-[var(--bg-surface)] text-[var(--color-primary)] shadow-sm border border-[var(--border)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
                                    title="Escuro">
                                    <Moon :size="16" />
                                </button>
                                
                                <button @click="setTheme('system')" 
                                    class="p-1.5 rounded-md transition-all flex items-center justify-center"
                                    :class="themeMode === 'system' ? 'bg-[var(--bg-surface)] text-[var(--text-main)] shadow-sm border border-[var(--border)]' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
                                    title="Sistema">
                                    <Monitor :size="16" />
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                <section class="space-y-2">
                    <h2 class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Gestão</h2>
                    <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] overflow-hidden divide-y divide-[var(--border)]">
                        <div @click="navigateTo('/categorias')" class="p-3.5 flex items-center gap-3 hover:bg-[var(--bg-hover)] transition-colors cursor-pointer active:bg-[var(--bg-hover)]">
                            <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]"><Tag :size="16" /></div>
                            <div class="flex-1">
                                <p class="text-xs font-bold text-[var(--text-main)]">Categorias</p>
                                <p class="text-[10px] text-[var(--text-muted)]">Criar e organizar</p>
                            </div>
                            <ChevronRight :size="16" class="text-[var(--text-muted)]" />
                        </div>
                        <div @click="navigateTo('/cartoes')" class="p-3.5 flex items-center gap-3 hover:bg-[var(--bg-hover)] transition-colors cursor-pointer active:bg-[var(--bg-hover)]">
                            <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]"><CreditCard :size="16" /></div>
                            <div class="flex-1">
                                <p class="text-xs font-bold text-[var(--text-main)]">Cartões</p>
                                <p class="text-[10px] text-[var(--text-muted)]">Limites e vencimentos</p>
                            </div>
                            <ChevronRight :size="16" class="text-[var(--text-muted)]" />
                        </div>
                    </div>
                </section>

                <section class="space-y-2">
                    <h2 class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider ml-1">Módulos</h2>
                    <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] overflow-hidden divide-y divide-[var(--border)]">
                        
                        <div class="p-3.5 flex items-center justify-between hover:bg-[var(--bg-hover)] transition-colors">
                            <div class="flex items-center gap-3">
                                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]"><User :size="16" /></div>
                                <div>
                                    <p class="text-xs font-bold text-[var(--text-main)]">Acertos (Devedores)</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">Marcar quem comprou</p>
                                </div>
                            </div>
                            <button @click="enableDebts = !enableDebts" class="relative w-10 h-5 rounded-full transition-colors duration-200 focus:outline-none"
                                :class="enableDebts ? 'bg-[var(--color-success)]' : 'bg-[var(--border)]'">
                                <span class="block w-3.5 h-3.5 bg-white rounded-full shadow transform transition-transform duration-200"
                                    :class="enableDebts ? 'translate-x-5' : 'translate-x-0.5 mt-[3px]'"></span>
                            </button>
                        </div>

                        <div class="p-3.5 flex items-center justify-between hover:bg-[var(--bg-hover)] transition-colors">
                            <div class="flex items-center gap-3">
                                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]"><Target :size="16" /></div>
                                <div>
                                    <p class="text-xs font-bold text-[var(--text-main)]">Metas e Objetivos</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">Notebook, Viagem...</p>
                                </div>
                            </div>
                            <button @click="enableGoals = !enableGoals" class="relative w-10 h-5 rounded-full transition-colors duration-200 focus:outline-none"
                                :class="enableGoals ? 'bg-[var(--color-success)]' : 'bg-[var(--border)]'">
                                <span class="block w-3.5 h-3.5 bg-white rounded-full shadow transform transition-transform duration-200"
                                    :class="enableGoals ? 'translate-x-5' : 'translate-x-0.5 mt-[3px]'"></span>
                            </button>
                        </div>
                        
                        <div class="p-3.5 flex items-center justify-between hover:bg-[var(--bg-hover)] transition-colors">
                            <div class="flex items-center gap-3">
                                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]"><TrendingUp :size="16" /></div>
                                <div>
                                    <p class="text-xs font-bold text-[var(--text-main)]">Investimentos</p>
                                    <p class="text-[10px] text-[var(--text-muted)]">Renda fixa, ações</p>
                                </div>
                            </div>
                            <button @click="enableInvestments = !enableInvestments" class="relative w-10 h-5 rounded-full transition-colors duration-200 focus:outline-none"
                                :class="enableInvestments ? 'bg-[var(--color-success)]' : 'bg-[var(--border)]'">
                                <span class="block w-3.5 h-3.5 bg-white rounded-full shadow transform transition-transform duration-200"
                                    :class="enableInvestments ? 'translate-x-5' : 'translate-x-0.5 mt-[3px]'"></span>
                            </button>
                        </div>
                    </div>
                </section>

                <button @click="handleLogout" 
                        class="w-full py-3.5 rounded-xl font-bold text-xs active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4 text-[var(--color-danger)] border border-[var(--color-danger)]/20 hover:bg-[var(--color-danger)]/10 bg-[var(--color-danger)]/5">
                    <LogOut :size="16" /> Sair da Conta
                </button>
                
                <p class="text-center text-[10px] text-[var(--text-muted)] opacity-40 pb-4">Versão 2.1.0 (Build Dez/25)</p>

            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>