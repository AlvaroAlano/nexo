<script setup>
import { computed } from 'vue';
import { Mail, Lock, ChevronLeft, ArrowRight } from 'lucide-vue-next';
import AuthGoogleButton from './AuthGoogleButton.vue';

const props = defineProps(['mode', 'isLoading', 'errorMessage']);
const emit = defineEmits(['submit', 'back', 'google-login', 'update:email', 'update:password', 'update:fullName']);

const isRegister = computed(() => props.mode === 'register');
</script>

<template>
  <div class="h-full flex flex-col py-8">
    <button @click="$emit('back')" class="self-start p-2 hover:bg-[var(--bg-hover)] rounded-full transition-colors mb-6 text-[var(--text-muted)] hover:text-[var(--text-main)]">
      <ChevronLeft :size="28" />
    </button>

    <div class="flex-1 flex flex-col">
      <h2 class="text-3xl font-bold mb-2 text-[var(--text-main)]">
        {{ isRegister ? 'Vamos começar' : 'Bem-vindo de volta' }}
      </h2>
      <p class="text-[var(--text-muted)] mb-8 text-lg">
        {{ isRegister ? 'Crie sua conta em segundos.' : 'Preencha seus dados para entrar.' }}
      </p>

      <form @submit.prevent="$emit('submit')" class="space-y-5">
        <div v-if="isRegister" class="space-y-2">
          <label class="text-sm font-medium text-[var(--text-muted)] ml-1">Nome completo</label>
          <input 
            @input="$emit('update:fullName', $event.target.value)"
            type="text" 
            class="w-full bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl px-4 py-4 text-[var(--text-main)] placeholder-[var(--text-muted)] focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] transition-all outline-none text-lg shadow-sm" 
            placeholder="Ex: João Silva" 
          />
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--text-muted)] ml-1">E-mail</label>
          <div class="relative">
            <Mail class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" :size="20"/>
            <input 
              @input="$emit('update:email', $event.target.value)"
              type="email" 
              class="w-full bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl pl-12 pr-4 py-4 text-[var(--text-main)] placeholder-[var(--text-muted)] focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] transition-all outline-none text-lg shadow-sm" 
              placeholder="seu@email.com" 
            />
          </div>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--text-muted)] ml-1">Senha</label>
          <div class="relative">
            <Lock class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" :size="20"/>
            <input 
              @input="$emit('update:password', $event.target.value)"
              type="password" 
              class="w-full bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl pl-12 pr-4 py-4 text-[var(--text-main)] placeholder-[var(--text-muted)] focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] transition-all outline-none text-lg shadow-sm" 
              placeholder="••••••••" 
            />
          </div>
        </div>

        <div v-if="errorMessage" class="p-4 bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/20 rounded-xl flex gap-3 items-center animate-in slide-in-from-top-2">
          <div class="w-1 h-8 bg-[var(--color-danger)] rounded-full"></div>
          <p class="text-[var(--color-danger)] text-sm font-medium">{{ errorMessage }}</p>
        </div>

        <button type="submit" :disabled="isLoading" class="w-full py-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:opacity-70 disabled:cursor-not-allowed text-white font-bold rounded-2xl transition-all shadow-lg shadow-[var(--color-primary)]/25 mt-4 flex items-center justify-center gap-3 active:scale-95 text-lg group">
          <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          <span v-else>{{ isRegister ? 'Criar Conta' : 'Entrar' }}</span>
          <ArrowRight v-if="!isLoading" :size="20" class="group-hover:translate-x-1 transition-transform" />
        </button>
      </form>

      <div class="relative my-8 text-center">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-[var(--border)]"></div></div>
        <span class="relative bg-[var(--bg-app)] px-3 text-xs text-[var(--text-muted)] uppercase tracking-widest font-bold">Ou continue com</span>
      </div>

      <AuthGoogleButton @click="$emit('google-login')" />
    </div>
  </div>
</template>