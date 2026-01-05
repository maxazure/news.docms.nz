/**
 * 登录组件
 */
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>登录</h1>

      <div v-if="error" class="error-message">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名或邮箱</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="form-control"
            required
            autofocus
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="form-control"
            required
          />
        </div>

        <div class="form-group">
          <label>
            <input type="checkbox" v-model="remember" /> 记住我
          </label>
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="auth-links">
        <p>还没有账号？<a href="/register">立即注册</a></p>
        <p><a href="/">返回首页</a></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

export default {
  name: 'Login',
  setup() {
    const username = ref('');
    const password = ref('');
    const remember = ref(false);
    const error = ref('');
    const loading = ref(false);

    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();

    const handleLogin = async () => {
      error.value = '';
      loading.value = true;

      try {
        await authStore.login(username.value, password.value);
        const redirect = route.query.redirect || '/';
        router.push(redirect);
      } catch (e) {
        error.value = e.response?.data?.error || '登录失败，请检查用户名和密码';
      } finally {
        loading.value = false;
      }
    };

    return {
      username,
      password,
      remember,
      error,
      loading,
      handleLogin
    };
  }
};
</script>
