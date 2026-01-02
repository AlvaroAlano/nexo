import { ref, computed, watch } from 'vue';
import api from '../services/api';

// Configurações Base dos Gráficos (Estáticos)
const BASE_RUNWAY_OPTIONS = {
    chart: { type: 'area', toolbar: { show: false }, fontFamily: 'inherit', parentHeightOffset: 0, zoom: { enabled: false }, background: 'transparent' },
    stroke: { curve: 'smooth', width: 2 },
    dataLabels: { enabled: false },
    grid: { show: true, borderColor: 'rgba(255,255,255,0.1)', strokeDashArray: 4, padding: { top: 0, right: 10, bottom: 0, left: 10 } },
    tooltip: { theme: 'dark', x: { show: false }, marker: { show: false }, style: { fontSize: '10px' } },
    yaxis: { show: true, labels: { style: { colors: 'rgba(255,255,255,0.7)', fontSize: '10px', fontFamily: 'inherit' }, formatter: (val) => val >= 1000 ? `${(val/1000).toFixed(1)}k` : val.toFixed(0), offsetX: -5 } }
};

const BASE_DONUT_OPTIONS = {
    chart: { type: 'donut', fontFamily: 'inherit', background: 'transparent' },
    stroke: { show: false, width: 0 },
    dataLabels: { enabled: false },
    plotOptions: { pie: { donut: { size: '75%', labels: { show: false } } } },
    legend: { show: false },
    tooltip: { enabled: false }
};

