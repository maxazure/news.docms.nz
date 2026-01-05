/**
 * Vue 3 应用入口
 */
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';

// 导入样式
import '../css/main.css';
import '../css/admin.css';

// 导入视图组件
import Home from './views/Home.vue';
import Article from './views/Article.vue';
import Login from './views/Login.vue';
import Register from './views/Register.vue';
import Profile from './views/Profile.vue';
import Admin from './views/Admin.vue';
import AdminDashboard from './views/AdminDashboard.vue';
import AdminArticles from './views/AdminArticles.vue';
import AdminArticleEdit from './views/AdminArticleEdit.vue';
import AdminUsers from './views/AdminUsers.vue';
import AdminCategories from './views/AdminCategories.vue';

// 导入状态管理
import { useAuthStore } from './stores/auth';

// 创建 Pinia
const pinia = createPinia();

// 创建路由
const routes = [
  { path: '/', component: Home, name: 'home' },
  { path: '/article/:slug', component: Article, name: 'article' },
  { path: '/login', component: Login, name: 'login' },
  { path: '/register', component: Register, name: 'register' },
  { path: '/profile', component: Profile, name: 'profile' },
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', component: AdminDashboard, name: 'admin-dashboard' },
      { path: 'articles', component: AdminArticles, name: 'admin-articles' },
      { path: 'articles/new', component: AdminArticleEdit, name: 'admin-article-new' },
      { path: 'articles/:id/edit', component: AdminArticleEdit, name: 'admin-article-edit' },
      { path: 'users', component: AdminUsers, name: 'admin-users' },
      { path: 'categories', component: AdminCategories, name: 'admin-categories' }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 检查是否已登录
  if (!authStore.token) {
    const token = localStorage.getItem('access_token');
    if (token) {
      authStore.token = token;
      await authStore.checkAuth();
    }
  }

  // 需要认证的页面
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' });
    return;
  }

  next();
});

// 创建并挂载应用
const app = createApp({
  setup() {
    return {};
  },
  template: '<router-view />'
});

app.use(pinia);
app.use(router);
app.mount('#app');
