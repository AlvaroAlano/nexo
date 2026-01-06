<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // <--- Importa a Store
import api from '../services/api'; // <--- Importa a API
import { Mail, Lock, Eye, EyeOff, Fingerprint, ChevronRight, AlertCircle } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore(); // <--- Inicia a Store

const isRegister = ref(false);
const showPassword = ref(false);
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

// Verifica se já está logado ao abrir o app
onMounted(() => {
  // Graças ao persist: true, se o usuário fechou o app logado,
  // o token estará aqui e redirecionamos na hora!
  if (authStore.token) {
    router.push('/dashboard');
  }
});

const toggleMode = () => {
    isRegister.value = !isRegister.value;
    errorMessage.value = '';
};

const handleAuth = async () => {
  // Validação Básica
  if (!email.value || !password.value) {
      errorMessage.value = 'Preencha todos os campos.';
      return;
  }
  
  errorMessage.value = '';
  isLoading.value = true;

  try {
    if (isRegister.value) {
        // --- FLUXO DE CADASTRO ---
        await api.post('/users/', {
            email: email.value,
            password: password.value,
            full_name: email.value.split('@')[0] // Pega o nome do e-mail provisoriamente
        });
        
        // Se der certo, faz o login automático em seguida
        await performLogin(); 

    } else {
        // --- FLUXO DE LOGIN ---
        await performLogin();
    }
  } catch (error) {
    console.error(error);
    // Tenta pegar a mensagem de erro do Backend ou usa uma genérica
    errorMessage.value = error.response?.data?.detail || 'Erro ao conectar. Verifique seus dados.';
  } finally {
    isLoading.value = false;
  }
};

// Função auxiliar para Login (Backend FastAPI padrão)
const performLogin = async () => {
    // O FastAPI espera o login como Form Data (OAuth2 standard)
    const formData = new URLSearchParams();
    formData.append('username', email.value);
    formData.append('password', password.value);

    // 1. Pega o Token
    const { data } = await api.post('/login/access-token', formData);
    
    // 2. Salva na Store (O persist: true vai salvar no celular automaticamente!)
    // Vamos salvar o email provisoriamente como usuário até termos uma rota /me
    authStore.setLoginData({ email: email.value }, data.access_token);
    
    // 3. Redireciona
    router.push('/dashboard');
};

const handleBiometric = () => {
    // Futuro: Implementar WebAuthn
    alert('Biometria em breve!');
};

const handleSocialLogin = (provider) => {
    alert(`Login com ${provider} em breve.`);
};

// Classes dinâmicas (Mantidas do seu código original)
const inputBorderClass = computed(() => 
    errorMessage.value 
    ? 'border-red-500/50 focus:border-red-500 focus:ring-red-500/20' 
    : 'border-[var(--border)] focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)]/20'
);

const iconColorClass = computed(() => 
    errorMessage.value 
    ? 'text-red-400' 
    : 'text-[var(--text-muted)] group-focus-within:text-[var(--color-primary)]'
);
</script>

