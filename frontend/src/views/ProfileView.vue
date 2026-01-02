<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; 
import SidebarDesktop from '../components/SidebarDesktop.vue'; 
import { 
    ChevronLeft, User, Camera, Mail, Phone, Lock, 
    Shield, Bell, Save, CheckCircle 
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

// Estado do Formulário
const isLoading = ref(false);
const showSuccess = ref(false);

const userData = ref({
    name: 'Usuário Nexo',
    email: 'usuario@exemplo.com',
    phone: '(11) 99999-0000',
    notifications: true,
    twoFactor: false
});

// Simulação de Salvar
const handleSave = () => {
    isLoading.value = true;
    
    // Simula delay de API
    setTimeout(() => {
        isLoading.value = false;
        showSuccess.value = true;
        
        // Esconde msg de sucesso após 3s
        setTimeout(() => showSuccess.value = false, 3000);
    }, 1500);
};
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
            <h1 class="text-lg font-bold tracking-tight">Meu Perfil</h1>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <User :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Meu Perfil</h1>
             </div>
             
             <div v-if="showSuccess" class="flex items-center gap-2 text-[var(--color-success)] text-sm font-bold animate-pulse">
                <CheckCircle :size="16" />
                Salvo com sucesso!
             </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-32 lg:pb-8 custom-scroll">
            
            <div class="w-full lg:max-w-4xl space-y-6">

                <div class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6 flex flex-col md:flex-row items-center gap-6 relative overflow-hidden transition-all hover:border-[var(--color-primary)]/30">
                    <div class="absolute top-0 left-0 w-full h-24 bg-gradient-to-r from-[var(--color-primary)]/10 to-transparent z-0 opacity-50"></div>
                    
                    <div class="relative z-10 group cursor-pointer">
                        <div class="w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-3xl shadow-lg ring-4 ring-[var(--bg-surface)]"
                             style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));">
                            US
                        </div>
                        <div class="absolute bottom-0 right-0 p-2 bg-[var(--bg-surface)] border border-[var(--border)] rounded-full text-[var(--text-main)] shadow-sm group-hover:scale-110 transition-transform">
                            <Camera :size="16" />
                        </div>
                    </div>

                    <div class="text-center md:text-left z-10 flex-1">
                        <h2 class="text-xl font-bold text-[var(--text-main)]">{{ userData.name }}</h2>
                        <p class="text-sm text-[var(--text-muted)]">Membro desde Dez 2025</p>
                        <div class="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-success)]/10 text-[var(--color-success)] text-xs font-bold border border-[var(--color-success)]/20">
                            <Shield :size="12" /> Conta Verificada
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <div class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6 space-y-4 shadow-sm">
                        <h3 class="font-bold text-[var(--text-main)] flex items-center gap-2 text-sm uppercase tracking-wider opacity-70 mb-2">
                            <User :size="16" /> Dados Pessoais
                        </h3>

                        <div class="space-y-1">
                            <label class="text-xs font-bold text-[var(--text-muted)] ml-1">Nome Completo</label>
                            <input v-model="userData.name" type="text" class="w-full bg-[var(--bg-app)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-primary)] transition-colors" />
                        </div>

                        <div class="space-y-1">
                            <label class="text-xs font-bold text-[var(--text-muted)] ml-1">E-mail</label>
                            <div class="relative">
                                <Mail :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                                <input v-model="userData.email" type="email" class="w-full bg-[var(--bg-app)] border border-[var(--border)] rounded-xl pl-10 pr-4 py-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-primary)] transition-colors" />
                            </div>
                        </div>

                         <div class="space-y-1">
                            <label class="text-xs font-bold text-[var(--text-muted)] ml-1">Telefone / Celular</label>
                            <div class="relative">
                                <Phone :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                                <input v-model="userData.phone" type="tel" class="w-full bg-[var(--bg-app)] border border-[var(--border)] rounded-xl pl-10 pr-4 py-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-primary)] transition-colors" />
                            </div>
                        </div>
                    </div>

                    <div class="space-y-6">
                        <div class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6 space-y-4 shadow-sm">
                            <h3 class="font-bold text-[var(--text-main)] flex items-center gap-2 text-sm uppercase tracking-wider opacity-70 mb-2">
                                <Lock :size="16" /> Segurança
                            </h3>

                            <button class="w-full flex items-center justify-between p-3 rounded-xl border border-[var(--border)] hover:bg-[var(--bg-app)] transition-colors group">
                                <span class="text-sm font-medium">Alterar Senha</span>
                                <span class="text-xs text-[var(--text-muted)] group-hover:text-[var(--color-primary)] transition-colors">Atualizar ></span>
                            </button>

                            <div class="flex items-center justify-between p-1">
                                <div class="flex-1 pr-4">
                                    <p class="text-sm font-medium">Autenticação em 2 Etapas</p>
                                    <p class="text-xs text-[var(--text-muted)]">Mais segurança para sua conta</p>
                                </div>
                                <button @click="userData.twoFactor = !userData.twoFactor" class="relative w-10 h-5 rounded-full transition-colors duration-200 focus:outline-none"
                                    :class="userData.twoFactor ? 'bg-[var(--color-primary)]' : 'bg-[var(--border)]'">
                                    <span class="block w-3.5 h-3.5 bg-white rounded-full shadow transform transition-transform duration-200"
                                        :class="userData.twoFactor ? 'translate-x-5' : 'translate-x-0.5 mt-[3px]'"></span>
                                </button>
                            </div>
                        </div>

                         <div class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] p-6 space-y-4 shadow-sm">
                            <h3 class="font-bold text-[var(--text-main)] flex items-center gap-2 text-sm uppercase tracking-wider opacity-70 mb-2">
                                <Bell :size="16" /> Preferências
                            </h3>

                            <div class="flex items-center justify-between p-1">
                                <div class="flex-1 pr-4">
                                    <p class="text-sm font-medium">Notificações por E-mail</p>
                                    <p class="text-xs text-[var(--text-muted)]">Resumos semanais e alertas</p>
                                </div>
                                <button @click="userData.notifications = !userData.notifications" class="relative w-10 h-5 rounded-full transition-colors duration-200 focus:outline-none"
                                    :class="userData.notifications ? 'bg-[var(--color-success)]' : 'bg-[var(--border)]'">
                                    <span class="block w-3.5 h-3.5 bg-white rounded-full shadow transform transition-transform duration-200"
                                        :class="userData.notifications ? 'translate-x-5' : 'translate-x-0.5 mt-[3px]'"></span>
                                </button>
                            </div>
                        </div>
                    </div>

                </div>

                <div class="flex justify-end pt-4 pb-12">
                    <button 
                        @click="handleSave"
                        :disabled="isLoading"
                        class="flex items-center gap-2 text-white px-8 py-3 rounded-xl font-bold shadow-lg transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed hover:brightness-110"
                        style="background-color: var(--color-primary); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);"
                    >
                        <span v-if="isLoading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                        <Save v-else :size="18" />
                        {{ isLoading ? 'Salvando...' : 'Salvar Alterações' }}
                    </button>
                </div>

            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 3px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>