export function useDashboard() {
    const isLoading = ref(true);
    const currentDate = ref(new Date());
    const showValues = ref(true);
    const isDark = ref(false); // Estado do tema movido para cá (ou useSettings)

    // Dados
    const summary = ref({ balance: 0, month_income: 0, month_expense: 0, projected_balance: 0 });
    const recentActivity = ref([]);
    const upcomingBills = ref([]);
    const creditCardsList = ref([]);
    const debtsSummary = ref({ total_receivable: 0, debtors: [] }); // Trazido para cá
    
    // Dados Gráficos
    const chartData = ref({ runwaySeries: [], categories: { labels: [], series: [], colors: [] } });

    // --- Computed Properties ---
    const creditCardsSummary = computed(() => {
        const totalInvoice = creditCardsList.value.reduce((sum, card) => sum + (card.invoice || 0), 0);
        const totalLimit = creditCardsList.value.reduce((sum, card) => sum + (card.limit || 0), 0);
        const totalDebt = creditCardsList.value.reduce((sum, card) => sum + (card.total_debt || card.invoice || 0), 0); // Fallback
        return { total_invoice: totalInvoice, total_debt: totalDebt, total_limit: totalLimit };
    });

    const currentMonthLabel = computed(() => {
        const label = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(currentDate.value);
        return label.charAt(0).toUpperCase() + label.slice(1);
    });

    // --- Configuração Dinâmica dos Gráficos ---
    const runwayOptions = computed(() => {
        const dates = [];
        for (let i = 6; i >= 0; i--) {
            const d = new Date(); d.setDate(d.getDate() - i);
            dates.push(`${d.getDate()}/${d.getMonth() + 1}`);
        }
        
        return {
            ...BASE_RUNWAY_OPTIONS,
            colors: [isDark.value ? '#22D3EE' : '#FCD34D'],
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.05, stops: [0, 100] } },
            markers: { size: 4, colors: [isDark.value ? '#0891B2' : '#F59E0B'], strokeColors: '#fff', strokeWidth: 2, hover: { size: 6 } },
            xaxis: { categories: dates, labels: { style: { colors: 'rgba(255,255,255,0.7)', fontSize: '10px', fontFamily: 'inherit' }, offsetY: -5 }, axisBorder: { show: false }, axisTicks: { show: false }, crosshairs: { show: false }, tooltip: { enabled: false } }
        };
    });

    const donutOptions = computed(() => ({
        ...BASE_DONUT_OPTIONS,
        labels: chartData.value.categories.labels,
        colors: chartData.value.categories.colors.length ? chartData.value.categories.colors : ['#333']
    }));

    // --- Actions ---
    const fetchDashboardData = async () => {
        try {
            isLoading.value = true;
            const month = currentDate.value.getMonth() + 1;
            const year = currentDate.value.getFullYear();

            // Executa tudo em paralelo
            const [summaryRes, recentRes, upcomingRes, cardsRes, chartsRes, debtsRes] = await Promise.all([
                api.get(`/dashboard/summary?month=${month}&year=${year}`),
                api.get(`/transactions/?limit=20&month=${month}&year=${year}`),
                api.get(`/dashboard/upcoming`),
                api.get(`/credit-cards/?month=${month}&year=${year}`),
                api.get(`/dashboard/charts/categories?month=${month}&year=${year}`),
                api.get('/debts/summary').catch(() => ({ data: { total_receivable: 0, debtors: [] } })) // Fallback se falhar
            ]);

            summary.value = summaryRes.data;
            recentActivity.value = recentRes.data;
            creditCardsList.value = cardsRes.data;
            debtsSummary.value = debtsRes.data;
            
            // Lógica de Contas + Faturas (Mantida a sua lógica original, apenas encapsulada)
            processUpcomingBills(upcomingRes.data, cardsRes.data);
            
            // Dados Mockados de Gráfico (Isso deve vir do back futuramente)
            const currentBalance = summary.value.balance || 0;
            chartData.value.runwaySeries = [{ 
                name: 'Saldo', 
                data: [currentBalance * 0.9, currentBalance * 0.85, currentBalance * 1.1, currentBalance * 0.95, currentBalance * 1.05, currentBalance * 0.98, currentBalance] 
            }];

            if (chartsRes.data.length > 0) {
                chartData.value.categories = {
                    labels: chartsRes.data.map(i => i.name),
                    series: chartsRes.data.map(i => i.value),
                    colors: chartsRes.data.map(i => i.color)
                };
            }

        } catch (error) {
            console.error("Erro no Dashboard:", error);
        } finally {
            isLoading.value = false;
        }
    };

    const processUpcomingBills = (apiBills, cards) => {
        const today = new Date(); today.setHours(0,0,0,0);
        const nextWeek = new Date(); nextWeek.setDate(today.getDate() + 7);

        const cardBills = cards.map(card => {
            const due = new Date(today.getFullYear(), today.getMonth(), card.due_day);
            if (due < today) due.setMonth(due.getMonth() + 1);
            return {
                id: `card-${card.id}`, description: `Fatura ${card.name}`, amount: card.invoice,
                date: due.toISOString().split('T')[0], type: 'card', color: card.color
            };
        }).filter(bill => {
            const billDate = new Date(bill.date + 'T00:00:00');
            return billDate >= today && billDate <= nextWeek && bill.amount > 0;
        });

        upcomingBills.value = [...apiBills, ...cardBills].sort((a, b) => new Date(a.date) - new Date(b.date));
    };

    const changeMonth = (delta) => {
        const newDate = new Date(currentDate.value);
        newDate.setMonth(newDate.getMonth() + delta);
        currentDate.value = newDate;
        fetchDashboardData();
    };

    const togglePrivacy = () => showValues.value = !showValues.value;

    // Helpers de Formatação
    const formatCurrency = (val) => !showValues.value ? '••••' : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
    
    const getDaysRemaining = (dateString) => {
        if (!dateString) return '';
        const today = new Date(); today.setHours(0, 0, 0, 0);
        const due = new Date(dateString + 'T00:00:00');
        const diffDays = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
        if (diffDays < 0) return 'Venceu';
        if (diffDays === 0) return 'Hoje';
        if (diffDays === 1) return 'Amanhã';
        return `${diffDays} dias`;
    };

    return {
        isLoading, isDark, currentDate, showValues,
        summary, recentActivity, upcomingBills, creditCardsList, debtsSummary,
        creditCardsSummary, chartData, runwayOptions, donutOptions, currentMonthLabel,
        fetchDashboardData, changeMonth, togglePrivacy, formatCurrency, getDaysRemaining
    };
}