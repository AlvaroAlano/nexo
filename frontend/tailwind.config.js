/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // <--- ADICIONE ESTA LINHA OBRIGATÓRIA
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}