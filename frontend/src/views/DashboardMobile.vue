<script setup>
import { ref, onMounted, onActivated, nextTick } from 'vue';
import { useRouter } from 'vue-router'; 
import { useDashboard } from '../composables/useDashboard';
import { useSettings } from '../composables/useSettings';

// Componentes
import GoalsSummaryWidget from '../components/Dashboard/GoalsSummaryWidget.vue';
import InvestmentsSummaryWidget from '../components/Dashboard/InvestmentsSummaryWidget.vue';
import NewCardModal from '../components/NewCardModal.vue';
import NewTransactionModal from '../components/NewTransactionModal.vue';
import TransactionDetailsModal from '../components/TransactionDetailsModal.vue';
import InvoiceDetailModal from '../components/InvoiceDetailModal.vue';
import UpcomingBillsModal from '../components/UpcomingBillsModal.vue';
import TransactionRow from '../components/TransactionRow.vue';
import CreditCardWidget from '../components/CreditCardWidget.vue';

import { 
  ChevronLeft, ChevronRight, MoreVertical, Landmark, Plus, Minus, CreditCard, 
  List, ArrowRight, Eye, EyeOff, ChevronDown, ChevronUp, PieChart, Users, Bell, Calendar
} from 'lucide-vue-next';

const router = useRouter(); 
const { enableDebts, enableGoals, enableInvestments } = useSettings();

// --- TUDO VEM DO COMPOSABLE AGORA ---
const { 
    summary, recentActivity, upcomingBills, creditCardsList, debtsSummary,
    creditCardsSummary, chartData, runwayOptions, donutOptions, currentMonthLabel, showValues, isDark,
    fetchDashboardData, changeMonth, formatCurrency, getDaysRemaining, togglePrivacy, currentDate
} = useDashboard();

// Estados Locais (Apenas UI/Modais)
const isModalOpen = ref(false); 
const isCardModalOpen = ref(false);
const isInvoiceModalOpen = ref(false);
const isUpcomingModalOpen = ref(false);
const isDetailsModalOpen = ref(false);
const isNotificationsOpen = ref(false); // Mantido simples por enquanto
const isTransactionListExpanded = ref(false); 
const showCharts = ref(true);

const selectedTransaction = ref(null);
const transactionToEdit = ref(null);
const selectedCard = ref(null);

// Helpers de Modal
const openDetails = (tx) => { selectedTransaction.value = tx; isDetailsModalOpen.value = true; };
const openEditModal = (tx) => { transactionToEdit.value = tx; isModalOpen.value = true; };
const handleUpcomingSelect = (bill) => { isUpcomingModalOpen.value = false; openDetails(bill); };
const openInvoiceDetails = (card) => { selectedCard.value = card; isInvoiceModalOpen.value = true; };

// Ciclo de Vida
onMounted(() => fetchDashboardData());

// Hack para o ApexCharts renderizar corretamente ao voltar para a tela
onActivated(async () => {
    showCharts.value = false;
    await nextTick();
    setTimeout(() => { showCharts.value = true; fetchDashboardData(); }, 300);
});

// Detecção Simples de Tema (Se não usar useSettings globalmente ainda)
const checkTheme = () => isDark.value = document.documentElement.classList.contains('dark');
onMounted(checkTheme);
</script>

