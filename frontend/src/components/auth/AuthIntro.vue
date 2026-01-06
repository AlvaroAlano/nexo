<script setup>
import { defineEmits } from 'vue';
import AuthGoogleButton from './AuthGoogleButton.vue'; // Já vamos criar esse

defineEmits(['to-login', 'to-register', 'google-login']);
</script>

<template>
  <div class="h-full flex flex-col justify-between py-12">
    <div class="flex flex-col items-center justify-center flex-1 text-center space-y-8">
      <div class="relative group">
        <div class="absolute inset-0 bg-[var(--color-primary)] blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
        <div class="relative w-24 h-24 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-primary-hover)] rounded-3xl flex items-center justify-center shadow-2xl shadow-[var(--color-primary)]/20 mb-4 transform group-hover:scale-105 transition-transform duration-500">
          <span class="text-5xl font-bold text-white tracking-tighter">N</span>
        </div>
      </div>
      <div>
        <h1 class="text-4xl font-bold mb-3 tracking-tight text-[var(--text-main)]">NEXO</h1>
        <p class="text-[var(--text-muted)] text-lg max-w-[250px] mx-auto leading-relaxed">
          Controle suas finanças com inteligência e simplicidade.
        </p>
      </div>
    </div>

    <div class="space-y-4 w-full mb-8">
      <button @click="$emit('to-register')" class="w-full py-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold rounded-2xl transition-all shadow-lg shadow-[var(--color-primary)]/25 active:scale-95 text-lg">
        Criar minha conta
      </button>
      <button @click="$emit('to-login')" class="w-full py-4 bg-[var(--bg-surface)] hover:bg-[var(--bg-hover)] text-[var(--text-main)] font-semibold rounded-2xl transition-all border border-[var(--border)] active:scale-95 text-lg">
        Já tenho conta
      </button>
      
      <AuthGoogleButton @click="$emit('google-login')" />
    </div>
  </div>
</template>