<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 
import SidebarDesktop from '../components/SidebarDesktop.vue'; 
import { 
    ChevronLeft, Tag, Plus, ShoppingCart, Utensils, 
    Car, Home, MoreVertical, Edit2, Trash2, TrendingUp, TrendingDown,
    PieChart, Bitcoin, Landmark, Smartphone, X, Check,
    Coffee, Gift, Heart, Music, Plane, Book, Briefcase, Zap
} from 'lucide-vue-next';

const router = useRouter();
const goBack = () => router.back();

// --- CONFIGURAÇÃO ---
const API_URL = 'http://localhost:8000/api/v1/categories';

// --- ESTADO ---
const activeTab = ref('expense'); 
const showModal = ref(false);
const isEditing = ref(false);
const isLoading = ref(false);
const categories = ref([]);
const activeMenuId = ref(null); 

// --- OPÇÕES VISUAIS ---
const availableColors = [
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-500', 
    'bg-teal-500', 'bg-cyan-500', 'bg-blue-500', 'bg-indigo-500', 
    'bg-purple-500', 'bg-pink-500', 'bg-rose-500', 'bg-zinc-500'
];

const availableIcons = [
    { name: 'Utensils', component: Utensils },
    { name: 'ShoppingCart', component: ShoppingCart },
    { name: 'Car', component: Car },
    { name: 'Home', component: Home },
    { name: 'Smartphone', component: Smartphone },
    { name: 'Coffee', component: Coffee },
    { name: 'Gift', component: Gift },
    { name: 'Heart', component: Heart },
    { name: 'Music', component: Music },
    { name: 'Plane', component: Plane },
    { name: 'Book', component: Book },
    { name: 'Briefcase', component: Briefcase },
    { name: 'Zap', component: Zap },
    { name: 'Tag', component: Tag },
    { name: 'TrendingUp', component: TrendingUp },
    { name: 'PieChart', component: PieChart },
    { name: 'Landmark', component: Landmark },
];

const form = ref({ id: null, name: '', type: 'expense', color: 'bg-zinc-500', icon: 'Tag' });

// --- API ---
const fetchCategories = async () => {
    try {
        const response = await fetch(API_URL + '/');
        if (response.ok) categories.value = await response.json();
    } catch (e) { console.error(e); }
};

