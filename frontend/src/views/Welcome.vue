<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useDashboardStore } from '../stores/dashboard';
import api from '../services/api';
import { Zap } from 'lucide-vue-next';

// Importando os novos componentes
import AuthIntro from '../components/auth/AuthIntro.vue';
import AuthForm from '../components/auth/AuthForm.vue';
import AuthLoading from '../components/auth/AuthLoading.vue';

const router = useRouter();
const authStore = useAuthStore();
const dashboardStore = useDashboardStore();

const isDev = import.meta.env.DEV; 

const currentStep = ref('intro'); // 'intro' | 'login' | 'register' | 'loading'
const isLoading = ref(false);
const errorMessage = ref('');

// Estado do formulário
const email = ref('');
const password = ref('');
const fullName = ref('');

onMounted(async () => {
  // --- CORREÇÃO DO FEEDBACK DO GPT (PONTO 6) ---
  if (authStore.token) {
    currentStep.value = 'loading';
    try {
        // Tenta carregar. Se o token estiver expirado, vai dar erro aqui.
        await handlePreLoadAndEnter();
    } catch (e) {
        // Se falhou (token inválido), limpamos tudo e mandamos login de novo.
        // Isso evita o loop infinito que o GPT alertou!
        console.warn("Token expirado ou inválido. Reiniciando login.");
        authStore.logout(); 
        currentStep.value = 'intro';
    }
  }
});

// Funções de Navegação
const goToLogin = () => { errorMessage.value = ''; currentStep.value = 'login'; };
const goToRegister = () => { errorMessage.value = ''; currentStep.value = 'register'; };
const goBack = () => { errorMessage.value = ''; currentStep.value = 'intro'; };

const handleGoogleLogin = () => {
    alert("Em breve: Login com Google One Tap");
};

// Login de Desenvolvedor
const handleDevLogin = async () => {
    email.value = 'alvarob.alano@hotmail.com';
    password.value = '123456'; // <--- SUA SENHA
    currentStep.value = 'login';
    await handleAuth();
};

const handleAuth = async () => {
    errorMessage.value = '';
    
    // Validação simples
    if (!email.value || !password.value) {
        errorMessage.value = 'Preencha todos os campos.';
        return;
    }
    
    isLoading.value = true;

    try {
        if (currentStep.value === 'register') {
            // --- CORREÇÃO DO ERRO 404 ---
            // A URL correta é '/users' (sem a barra no final)
            await api.post('/users', {
                email: email.value,
                password: password.value,
                full_name: fullName.value || email.value.split('@')[0]
            });
        }

        const formData = new URLSearchParams();
        formData.append('username', email.value);
        formData.append('password', password.value);

        const { data } = await api.post('/login/access-token', formData);
        
        authStore.setLoginData({ email: email.value }, data.access_token);
        
        currentStep.value = 'loading';
        isLoading.value = false; 
        
        await handlePreLoadAndEnter();

    } catch (error) {
        console.error(error);
        isLoading.value = false;

        // Tradutor de erros para ficar amigável (Ponto 3 do GPT)
        if (error.response?.status === 404) {
             errorMessage.value = "Erro de conexão (404). Contate o suporte.";
        } else if (error.response?.status === 409 || error.response?.data?.detail?.includes('exists')) {
             errorMessage.value = "E-mail já cadastrado. Tente fazer login.";
        } else if (error.response?.status === 401) {
             errorMessage.value = "Senha ou e-mail incorretos.";
        } else {
             errorMessage.value = error.response?.data?.detail || 'Erro ao conectar.';
        }
    }
};

const handlePreLoadAndEnter = async () => {
    // Carrega dados. Se o token for ruim, o axios joga um erro 401 e cai no catch lá de cima
    await Promise.all([
        dashboardStore.fetchAllData(),
        new Promise(resolve => setTimeout(resolve, 2000)) 
    ]);
    router.push('/dashboard');
};
</script>

<template>
  <div class="fixed inset-0 w-full h-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans overflow-hidden flex flex-col transition-colors duration-300">
    
    <button v-if="isDev" @click="handleDevLogin" class="absolute top-4 right-4 z-50 flex items-center gap-2 px-3 py-1.5 bg-red-500/10 text-red-500 border border-red-500/30 rounded-lg text-xs font-mono font-bold hover:bg-red-500/20 cursor-pointer">
        <Zap :size="14" /> DEV
    </button>

    <div class="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-[var(--color-primary)] opacity-15 rounded-full blur-[120px] pointer-events-none animate-pulse"></div>
    <div class="absolute bottom-[-10%] left-[-10%] w-[300px] h-[300px] bg-[var(--color-primary)] opacity-10 rounded-full blur-[100px] pointer-events-none"></div>

    <div class="flex-1 flex flex-col relative z-10 px-6 h-full max-w-md mx-auto w-full">
        
        <Transition name="fade" mode="out-in">
            <AuthIntro 
                v-if="currentStep === 'intro'" 
                @to-login="goToLogin" 
                @to-register="goToRegister" 
                @google-login="handleGoogleLogin"
            />

            <AuthForm 
                v-else-if="currentStep === 'login' || currentStep === 'register'"
                :mode="currentStep"
                :is-loading="isLoading"
                :error-message="errorMessage"
                @submit="handleAuth"
                @back="goBack"
                @google-login="handleGoogleLogin"
                @update:email="e => email = e"
                @update:password="p => password = p"
                @update:fullName="n => fullName = n"
            />

            <AuthLoading 
                v-else-if="currentStep === 'loading'" 
            />
        </Transition>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.4s ease, transform 0.4s ease; }
.fade-enter-from { opacity: 0; transform: translateY(20px); }
.fade-leave-to { opacity: 0; transform: translateY(-20px); }
</style>