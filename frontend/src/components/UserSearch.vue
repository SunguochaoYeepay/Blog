<template>
  <div class="user-search">
    <a-card title="用户查询" :bordered="false">
      <a-form layout="inline" :model="queryForm" @finish="handleSearch">
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="queryForm.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="queryForm.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="部门" name="department">
          <a-input v-model:value="queryForm.department" placeholder="请输入部门" />
        </a-form-item>
        <a-form-item label="角色" name="role">
          <a-input v-model:value="queryForm.role" placeholder="请输入角色" />
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit">查询</a-button>
            <a-button @click="resetForm">重置</a-button>
          </a-space>
        </a-form-item>
      </a-form>

      <a-table
        :columns="columns"
        :data-source="users"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="viewUser(record)">查看</a>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import type { TablePaginationConfig } from 'ant-design-vue';
import { searchUsers, type User, type UserQuery } from '../api/user';

export default defineComponent({
  name: 'UserSearch',
  setup() {
    const loading = ref(false);
    const users = ref<User[]>([]);
    const queryForm = reactive<UserQuery>({
      username: '',
      email: '',
      department: '',
      role: '',
    });

    const pagination = reactive<TablePaginationConfig>({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showTotal: (total) => `共 ${total} 条记录`,
    });

    const columns = [
      {
        title: '用户名',
        dataIndex: 'username',
        key: 'username',
      },
      {
        title: '邮箱',
        dataIndex: 'email',
        key: 'email',
      },
      {
        title: '姓名',
        dataIndex: 'full_name',
        key: 'full_name',
      },
      {
        title: '部门',
        dataIndex: 'department',
        key: 'department',
      },
      {
        title: '角色',
        dataIndex: 'role',
        key: 'role',
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at',
      },
      {
        title: '最后登录',
        dataIndex: 'last_login',
        key: 'last_login',
      },
      {
        title: '操作',
        key: 'action',
      },
    ];

    const fetchUsers = async () => {
      loading.value = true;
      try {
        const data = await searchUsers(
          queryForm,
          pagination.current || 1,
          pagination.pageSize || 10
        );
        users.value = data;
      } catch (error) {
        message.error('获取用户列表失败');
      } finally {
        loading.value = false;
      }
    };

    const handleSearch = () => {
      pagination.current = 1;
      fetchUsers();
    };

    const resetForm = () => {
      Object.assign(queryForm, {
        username: '',
        email: '',
        department: '',
        role: '',
      });
      handleSearch();
    };

    const handleTableChange = (pag: TablePaginationConfig) => {
      Object.assign(pagination, pag);
      fetchUsers();
    };

    const viewUser = (user: User) => {
      message.info(`查看用户：${user.username}`);
    };

    return {
      loading,
      users,
      queryForm,
      columns,
      pagination,
      handleSearch,
      resetForm,
      handleTableChange,
      viewUser,
    };
  },
});
</script>

<style scoped>
.user-search {
  padding: 24px;
}

.ant-form {
  margin-bottom: 24px;
}
</style> 