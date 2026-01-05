/**
 * 注册组件
 */
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>注册</h1>

      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>

      <form @submit.prevent="handleRegister" v-if="!success">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="form-control"
            required
            minlength="3"
            maxlength="20"
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="form-control"
            required
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
            minlength="8"
          />
          <small style="color: var(--text-light)">至少8个字符，包含大小写字母、数字和特殊字符</small>
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            class="form-control"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="auth-links" v-if="success">
        <a href="/login" class="btn btn-primary">立即登录</a>
      </div>

      <div class="auth-links" v-if="!success">
        <p>已有账号？<a href="/login">立即登录</a></p>
        <p><a href="/">返回首页</a></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { authApi } from '../api/auth';

export default {
  name: 'Register',
  setup() {
    const username = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const error = ref('');
    const success = ref('');
    const loading = ref(false);

    const router = useRouter();
    const authStore = useAuthStore();

    const handleRegister = async () => {
      error.value = '';
      success.value = '';

      if (password.value !== confirmPassword.value) {
        error.value = '两次输入的密码不一致';
        return;
      }

      loading.value = true;

      try {
        // 先注册
        await authApi.register({
          username: username.value,
          email: email.value,
          password: password.value
        });

        // 自动登录
        await authStore.login(username.value, password.value);

        success.value = '注册成功！正在跳转到首页...';
        setTimeout(() => {
          router.push('/');
        }, 1500);
      } catch (e) {
        error.value = e.response?.data?.error || '注册失败，请稍后重试';
      } finally {
        loading.value = false;
      }
    };

    return {
      username,
      email,
      password,
      confirmPassword,
      error,
      success,
      loading,
      handleRegister
    };
  }
};
</script>