const saveCategory = async () => {
    if (!form.value.name) return alert('Digite um nome');
    isLoading.value = true;
    const payload = { name: form.value.name, type: form.value.type, color: form.value.color, icon: form.value.icon };

    try {
        let response;
        if (isEditing.value && form.value.id) {
            response = await fetch(`${API_URL}/${form.value.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        } else {
            response = await fetch(API_URL + '/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        }
        if (response.ok) { await fetchCategories(); closeModal(); }
    } catch (e) { console.error(e); } 
    finally { isLoading.value = false; }
};

const deleteCategory = async (category) => {
    activeMenuId.value = null;
    try {
        const response = await fetch(`${API_URL}/${category.id}`, { method: 'DELETE' });
        if (response.ok) categories.value = categories.value.filter(c => c.id !== category.id);
    } catch (e) { console.error(e); }
};

const getIconComponent = (iconName) => {
    const found = availableIcons.find(i => i.name === iconName);
    return found ? found.component : Tag;
};

const filteredCategories = computed(() => categories.value.filter(c => c.type === activeTab.value));

const openModal = (category = null) => {
    activeMenuId.value = null;
    if (category) {
        isEditing.value = true;
        form.value = { ...category };
    } else {
        isEditing.value = false;
        form.value = { id: null, name: '', type: activeTab.value, color: 'bg-zinc-500', icon: 'Tag' };
    }
    showModal.value = true;
};

const closeModal = () => { showModal.value = false; };
const selectIcon = (iconName) => { form.value.icon = iconName; };
const toggleMenu = (id) => { activeMenuId.value = activeMenuId.value === id ? null : id; };

onMounted(fetchCategories);
</script>

<template>
  <div class="h-screen w-full bg-[var(--bg-app)] text-[var(--text-main)] font-sans transition-colors duration-300 flex overflow-hidden relative">
    
    <div v-if="activeMenuId" @click="activeMenuId = null" class="fixed inset-0 z-30 bg-transparent"></div>

    <div class="hidden lg:flex h-full shrink-0 z-10">
        <SidebarDesktop />
    </div>

    <div class="flex-1 flex flex-col h-full overflow-hidden relative">
        
        <div class="lg:hidden px-4 py-4 flex items-center justify-between bg-[var(--bg-surface)] border-b border-[var(--border)] sticky top-0 z-20 shadow-sm shrink-0">
            <div class="flex items-center gap-3">
                <button @click="goBack" class="p-2 -ml-2 rounded-full hover:bg-[var(--bg-app)] transition-colors active:scale-95 text-[var(--text-main)]">
                    <ChevronLeft :size="22" />
                </button>
                <h1 class="text-lg font-bold tracking-tight">Categorias</h1>
            </div>
            <button @click="openModal()" class="p-2 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] active:bg-[var(--color-primary)]/20">
                <Plus :size="20" />
            </button>
        </div>

        <header class="hidden lg:flex h-16 px-8 mx-6 mt-4 items-center justify-between bg-[var(--bg-surface)]/80 backdrop-blur-md border border-[var(--border)] flex-shrink-0 transition-colors rounded-2xl shadow-sm">
             <div class="flex items-center gap-3 text-[var(--text-main)]">
                <div class="p-1.5 rounded-md bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    <Tag :size="20" />
                </div>
                <h1 class="text-lg font-bold tracking-tight">Gestão de Categorias</h1>
             </div>
             <button @click="openModal()" class="flex items-center gap-2 bg-[var(--color-primary)] hover:brightness-110 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-[var(--color-primary)]/20 active:scale-95">
                <Plus :size="16" /> Nova Categoria
             </button>
        </header>

        <div class="flex-1 overflow-y-auto p-4 lg:p-6 pb-32 lg:pb-8 custom-scroll">
            <div class="w-full lg:max-w-5xl space-y-6">

                <div class="bg-[var(--bg-surface)] p-1 rounded-xl border border-[var(--border)] inline-flex relative flex-wrap sm:flex-nowrap w-full sm:w-auto">
                    <button @click="activeTab = 'expense'"
                        class="px-4 sm:px-6 py-2 rounded-lg text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2 flex-1 sm:flex-none"
                        :class="activeTab === 'expense' ? 'bg-[var(--color-danger)] text-white shadow-md' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                        <TrendingDown :size="16" /> Despesas
                    </button>
                    <button @click="activeTab = 'income'"
                        class="px-4 sm:px-6 py-2 rounded-lg text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2 flex-1 sm:flex-none"
                        :class="activeTab === 'income' ? 'bg-[var(--color-success)] text-white shadow-md' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                        <TrendingUp :size="16" /> Receitas
                    </button>
                    <button @click="activeTab = 'investment'"
                        class="px-4 sm:px-6 py-2 rounded-lg text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2 flex-1 sm:flex-none"
                        :class="activeTab === 'investment' ? 'bg-[var(--color-warning)] text-white shadow-md' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
                        <PieChart :size="16" /> Investimentos
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pb-24">
                    <div v-for="cat in filteredCategories" :key="cat.id" 
                         class="group bg-[var(--bg-surface)] hover:bg-[var(--bg-hover)] border border-[var(--border)] rounded-xl p-3 flex items-center justify-between transition-all duration-200 hover:border-[var(--color-primary)]/30 hover:shadow-sm cursor-pointer relative"
                         :class="{'z-50 ring-1 ring-[var(--text-muted)]/30': activeMenuId === cat.id}" 
                         @click="openModal(cat)"
                    >
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg flex items-center justify-center text-white shadow-sm shrink-0"
                                 :class="cat.color">
                                <component :is="getIconComponent(cat.icon)" :size="18" />
                            </div>
                            <div>
                                <h3 class="font-bold text-sm text-[var(--text-main)]">{{ cat.name }}</h3>
                            </div>
                        </div>

                        <div class="flex items-center gap-1">
                            
                            <div class="hidden md:flex opacity-0 group-hover:opacity-100 transition-opacity gap-1">
                                <button @click.stop="openModal(cat)" class="p-2 rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-app)] hover:text-[var(--color-primary)] transition-colors">
                                    <Edit2 :size="16" />
                                </button>
                                <button @click.stop="deleteCategory(cat)" class="p-2 rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-app)] hover:text-[var(--color-danger)] transition-colors">
                                    <Trash2 :size="16" />
                                </button>
                            </div>
                            
                            <div class="relative md:hidden">
                                <button @click.stop="toggleMenu(cat.id)" class="p-2 text-[var(--text-muted)] rounded-full active:bg-[var(--bg-app)] transition-colors">
                                    <MoreVertical :size="18" />
                                </button>

                                <div v-if="activeMenuId === cat.id" 
                                     class="absolute right-0 top-8 w-32 bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                                    <button @click.stop="openModal(cat)" class="w-full text-left px-4 py-3 text-sm font-medium hover:bg-[var(--bg-app)] flex items-center gap-2 text-[var(--text-main)] border-b border-[var(--border)]">
                                        <Edit2 :size="14" /> Editar
                                    </button>
                                    <button @click.stop="deleteCategory(cat)" class="w-full text-left px-4 py-3 text-sm font-medium hover:bg-[var(--color-danger)]/10 text-[var(--color-danger)] flex items-center gap-2">
                                        <Trash2 :size="14" /> Excluir
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>

                    <div v-if="filteredCategories.length === 0" class="col-span-full text-center py-12 opacity-50">
                        <p class="text-sm">Nenhuma categoria encontrada para esta aba.</p>
                    </div>
                </div>

            </div>
        </div>

        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-opacity">
            <div class="bg-[var(--bg-surface)] w-full max-w-md rounded-2xl border border-[var(--border)] shadow-2xl flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
                
                <div class="p-4 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-app)] rounded-t-2xl">
                    <h3 class="font-bold text-lg text-[var(--text-main)]">
                        {{ isEditing ? 'Editar Categoria' : 'Nova Categoria' }}
                    </h3>
                    <button @click="closeModal" class="p-2 rounded-full hover:bg-[var(--bg-surface)] text-[var(--text-muted)]">
                        <X :size="20" />
                    </button>
                </div>

                <div class="p-6 overflow-y-auto custom-scroll space-y-6">
                    <div class="space-y-2">
                        <label class="text-xs font-bold text-[var(--text-muted)] uppercase">Nome</label>
                        <input v-model="form.name" type="text" placeholder="Ex: Alimentação" 
                            class="w-full bg-[var(--bg-app)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                            autoFocus
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="text-xs font-bold text-[var(--text-muted)] uppercase">Tipo</label>
                        <div class="flex bg-[var(--bg-app)] p-1 rounded-xl border border-[var(--border)]">
                            <button @click="form.type = 'expense'" class="flex-1 py-2 rounded-lg text-xs font-bold transition-all"
                                :class="form.type === 'expense' ? 'bg-[var(--color-danger)] text-white shadow' : 'text-[var(--text-muted)]'">Despesa</button>
                            <button @click="form.type = 'income'" class="flex-1 py-2 rounded-lg text-xs font-bold transition-all"
                                :class="form.type === 'income' ? 'bg-[var(--color-success)] text-white shadow' : 'text-[var(--text-muted)]'">Receita</button>
                            <button @click="form.type = 'investment'" class="flex-1 py-2 rounded-lg text-xs font-bold transition-all"
                                :class="form.type === 'investment' ? 'bg-[var(--color-warning)] text-white shadow' : 'text-[var(--text-muted)]'">Invest.</button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label class="text-xs font-bold text-[var(--text-muted)] uppercase">Cor</label>
                        <div class="flex flex-wrap gap-3">
                            <button v-for="color in availableColors" :key="color"
                                @click="form.color = color"
                                class="w-8 h-8 rounded-full transition-transform hover:scale-110 flex items-center justify-center ring-2 ring-offset-2 ring-offset-[var(--bg-surface)]"
                                :class="[color, form.color === color ? 'ring-[var(--text-main)]' : 'ring-transparent']"
                            >
                                <Check v-if="form.color === color" :size="14" class="text-white" />
                            </button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label class="text-xs font-bold text-[var(--text-muted)] uppercase">Ícone</label>
                        <div class="grid grid-cols-6 gap-2">
                            <button v-for="(item, idx) in availableIcons" :key="idx"
                                @click="selectIcon(item.name)"
                                class="aspect-square rounded-xl flex items-center justify-center border transition-all hover:bg-[var(--bg-app)]"
                                :class="form.icon === item.name 
                                    ? 'bg-[var(--color-primary)]/10 border-[var(--color-primary)] text-[var(--color-primary)] shadow-sm' 
                                    : 'border-transparent text-[var(--text-muted)]'"
                            >
                                <component :is="item.component" :size="20" />
                            </button>
                        </div>
                    </div>
                </div>

                <div class="p-4 border-t border-[var(--border)] flex justify-end gap-3 bg-[var(--bg-surface)] rounded-b-2xl">
                    <button @click="closeModal" class="px-4 py-2 text-sm font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors">Cancelar</button>
                    <button @click="saveCategory" :disabled="isLoading" 
                            class="px-6 py-2 text-white rounded-xl text-sm font-bold shadow-lg transition-all active:scale-95 disabled:opacity-50 hover:brightness-110"
                            style="background-color: var(--color-primary); box-shadow: 0 4px 6px -1px rgba(var(--color-primary), 0.2);">
                        {{ isLoading ? 'Salvando...' : 'Salvar' }}
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