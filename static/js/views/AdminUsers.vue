/**
 * 后台用户管理组件
 */
<template>
  <div class="admin-users">
    <div class="admin-header">
      <h1>用户管理</h1>
    </div>

    <div class="data-table">
      <table v-if="users.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="role-badge" :class="'role-' + user.role">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>
              <span :style="{ color: user.is_active ? 'green' : 'red' }">
                {{ user.is_active ? '正常' : '禁用' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td class="table-actions">
              <button
                v-if="user.id !== currentUserId"
                @click="toggleUserStatus(user)"
                class="btn btn-small"
                :class="user.is_active ? 'btn-danger' : 'btn-success'"
              >
                {{ user.is_active ? '禁用' : '启用' }}
              </button>
              <span v-else style="color: var(--text-light)">自己</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data">暂无用户</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { usersApi } from '../api/users';
import { useAuthStore } from '../stores/auth';

export default {
  name: 'AdminUsers',
  setup() {
    const users = ref([]);
    const authStore = useAuthStore();

    const currentUserId = computed(() => authStore.user?.id);

    const fetchUsers = async () => {
      try {
        const response = await usersApi.getList();
        users.value = response.data.users;
      } catch (e) {
        console.error('Failed to fetch users:', e);
      }
    };

    const toggleUserStatus = async (user) => {
      if (!confirm(`确定要${user.is_active ? '禁用' : '启用'}用户 "${user.username}" 吗？`)) return;

      try {
        await usersApi.toggleActive(user.id);
        fetchUsers();
      } catch (e) {
        alert(e.response?.data?.error || '操作失败');
      }
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('zh-CN');
    };

    onMounted(() => {
      fetchUsers();
    });

    return {
      users,
      currentUserId,
      toggleUserStatus,
      formatDate
    };
  }
};
</script>

<style scoped>
.no-data {
  text-align: center;
  padding: 30px;
  color: var(--text-light);
}
</style>
