/**
 * 后台管理布局组件
 */
<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin">
          <span>仪表盘</span>
        </router-link>
        <router-link to="/admin/articles">
          <span>文章管理</span>
        </router-link>
        <router-link to="/admin/categories">
          <span>分类管理</span>
        </router-link>
        <router-link to="/admin/users">
          <span>用户管理</span>
        </router-link>
        <a href="/">
          <span>返回前台</span>
        </a>
        <a href="#" @click.prevent="handleLogout">
          <span>退出登录</span>
        </a>
      </nav>
    </aside>

    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

export default {
  name: 'Admin',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const handleLogout = async () => {
      await authStore.logout();
      router.push('/login');
    };

    return {
      handleLogout
    };
  }
};
</script>
