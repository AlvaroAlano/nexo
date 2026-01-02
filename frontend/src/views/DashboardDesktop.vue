<script setup>
import { ref, onMounted, onActivated, computed, watchEffect } from 'vue';
import api from '../services/api';
import { useDashboard } from '../composables/useDashboard'; 
import { useSettings } from '../composables/useSettings'; 

// Components
import SidebarDesktop from '../components/SidebarDesktop.vue';
import SummaryCards from '../components/Dashboard/SummaryCards.vue';
import GoalsSummaryWidget from '../components/Dashboard/GoalsSummaryWidget.vue';
import NewTransactionModal from '../components/NewTransactionModal.vue';
import NewCardModal from '../components/NewCardModal.vue';
import TransactionDetailsModal from '../components/TransactionDetailsModal.vue';
import InvoiceDetailModal from '../components/InvoiceDetailModal.vue';
import TransactionRow from '../components/TransactionRow.vue';
import CreditCardWidget from '../components/CreditCardWidget.vue';

import { 
  Bell, Plus, ChevronLeft, ChevronRight, BarChart2, CalendarCheck,
  Calendar, Activity, PieChart, Users 
} from 'lucide-vue-next';

// --- LÓGICA (Mantida igual, pois já está atualizada) ---
const { 
    isLoading, currentDate, summary, recentActivity, upcomingBills, 
    creditCardsList, creditCardsSummary, chartData, currentMonthLabel,
    fetchDashboardData, changeMonth, formatCurrency, getDaysRemaining
} = useDashboard();

const { enableDebts, enableGoals } = useSettings();

const isModalOpen = ref(false); 
const isCardModalOpen = ref(false); 
const isDark = ref(true); 
const chartType = ref('donut');
const isInvoiceModalOpen = ref(false);
const selectedCard = ref(null);
const selectedTransaction = ref(null);
const isDetailsModalOpen = ref(false);
const transactionToEdit = ref(null);
const debtsSummary = ref({ total_receivable: 0, debtors: [] });
const CHART_COLORS = { light: '#2563EB', dark: '#3B82F6' };

const openInvoiceDetails = (card) => { selectedCard.value = card; isInvoiceModalOpen.value = true; };
const openDetails = (tx) => { selectedTransaction.value = tx; isDetailsModalOpen.value = true; };
const openEditModal = (tx) => { transactionToEdit.value = tx; isModalOpen.value = true; };

const handleDataUpdate = async () => {
    await fetchDashboardData();
    if (enableDebts.value) await fetchDebtsSummary();
};

const handleDelete = async (tx) => {
    if(!confirm(`Deseja realmente excluir "${tx.description}"?`)) return;
    try { await api.delete(`/transactions/${tx.id}`); handleDataUpdate(); } catch (error) { alert("Erro ao excluir."); }
};

const fetchDebtsSummary = async () => {
    if (!enableDebts.value) return;
    try { const res = await api.get('/debts/summary'); debtsSummary.value = res.data; } catch (e) { console.error(e); }
};

const healthStatus = computed(() => {
  const r = summary.value.commitment_ratio || 0;
  if (r > 85) return { label: 'Crítico', text: 'text-[var(--color-danger)]', bg: 'bg-[var(--color-danger)]', border: 'border-[var(--color-danger)]/20' };
  if (r > 60) return { label: 'Atenção', text: 'text-[var(--color-warning)]', bg: 'bg-[var(--color-warning)]', border: 'border-[var(--color-warning)]/20' };
  return { label: 'Saudável', text: 'text-[var(--color-success)]', bg: 'bg-[var(--color-success)]', border: 'border-[var(--color-success)]/20' };
});

const progressColor = computed(() => {
  const ratio = summary.value.commitment_ratio || 0;
  if (ratio > 85) return 'var(--color-danger)'; 
  if (ratio > 60) return 'var(--color-warning)'; 
  return 'var(--color-success)'; 
});