<template>
  <div class="h-full w-full overflow-y-auto bg-[var(--bg-app)] text-[var(--text-main)] font-sans pb-24">
    
    <div class="text-white relative flex flex-col pt-8 shadow-md z-10 transition-all duration-500" 
         :class="isDark ? 'bg-[var(--bg-surface)]' : 'bg-gradient-to-br from-[#1976D2] to-[#1565C0]'">
      
      <div class="px-5 flex justify-between items-center z-20 mb-4">
          <div class="flex items-center gap-3">
              <button @click="togglePrivacy" class="p-2 rounded-full hover:bg-white/10 transition-colors">
                  <component :is="showValues ? Eye : EyeOff" :size="22" class="text-white/90" />
              </button>
              <div class="flex items-center gap-1">
                  <button @click="changeMonth(-1)" class="p-1 hover:bg-white/10 rounded-full"><ChevronLeft :size="18" class="text-white/90" /></button>
                  <span class="text-sm font-bold tracking-wide text-white min-w-[90px] text-center">{{ currentMonthLabel }}</span>
                  <button @click="changeMonth(1)" class="p-1 hover:bg-white/10 rounded-full"><ChevronRight :size="18" class="text-white/90" /></button>
              </div>
          </div>
          <button @click="isNotificationsOpen = true" class="relative p-2 rounded-full hover:bg-white/10">
              <Bell :size="22" class="text-white/90" />
          </button>
      </div>

      <div class="flex justify-between items-end px-6 mb-2 relative z-20">
        <div class="flex flex-col items-center opacity-90 w-1/3">
            <span class="text-[9px] font-medium text-white/70 uppercase">Receitas</span>
            <span class="text-xs font-semibold font-numeric text-emerald-300">{{ formatCurrency(summary.month_income) }}</span>
        </div>
        <div class="flex flex-col items-center cursor-pointer w-1/3" @click="togglePrivacy">
            <span class="text-[9px] font-bold text-white/60 uppercase mb-0.5">Saldo</span>
            <span class="text-2xl font-bold leading-none font-numeric">{{ formatCurrency(summary.balance) }}</span>
        </div>
        <div class="flex flex-col items-center opacity-90 w-1/3">
            <span class="text-[9px] font-medium text-white/70 uppercase">Previsto</span>
            <span class="text-xs font-semibold font-numeric text-white/90">{{ formatCurrency(summary.projected_balance) }}</span>
        </div>
      </div>
      
      <div class="relative w-full h-[160px] mt-1 px-0 pb-0">
          <apexchart v-if="showCharts" type="area" height="100%" width="100%" :options="runwayOptions" :series="chartData.runwaySeries"></apexchart>
      </div>
    </div>

    <div class="bg-[var(--bg-app)] relative z-0 px-4 pt-6 space-y-5">
      
      <div class="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide snap-x">
          <div class="min-w-[145px] p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] shadow-sm flex flex-col justify-between snap-center">
              <div class="flex items-center gap-2 mb-1">
                  <div class="p-1.5 rounded-full bg-indigo-500/10 text-indigo-500"><CreditCard :size="15" /></div>
                  <span class="text-[9px] font-bold text-[var(--text-muted)] uppercase">Faturas</span>
              </div>
              <div>
                  <p class="text-sm font-bold text-[var(--text-main)] mb-1">{{ formatCurrency(creditCardsSummary.total_invoice) }}</p>
                  <div class="w-full bg-gray-200 dark:bg-gray-700 h-1.5 rounded-full overflow-hidden">
                      <div class="h-full bg-indigo-500 rounded-full" :style="{ width: Math.min(((creditCardsSummary.total_debt||0)/(creditCardsSummary.total_limit||1))*100, 100) + '%' }"></div>
                  </div>
              </div>
          </div>

          <div v-if="enableDebts" @click="router.push('/acertos')" class="min-w-[140px] p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] shadow-sm flex flex-col justify-between snap-center cursor-pointer">
              <div class="flex items-center gap-2 mb-1">
                  <div class="p-1.5 rounded-full bg-purple-500/10 text-purple-500"><Users :size="15" /></div>
                  <span class="text-[9px] font-bold text-[var(--text-muted)] uppercase">A Receber</span>
              </div>
              <div>
                  <p class="text-sm font-bold text-[var(--text-main)] mb-1">{{ formatCurrency(debtsSummary.total_receivable) }}</p>
                  <p class="text-[9px] text-[var(--text-muted)]">{{ debtsSummary.debtors.length }} devedores</p>
              </div>
          </div>

           <div @click="isUpcomingModalOpen = true" class="min-w-[140px] p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] shadow-sm flex flex-col justify-between snap-center cursor-pointer">
              <div class="flex items-center gap-2 mb-2">
                  <div class="p-1.5 rounded-full bg-rose-500/10 text-rose-500"><Calendar :size="15" /></div>
                  <span class="text-[9px] font-bold text-[var(--text-muted)] uppercase">A Vencer</span>
              </div>
              <div v-if="upcomingBills.length > 0" class="flex flex-col gap-2">
                  <div v-for="bill in upcomingBills.slice(0, 2)" :key="bill.id" class="border-l-2 border-rose-500 pl-2">
                      <p class="text-[11px] font-bold truncate mb-0.5">{{ bill.description }}</p>
                      <p class="text-[9px] text-rose-500 font-medium">{{ getDaysRemaining(bill.date) }}</p>
                  </div>
              </div>
              <div v-else><p class="text-[9px] text-[var(--text-muted)]">Nada previsto 🎉</p></div>
          </div>
      </div>

      <div class="bg-[var(--bg-surface)] rounded-xl shadow-sm p-3 border border-[var(--border)]">
        <div class="flex justify-between items-center mb-3 px-1">
            <h3 class="text-sm font-bold text-[var(--text-main)]">Visão geral</h3>
            <button class="text-[var(--text-muted)]"><MoreVertical :size="16" /></button>
        </div>
        <div class="space-y-3">
           <div class="flex justify-between border-b border-[var(--border)]/30 pb-2 px-1">
                <div class="flex gap-3 items-center">
                    <div class="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500"><Landmark :size="16" /></div>
                    <div class="flex flex-col"><span class="text-xs font-semibold">Saldo</span><span class="text-[9px] text-muted">Disponível</span></div>
                </div>
                <p class="text-xs font-bold">{{ formatCurrency(summary.balance) }}</p>
           </div>
           </div>
      </div>

      <div class="bg-[var(--bg-surface)] rounded-xl border border-[var(--border)] shadow-sm p-3">
         <div class="flex justify-between items-center mb-3 px-1">
             <h3 class="text-xs font-bold text-[var(--text-main)] uppercase flex items-center gap-2"><List :size="14" /> Movimentações</h3>
         </div>
         
         <div v-if="recentActivity.length > 0">
            <TransactionRow v-for="tx in (isTransactionListExpanded ? recentActivity : recentActivity.slice(0,3))" 
                :key="tx.id" :transaction="tx" :privacy-mode="!showValues" @click="openDetails" />
         </div>
         <div v-else class="text-center py-4 text-muted text-xs">Sem movimentações.</div>

         <div v-if="recentActivity.length > 3" class="mt-3 pt-2 border-t border-[var(--border)]/30">
            <button @click="isTransactionListExpanded = !isTransactionListExpanded" class="w-full py-2 flex items-center justify-center gap-1 text-xs font-bold text-blue-500">
                 {{ isTransactionListExpanded ? 'Ver menos' : 'Ver todas' }}
                 <component :is="isTransactionListExpanded ? ChevronUp : ChevronDown" :size="14" />
             </button>
         </div>
      </div>

      <div class="bg-[var(--bg-surface)] rounded-xl shadow-sm p-4 border border-[var(--border)]">
         <div class="flex justify-between items-center mb-3 px-1"><h3 class="text-sm font-bold text-[var(--text-main)]">Por categoria</h3></div>
         <div v-if="chartData.categories.series.length > 0" class="flex items-center justify-between">
           <div class="w-24 h-24"><apexchart v-if="showCharts" type="donut" width="100%" height="100%" :options="donutOptions" :series="chartData.categories.series"></apexchart></div>
           <div class="flex-1 pl-5 space-y-2">
             <div v-for="(item, index) in donutOptions.labels.slice(0, 3)" :key="index" class="flex justify-between text-[10px]">
                <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full" :style="{background: donutOptions.colors[index]}"></div><span>{{ item }}</span></div>
                <span class="font-bold">{{ Math.round((chartData.categories.series[index] / chartData.categories.series.reduce((a,b)=>a+b,0)) * 100) }}%</span>
             </div>
           </div>
         </div>
         <div v-else class="flex flex-col items-center py-6 text-muted"><PieChart :size="24" class="opacity-50 mb-2" /><span class="text-xs">Sem dados</span></div>
      </div>

      <div v-if="enableGoals || enableInvestments" class="space-y-3 mb-20">
          <GoalsSummaryWidget v-if="enableGoals" @update="fetchDashboardData" />
          <InvestmentsSummaryWidget v-if="enableInvestments" />
      </div>

    </div>

    <button @click="isModalOpen = true" class="fixed bottom-[80px] right-4 w-12 h-12 bg-blue-600 text-white rounded-full shadow-xl flex items-center justify-center z-50 active:scale-90 transition-transform">
        <Plus :size="24" stroke-width="3" />
    </button>
    
    <NewTransactionModal :isOpen="isModalOpen" :transactionToEdit="transactionToEdit" @close="isModalOpen = false; transactionToEdit = null" @success="fetchDashboardData" />
    <NewCardModal :isOpen="isCardModalOpen" @close="isCardModalOpen = false" @success="fetchDashboardData" />
    <TransactionDetailsModal :isOpen="isDetailsModalOpen" :transaction="selectedTransaction" @close="isDetailsModalOpen = false" @deleted="fetchDashboardData" @edit="openEditModal" @updated="fetchDashboardData" />
    <InvoiceDetailModal :isOpen="isInvoiceModalOpen" :card="selectedCard" :month="currentDate.getMonth() + 1" :year="currentDate.getFullYear()" @close="isInvoiceModalOpen = false" />
    <UpcomingBillsModal :isOpen="isUpcomingModalOpen" :bills="upcomingBills" @close="isUpcomingModalOpen = false" @select="handleUpcomingSelect" />
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.font-numeric { font-variant-numeric: tabular-nums; }
</style>