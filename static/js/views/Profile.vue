/**
 * 个人中心组件
 */
<template>
  <div class="profile-page">
    <div class="profile-card">
      <h1>个人中心</h1>

      <div class="user-info">
        <div class="info-item">
          <label>用户名</label>
          <span>{{ user?.username }}</span>
        </div>
        <div class="info-item">
          <label>邮箱</label>
          <span>{{ user?.email }}</span>
        </div>
        <div class="info-item">
          <label>角色</label>
          <span class="role-badge" :class="'role-' + user?.role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</span>
        </div>
        <div class="info-item">
          <label>注册时间</label>
          <span>{{ formatDate(user?.created_at) }}</span>
        </div>
      </div>

      <div class="password-section">
        <h2>修改密码</h2>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label for="oldPassword">原密码</label>
            <input
              type="password"
              id="oldPassword"
              v-model="oldPassword"
              class="form-control"
              required
            />
          </div>
          <div class="form-group">
            <label for="newPassword">新密码</label>
            <input
              type="password"
              id="newPassword"
              v-model="newPassword"
              class="form-control"
              required
              minlength="8"
            />
          </div>
          <div class="form-group">
            <label for="confirmNewPassword">确认新密码</label>
            <input
              type="password"
              id="confirmNewPassword"
              v-model="confirmNewPassword"
              class="form-control"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '修改中...' : '修改密码' }}
          </button>
        </form>
      </div>

      <div class="logout-section">
        <button @click="handleLogout" class="btn btn-danger">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { authApi } from '../api/auth';

export default {
  name: 'Profile',
  setup() {
    const oldPassword = ref('');
    const newPassword = ref('');
    const confirmNewPassword = ref('');
    const error = ref('');
    const success = ref('');
    const loading = ref(false);

    const router = useRouter();
    const authStore = useAuthStore();

    const user = computed(() => authStore.user);

    const changePassword = async () => {
      error.value = '';
      success.value = '';

      if (newPassword.value !== confirmNewPassword.value) {
        error.value = '两次输入的新密码不一致';
        return;
      }

      loading.value = true;

      try {
        await authApi.changePassword({
          old_password: oldPassword.value,
          new_password: newPassword.value
        });
        success.value = '密码修改成功';
        oldPassword.value = '';
        newPassword.value = '';
        confirmNewPassword.value = '';
      } catch (e) {
        error.value = e.response?.data?.error || '密码修改失败';
      } finally {
        loading.value = false;
      }
    };

    const handleLogout = async () => {
      await authStore.logout();
      router.push('/');
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('zh-CN');
    };

    onMounted(() => {
      if (!authStore.isLoggedIn) {
        router.push('/login');
      }
    });

    return {
      user,
      oldPassword,
      newPassword,
      confirmNewPassword,
      error,
      success,
      loading,
      changePassword,
      handleLogout,
      formatDate
    };
  }
};
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 30px;
  box-shadow: var(--shadow);
}

.profile-card h1 {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--primary-color);
}

.user-info {
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item label {
  font-weight: 500;
  color: var(--text-light);
}

.password-section {
  margin-bottom: 30px;
}

.password-section h2 {
  font-size: 1.2em;
  margin-bottom: 20px;
}

.logout-section {
  text-align: center;
}

.logout-section .btn {
  width: 100%;
}
</style>