const runwayOptions = ref({
  chart: { type: 'area', toolbar: { show: false }, fontFamily: 'inherit', background: 'transparent', animations: { enabled: true } },
  colors: [CHART_COLORS.light], 
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.02, stops: [0, 100] } },
  dataLabels: { enabled: false }, stroke: { curve: 'smooth', width: 3 },
  xaxis: { labels: { show: false }, axisBorder: { show: false }, axisTicks: { show: false } }, yaxis: { show: false }, 
  grid: { show: true, borderColor: 'var(--border)', strokeDashArray: 3, padding: { left: 10, right: 0, top: 0, bottom: 0 } },
  tooltip: { theme: 'dark' }
});

const rankingOptions = ref({
  chart: { type: 'donut', background: 'transparent', fontFamily: 'inherit' },
  labels: [], colors: [], stroke: { show: false }, 
  dataLabels: { enabled: true, formatter: (val) => Math.round(val) + "%", style: { fontSize: '12px', fontWeight: 'bold' }, dropShadow: { enabled: false } },
  plotOptions: { pie: { donut: { size: '75%', labels: { show: true, name: { show: false }, value: { show: true, fontSize: '20px', fontWeight: 700, offsetY: 8, color: 'var(--text-main)', formatter: (val) => formatCurrency(val) }, total: { show: true, showAlways: true, formatter: w => formatCurrency(w.globals.seriesTotals.reduce((a, b) => a + b, 0)), color: 'var(--text-main)' } } } } },
  legend: { show: false }, tooltip: { enabled: true, theme: 'dark' }
});

const barOptions = ref({
  chart: { type: 'bar', background: 'transparent', fontFamily: 'inherit', toolbar: { show: false } },
  colors: [], plotOptions: { bar: { borderRadius: 4, horizontal: true, barHeight: '50%', distributed: true } },
  dataLabels: { enabled: false }, xaxis: { categories: [], labels: { style: { colors: 'var(--text-muted)' } } }, yaxis: { labels: { style: { colors: 'var(--text-muted)' } } },
  grid: { show: false }, legend: { show: false }, tooltip: { theme: 'dark' }
});

watchEffect(() => {
    const runwayColor = isDark.value ? CHART_COLORS.dark : CHART_COLORS.light;
    runwayOptions.value = { ...runwayOptions.value, colors: [runwayColor] };
    if(chartData.value.categories.labels.length > 0) {
        rankingOptions.value = { ...rankingOptions.value, labels: chartData.value.categories.labels, colors: chartData.value.categories.colors };
        barOptions.value = { ...barOptions.value, colors: chartData.value.categories.colors, xaxis: { ...barOptions.value.xaxis, categories: chartData.value.categories.labels } };
    }
});

onMounted(() => {
    const savedTheme = localStorage.getItem('theme');
    isDark.value = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
    fetchDashboardData(); fetchDebtsSummary(); 
});
onActivated(() => { fetchDashboardData(); if (enableDebts.value) fetchDebtsSummary(); });
</script>