<template>
  <div class="fixed inset-0 z-[9999] w-screen h-screen bg-[var(--bg-app)] text-[var(--text-main)] font-sans overflow-y-auto overflow-x-hidden transition-colors duration-300 selection:bg-[var(--color-primary)]/30">
    
    <div class="absolute top-[-10%] right-[-20%] w-[350px] h-[350px] bg-[var(--color-primary)]/15 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] left-[-10%] w-[250px] h-[250px] bg-[var(--color-primary)]/10 rounded-full blur-[90px] pointer-events-none"></div>

    <div class="min-h-full w-full flex flex-col justify-center items-center px-6 py-12 relative z-10">
        
        <div class="w-full max-w-sm">
            
            <Transition name="fade-slide" mode="out-in">
                <div :key="isRegister" class="text-center mb-8 mt-4">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-primary-hover)] flex items-center justify-center text-white font-bold text-3xl shadow-2xl shadow-[var(--color-primary)]/40 mb-6 mx-auto transform hover:scale-105 transition-transform duration-500">
                        N
                    </div>
                    <h1 class="text-3xl font-bold tracking-tight text-[var(--text-main)] mb-2">
                        {{ isRegister ? 'Criar Conta' : 'Bem-vindo!' }}
                    </h1>
                    <p class="text-sm text-[var(--text-muted)] max-w-[280px] mx-auto leading-relaxed">
                        {{ isRegister ? 'Cadastre-se para assumir o controle.' : 'Acesse sua conta para continuar.' }}
                    </p>
                </div>
            </Transition>

            <form @submit.prevent="handleAuth" class="space-y-5">
                
                <div class="space-y-1.5">
                    <div class="relative group">
                        <div class="absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-300" :class="iconColorClass">
                            <Mail :size="20" />
                        </div>
                        <input 
                            v-model="email"
                            type="email" 
                            placeholder="E-mail (Opcional)"
                            class="w-full bg-[var(--bg-surface)] border rounded-2xl pl-12 pr-4 py-4 text-base font-medium text-[var(--text-main)] focus:outline-none focus:ring-2 transition-all placeholder-[var(--text-muted)]/50 shadow-sm"
                            :class="inputBorderClass"
                        />
                    </div>
                </div>

                <div class="space-y-1.5">
                    <div class="relative group">
                        <div class="absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-300" :class="iconColorClass">
                            <Lock :size="20" />
                        </div>
                        <input 
                            v-model="password"
                            :type="showPassword ? 'text' : 'password'" 
                            placeholder="Senha (Opcional)"
                            class="w-full bg-[var(--bg-surface)] border rounded-2xl pl-12 pr-12 py-4 text-base font-medium text-[var(--text-main)] focus:outline-none focus:ring-2 transition-all placeholder-[var(--text-muted)]/50 shadow-sm"
                            :class="inputBorderClass"
                        />
                        <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors p-1">
                            <component :is="showPassword ? EyeOff : Eye" :size="20" />
                        </button>
                    </div>
                    
                    <div v-if="errorMessage" class="flex items-center gap-1.5 mt-2 px-1 animate-in slide-in-from-top-1 fade-in duration-200">
                        <AlertCircle :size="14" class="text-red-500" />
                        <p class="text-xs text-red-500 font-medium">{{ errorMessage }}</p>
                    </div>

                    <div v-if="!isRegister && !errorMessage" class="text-right pt-1 px-1">
                        <button type="button" class="text-xs font-bold text-[var(--text-muted)] hover:text-[var(--color-primary)] transition-colors">Recuperar senha</button>
                    </div>
                </div>

                <button 
                    type="submit"
                    :disabled="isLoading"
                    class="w-full py-4 bg-[var(--color-primary)] hover:brightness-110 text-white font-bold rounded-2xl transition-all active:scale-[0.98] shadow-xl shadow-[var(--color-primary)]/30 mt-6 flex justify-center items-center gap-2 text-base disabled:opacity-80 disabled:cursor-not-allowed group relative overflow-hidden"
                >
                    <span>{{ isRegister ? 'Cadastrar' : 'Acessar conta' }}</span>
                    
                    <div class="w-5 h-5 flex items-center justify-center relative">
                        <Transition name="scale">
                            <span v-if="isLoading" class="absolute inset-0 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                            <ChevronRight v-else :size="20" class="group-hover:translate-x-1 transition-transform" />
                        </Transition>
                    </div>
                </button>

            </form>

            <div class="relative my-8 text-center">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-[var(--border)]"></div></div>
                <span class="relative bg-[var(--bg-app)] px-3 text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold">Ou acesse com</span>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button @click="handleSocialLogin('Google')" class="flex items-center justify-center gap-2 bg-[var(--bg-surface)] border border-[var(--border)] py-3.5 rounded-2xl hover:bg-[var(--bg-hover)] hover:border-[var(--text-muted)]/30 transition-all active:scale-95 shadow-sm group">
                    <svg class="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="none"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                    <span class="text-sm font-bold text-[var(--text-main)]">Google</span>
                </button>

                <button @click="handleBiometric" class="flex items-center justify-center gap-2 bg-[var(--bg-surface)] border border-[var(--border)] py-3.5 rounded-2xl hover:bg-[var(--bg-hover)] hover:border-[var(--color-primary)]/30 transition-all active:scale-95 shadow-sm group">
                    <Fingerprint :size="20" class="text-[var(--text-muted)] group-hover:text-[var(--color-primary)] group-hover:scale-110 transition-all" />
                    <span class="text-sm font-bold text-[var(--text-main)] group-hover:text-[var(--color-primary)] transition-colors">Face ID</span>
                </button>
            </div>

            <div class="mt-10 text-center">
                <p class="text-sm text-[var(--text-muted)]">
                    {{ isRegister ? 'Já tem conta?' : 'Não tem conta?' }}
                    <button @click="toggleMode" class="text-[var(--color-primary)] font-bold hover:underline ml-1">
                        {{ isRegister ? 'Fazer Login' : 'Criar conta' }}
                    </button>
                </p>
            </div>

        </div>
    </div>
  </div>
</template>

<style scoped>
/* Animação suave para troca de conteúdo */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Animação do Loader/Icone */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s ease;
}
.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.5);
}
</style>