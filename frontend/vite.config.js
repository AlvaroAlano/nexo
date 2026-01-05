import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'NEXO Financeiro',
        short_name: 'NEXO',
        description: 'Seu controle financeiro pessoal',
        theme_color: '#4F46E5', // Aproveitei para colocar o Azul Indigo da sua logo nova!
        icons: [
          {
            src: 'pwa-192x192.png?v=2', // <--- O TRUQUE ESTÁ AQUI
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png?v=2', // <--- E AQUI TAMBÉM
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
})