<template>
  <div class="flex h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] overflow-hidden transition-colors duration-300">
    
    <SidebarDesktop class="hidden lg:flex" />

    <main class="flex-1 flex flex-col h-full relative overflow-hidden bg-[var(--bg-app)] transition-colors duration-300">
        
        <header class="h-16 px-4 md:px-8 mx-4 md:mx-6 mt-4 flex items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] rounded-2xl shadow-sm z-20 shrink-0">
            <div class="flex items-center gap-2 md:gap-4">
               <button class="lg:hidden p-2 -ml-2 text-[var(--text-muted)]"><Users :size="20" /></button> 

               <button @click="changeMonth(-1)" class="w-8 h-8 rounded-full hover:bg-[var(--bg-app)] flex items-center justify-center text-[var(--text-muted)]"><ChevronLeft :size="18" /></button>
               <span class="text-sm font-semibold min-w-[120px] text-center tracking-wide text-[var(--text-main)]">{{ currentMonthLabel }}</span>
               <button @click="changeMonth(1)" class="w-8 h-8 rounded-full hover:bg-[var(--bg-app)] flex items-center justify-center text-[var(--text-muted)]"><ChevronRight :size="18" /></button>
            </div>
            <div class="flex items-center gap-4">
                <button class="text-[var(--text-muted)] hover:text-[var(--text-main)] relative hover:scale-110">
                   <Bell :size="20" />
                   <span class="absolute top-0 right-0 w-2 h-2 bg-[var(--color-danger)] rounded-full border-2 border-[var(--bg-surface)]"></span>
                </button>
                <button @click="isModalOpen = true" class="h-9 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2 shadow-lg shadow-blue-500/30">
                    <Plus :size="16" /> <span class="hidden md:inline">Nova Transação</span>
                </button>
            </div>
        </header>

        <div class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scroll z-10">
            
            <SummaryCards :summary="summary" :creditCardsSummary="creditCardsSummary" :formatCurrency="formatCurrency" />

            <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
                
                <div class="xl:col-span-8 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-sm flex flex-col relative overflow-hidden min-h-[360px]">
                    <div class="px-6 py-4 border-b border-[var(--border)] flex justify-between items-center bg-[var(--bg-app)]/30 backdrop-blur-sm">
                        <h3 class="text-xs font-bold uppercase text-[var(--text-muted)] tracking-wider flex items-center gap-2"><Activity :size="16" /> Runway (Caixa)</h3>
                        <div class="px-2.5 py-1 rounded-full border text-[10px] font-bold flex items-center gap-1.5" :class="`${healthStatus.bg}/10 ${healthStatus.text} ${healthStatus.border}`">
                            <div class="w-1.5 h-1.5 rounded-full" :class="healthStatus.bg"></div>{{ healthStatus.label }}
                        </div>
                    </div>
                    <div class="flex flex-col md:flex-row h-full">
                        <div class="flex-1 p-4 border-r-0 md:border-r border-[var(--border)] relative min-h-[200px]">
                            <apexchart type="area" height="100%" width="100%" :options="runwayOptions" :series="chartData.runwaySeries"></apexchart>
                        </div>
                        <div class="w-full md:w-72 p-6 flex flex-col justify-center space-y-8 bg-[var(--bg-surface)] shrink-0">
                            <div>
                                <p class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2">Saldo Final (Estimado)</p>
                                <h3 class="text-3xl font-bold font-numeric tracking-tight" :class="summary.projected_balance < 0 ? 'text-[var(--color-danger)]' : 'text-[var(--text-main)]'">{{ formatCurrency(summary.projected_balance) }}</h3>
                                <p class="text-[11px] text-[var(--text-muted)] mt-2 leading-tight opacity-70">Baseado nas contas fixas e faturas.</p>
                            </div>
                            <div>
                                <div class="flex justify-between items-end mb-2">
                                    <p class="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Renda Comprometida</p>
                                    <span class="text-xs font-bold" :style="{ color: progressColor }">{{ summary.commitment_ratio }}%</span>
                                </div>
                                <div class="w-full bg-[var(--bg-app)] h-1.5 rounded-full overflow-hidden border border-[var(--border)]">
                                    <div class="h-full rounded-full transition-all duration-1000" :style="{ width: summary.commitment_ratio + '%', backgroundColor: progressColor }"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="xl:col-span-4 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-sm p-5 flex flex-col relative min-h-[360px]">
                    <div class="flex justify-between items-center mb-2 z-10">
                        <h3 class="text-xs font-bold uppercase text-[var(--text-muted)] tracking-wider">Top Despesas</h3>
                        <div class="flex bg-[var(--bg-app)] p-1 rounded-lg border border-[var(--border)]" v-if="chartData.categories.series.length > 0">
                            <button @click="chartType = 'donut'" class="p-1.5 rounded-md transition-all" :class="chartType === 'donut' ? 'bg-[var(--bg-surface)] text-[var(--color-primary)] shadow-inner' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"><PieChart :size="14" /></button>
                            <button @click="chartType = 'bar'" class="p-1.5 rounded-md transition-all" :class="chartType === 'bar' ? 'bg-[var(--bg-surface)] text-[var(--color-primary)] shadow-inner' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"><BarChart2 :size="14" /></button>
                        </div>
                    </div>
                    <div class="flex-1 relative flex flex-col items-center justify-center min-h-[200px]">
                        <template v-if="chartData.categories.series.length > 0">
                            <apexchart v-if="chartType === 'donut'" type="donut" width="100%" height="100%" :options="rankingOptions" :series="chartData.categories.series"></apexchart>
                            <apexchart v-else type="bar" width="100%" height="100%" :options="barOptions" :series="[{ name: 'Valor', data: chartData.categories.series }]"></apexchart>
                        </template>
                        <div v-else class="text-center text-[var(--text-muted)]"><span class="text-xs font-medium">Sem despesas.</span></div>
                    </div>
                    <div v-if="chartType === 'donut' && chartData.categories.series.length > 0" class="mt-2 grid grid-cols-2 gap-2 pt-3 border-t border-[var(--border)]">
                        <div v-for="(item, i) in rankingOptions.labels.slice(0, 4)" :key="item" class="flex items-center gap-2 text-[10px]">
                            <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: rankingOptions.colors[i] }"></div>
                            <span class="text-[var(--text-muted)] truncate">{{ item }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-[400px]">
                
                <div class="xl:col-span-8 bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden flex flex-col">
                    <div class="px-6 py-4 border-b border-[var(--border)] flex justify-between items-center">
                        <h3 class="text-xs font-bold uppercase text-[var(--text-muted)] tracking-wider">Movimentações</h3>
                        <button class="text-[11px] font-medium text-[var(--color-primary)] hover:underline">Ver todas</button>
                    </div>
                    <div class="flex-1 overflow-y-auto p-2 custom-scroll max-h-[400px]">
                        <TransactionRow v-if="recentActivity.length" v-for="tx in recentActivity" :key="tx.id" :transaction="tx" :showActions="true" @click="openDetails" @edit="openEditModal" @delete="handleDelete" />
                        <div v-else class="p-8 text-center text-[var(--text-muted)] text-sm">Nenhuma movimentação.</div>
                    </div>
                </div>

                <div class="xl:col-span-4 flex flex-col gap-6">
                    
                    <div v-if="enableDebts" class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-sm p-4 flex flex-col">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-500 flex items-center justify-center"><Users :size="16" /></div>
                                <span class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">A Receber</span>
                            </div>
                            <button @click="$router.push('/acertos')" class="px-3 py-1 bg-purple-500/10 hover:bg-purple-500/20 text-purple-500 rounded-md text-[10px] font-bold">Detalhes</button>
                        </div>
                        <div class="flex items-baseline gap-2">
                            <h3 class="text-2xl font-bold font-numeric text-[var(--text-main)]">{{ formatCurrency(debtsSummary.total_receivable) }}</h3>
                            <span class="text-[10px] text-[var(--text-muted)]">{{ debtsSummary.debtors.length > 0 ? `de ${debtsSummary.debtors.length} pessoas` : 'Tudo em dia' }}</span>
                        </div>
                    </div>

                    <div v-if="enableGoals"><GoalsSummaryWidget @update="handleDataUpdate" /></div>

                    <div class="bg-[var(--bg-surface)] rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden flex flex-col max-h-[250px]">
                        <div class="px-5 py-3 border-b border-[var(--border)] flex justify-between items-center">
                            <h3 class="text-xs font-bold uppercase text-[var(--text-muted)] tracking-wider">Cartões</h3>
                            <button @click="isCardModalOpen = true" class="text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center gap-1 text-[10px] font-bold"><Plus :size="14" /> Novo</button>
                        </div>
                        <div class="flex-1 p-2 space-y-2 overflow-y-auto custom-scroll">
                            <CreditCardWidget v-if="creditCardsList.length" v-for="card in creditCardsList" :key="card.id" :card="card" @click="openInvoiceDetails(card)" />
                            <div v-else class="p-4 text-center text-[var(--text-muted)] text-xs">Sem cartões.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <NewTransactionModal :isOpen="isModalOpen" :transactionToEdit="transactionToEdit" @close="isModalOpen = false; transactionToEdit = null" @success="handleDataUpdate" />
    <NewCardModal :isOpen="isCardModalOpen" @close="isCardModalOpen = false" @success="handleDataUpdate" />
    <TransactionDetailsModal :isOpen="isDetailsModalOpen" :transaction="selectedTransaction" @close="isDetailsModalOpen = false" @deleted="handleDataUpdate" @edit="openEditModal" @updated="handleDataUpdate" />
    <InvoiceDetailModal :isOpen="isInvoiceModalOpen" :card="selectedCard" :month="currentDate.getMonth() + 1" :year="currentDate.getFullYear()" @close="isInvoiceModalOpen = false" />
  </div>
</template>