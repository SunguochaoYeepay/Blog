<template>
  <div class="user-list">
    <!-- 搜索区域 -->
    <a-card class="search-card" :bordered="false">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="用户名">
          <a-input
            v-model:value="searchForm.username"
            placeholder="请输入用户名"
            allow-clear
            @pressEnter="handleSearch"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input
            v-model:value="searchForm.email"
            placeholder="请输入邮箱"
            allow-clear
            @pressEnter="handleSearch"
          >
            <template #prefix>
              <MailOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item label="角色">
          <a-select
            v-model:value="searchForm.role"
            placeholder="请选择角色"
            style="width: 120px"
            allow-clear
          >
            <a-select-option v-for="option in roleOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleSearch">
              <template #icon><SearchOutlined /></template>
              搜索
            </a-button>
            <a-button @click="handleReset">
              <template #icon><ReloadOutlined /></template>
              重置
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 表格区域 -->
    <a-card class="table-card" :bordered="false">
      <template #title>
        <div class="table-toolbar">
          <div class="toolbar-title">
            用户列表
            <a-tag v-if="total" color="blue">{{ total }} 人</a-tag>
          </div>
          <div class="toolbar-buttons">
            <a-space>
              <a-button type="primary" @click="handleCreate">
                <template #icon><UserAddOutlined /></template>
                创建用户
              </a-button>
              <a-button 
                danger 
                :disabled="!selectedRowKeys.length"
                @click="handleBatchDelete"
              >
                <template #icon><DeleteOutlined /></template>
                批量删除
              </a-button>
            </a-space>
          </div>
        </div>
      </template>

      <a-table
        :columns="columns"
        :data-source="users"
        :loading="loading"
        :pagination="pagination"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :row-key="record => record.id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record, text }: { column: { key: string }; record: User; text: string }">
          <template v-if="column.key === 'username'">
            <div class="user-cell">
              <div class="avatar-wrapper" @click="handleEditAvatar(record)">
                <a-avatar 
                  :src="record.avatar"
                  :style="{ backgroundColor: !record.avatar ? getAvatarColor(record.username) : 'transparent' }"
                >
                  {{ !record.avatar ? record.username.charAt(0).toUpperCase() : '' }}
                </a-avatar>
                <div class="avatar-edit-overlay">
                  <EditOutlined />
                </div>
              </div>
              <div class="user-info">
                <div class="username">{{ record.username }}</div>
                <div class="email">{{ record.email }}</div>
              </div>
            </div>
          </template>
          <template v-else-if="column.key === 'role'">
            <a-tag :color="getRoleTagColor(text)">
              {{ getRoleLabel(text) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-badge :status="getUserStatus(record).status" :text="getUserStatus(record).text" />
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" @click="handleEdit(record.id)">编辑</a-button>
              <a-divider type="vertical" />
              <a-button type="link" danger @click="handleDelete(record.id)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 头像编辑模态框 -->
    <a-modal
      v-model:visible="avatarModalVisible"
      title="编辑头像"
      :footer="null"
      @cancel="handleAvatarCancel"
    >
      <div class="avatar-upload">
        <div class="avatar-preview">
          <img v-if="previewUrl" :src="previewUrl" alt="Avatar Preview" />
          <div v-else class="avatar-placeholder">
            <UserOutlined />
            <span>暂无头像</span>
          </div>
        </div>
        <div class="upload-actions">
          <a-upload
            name="avatar"
            :show-upload-list="false"
            :before-upload="beforeAvatarUpload"
            @change="handleAvatarChange"
          >
            <a-button type="primary">
              <template #icon><UploadOutlined /></template>
              选择图片
            </a-button>
          </a-upload>
          <a-button 
            type="primary"
            :disabled="!previewUrl"
            @click="handleAvatarSubmit"
            :loading="uploadLoading"
          >
            保存头像
          </a-button>
        </div>
        <div class="upload-tips">
          <p>支持 jpg、png 格式，文件大小不超过 2MB</p>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { 
  UserOutlined,
  MailOutlined,
  TeamOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined
} from '@ant-design/icons-vue';
import userApi from '@/api/user';
import type { User } from '@/api/user';
import type { TableProps } from 'ant-design-vue/es/table';

const router = useRouter();
const loading = ref(false);
const users = ref<User[]>([]);
const total = ref(0);
const selectedRowKeys = ref<number[]>([]);
const searchForm = ref({
  username: '',
  email: '',
  role: undefined as string | undefined,
});

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: (total: number) => `共 ${total} 条记录`,
  showSizeChanger: true,
  showQuickJumper: true,
});

// 角色选项
const roleOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'editor', label: '编辑' },
  { value: 'user', label: '普通用户' }
];

// 表格列定义
const columns = [
  {
    title: '用户信息',
    dataIndex: 'username',
    key: 'username',
    width: '25%',
  },
  {
    title: '角色',
    dataIndex: 'role',
    key: 'role',
    width: '15%',
    filters: roleOptions.map(option => ({
      text: option.label,
      value: option.value
    })),
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '15%',
  },
  {
    title: '最后登录',
    dataIndex: 'last_login',
    key: 'last_login',
    width: '20%',
    sorter: true,
    customRender: ({ text }: { text: string | null }) => formatDate(text)
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
  }
];

// 加载用户列表
const loadUsers = async () => {
  try {
    loading.value = true;
    const page = pagination.value.current || 1;
    const size = pagination.value.pageSize || 10;
    const response = await userApi.list({
      page,
      size,
      ...searchForm.value
    });
    users.value = response.data.items;
    total.value = response.data.total;
    pagination.value.total = response.data.total;
  } catch (error) {
    console.error('加载用户列表失败:', error);
    message.error('加载用户列表失败');
  } finally {
    loading.value = false;
  }
};

// 处理搜索
const handleSearch = () => {
  pagination.value.current = 1;
  loadUsers();
};

// 处理重置
const handleReset = () => {
  searchForm.value = {
    username: '',
    email: '',
    role: undefined,
  };
  pagination.value.current = 1;
  loadUsers();
};

// 处理表格变化
const handleTableChange: TableProps['onChange'] = (pag, filters, sorter) => {
  pagination.value.current = pag?.current || 1;
  pagination.value.pageSize = pag?.pageSize || 10;
  
  if (filters?.role?.length) {
    searchForm.value.role = filters.role[0] as string;
  } else {
    searchForm.value.role = undefined;
  }
  
  loadUsers();
};

// 处理选择变化
const onSelectChange = (selectedKeys: number[]) => {
  selectedRowKeys.value = selectedKeys;
};

// 处理创建
const handleCreate = () => {
  router.push('/admin/user/create');
};

// 处理编辑
const handleEdit = (id: number) => {
  router.push(`/admin/user/edit/${id}`);
};

// 处理删除
const handleDelete = (id: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个用户吗？',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await userApi.delete(id);
        message.success('删除成功');
        loadUsers();
      } catch (error) {
        message.error('删除失败');
      }
    },
  });
};

// 处理批量删除
const handleBatchDelete = () => {
  if (!selectedRowKeys.value.length) {
    message.warning('请选择要删除的用户');
    return;
  }

  Modal.confirm({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个用户吗？`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await userApi.batchDelete(selectedRowKeys.value);
        message.success('批量删除成功');
        selectedRowKeys.value = [];
        loadUsers();
      } catch (error) {
        message.error('批量删除失败');
      }
    },
  });
};

// 头像相关
const avatarModalVisible = ref(false);
const previewUrl = ref('');
const currentUser = ref<User | null>(null);
const uploadLoading = ref(false);

const handleEditAvatar = (user: User) => {
  currentUser.value = user;
  previewUrl.value = user.avatar || '';
  avatarModalVisible.value = true;
};

const handleAvatarCancel = () => {
  avatarModalVisible.value = false;
  previewUrl.value = '';
  currentUser.value = null;
};

const compressImage = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        // 计算缩放比例，限制最大尺寸为 200x200
        const maxSize = 200;
        if (width > height && width > maxSize) {
          height = Math.round((height * maxSize) / width);
          width = maxSize;
        } else if (height > maxSize) {
          width = Math.round((width * maxSize) / height);
          height = maxSize;
        }
        
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0, width, height);
        
        // 压缩为 JPEG 格式，质量 0.8
        resolve(canvas.toDataURL('image/jpeg', 0.8));
      };
      img.onerror = reject;
      img.src = e.target?.result as string;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

const beforeAvatarUpload = (file: File) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 格式的图片！');
    return false;
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB！');
    return false;
  }
  return true;
};

const handleAvatarChange = async (info: any) => {
  if (info.file.status !== 'uploading') {
    try {
      const compressedImage = await compressImage(info.file.originFileObj);
      previewUrl.value = compressedImage;
    } catch (error) {
      message.error('图片处理失败');
    }
  }
};

const handleAvatarSubmit = async () => {
  if (!currentUser.value || !previewUrl.value) return;
  
  try {
    uploadLoading.value = true;
    await userApi.updateAvatar(currentUser.value.id, previewUrl.value);
    message.success('头像更新成功');
    loadUsers();
    handleAvatarCancel();
  } catch (error) {
    message.error('头像更新失败');
  } finally {
    uploadLoading.value = false;
  }
};

// 工具函数
const getRoleTagColor = (role: string) => {
  const colorMap: Record<string, string> = {
    admin: 'red',
    editor: 'green',
    user: 'blue',
  };
  return colorMap[role] || 'default';
};

const getRoleLabel = (role: string) => {
  const option = roleOptions.find(opt => opt.value === role);
  return option ? option.label : role;
};

const getUserStatus = (user: User) => {
  const lastLogin = user.last_login ? new Date(user.last_login) : null;
  const now = new Date();
  
  if (!lastLogin) {
    return { status: 'default', text: '未登录' };
  }
  
  const diff = now.getTime() - lastLogin.getTime();
  if (diff < 30 * 60 * 1000) { // 30分钟内
    return { status: 'success', text: '在线' };
  } else if (diff < 24 * 60 * 60 * 1000) { // 24小时内
    return { status: 'warning', text: '离线' };
  } else {
    return { status: 'default', text: '长期未登录' };
  }
};

const getAvatarColor = (username: string) => {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae'];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return '从未登录';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    if (hours < 1) {
      const minutes = Math.floor(diff / (60 * 1000));
      return `${minutes} 分钟前`;
    }
    return `${hours} 小时前`;
  }
  
  return date.toLocaleString();
};

onMounted(() => {
  loadUsers();
});
</script>

<style lang="less" scoped>
.user-list {
  .search-card {
    margin-bottom: 16px;
    
    :deep(.ant-card-body) {
      padding: 24px;
    }

    .ant-form {
      .ant-form-item {
        margin-bottom: 0;
        margin-right: 16px;
      }
    }
  }

  .table-card {
    :deep(.ant-card-body) {
      padding: 0;
    }

    :deep(.ant-table-wrapper) {
      .ant-table-pagination {
        margin: 16px;
      }
    }
  }

  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #f0f0f0;

    .toolbar-title {
      font-size: 16px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .user-cell {
    display: flex;
    align-items: center;
    gap: 12px;

    .avatar-wrapper {
      position: relative;
      cursor: pointer;
      
      &:hover .avatar-edit-overlay {
        opacity: 1;
      }

      .avatar-edit-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
        color: white;
      }
    }

    .user-info {
      .username {
        font-weight: 500;
        line-height: 1.5715;
      }

      .email {
        font-size: 12px;
        color: rgba(0, 0, 0, 0.45);
        line-height: 1.5715;
      }
    }
  }

  .avatar-upload {
    text-align: center;

    .avatar-preview {
      width: 200px;
      height: 200px;
      margin: 0 auto 20px;
      border: 1px dashed #d9d9d9;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .avatar-placeholder {
        color: #999;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;

        .anticon {
          font-size: 32px;
        }
      }
    }

    .upload-actions {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-bottom: 16px;
    }

    .upload-tips {
      color: #999;
      font-size: 12px;
    }
  }

  // 响应式调整
  @media screen and (max-width: 768px) {
    .search-card {
      :deep(.ant-form) {
        .ant-form-item {
          margin-bottom: 16px;
          margin-right: 0;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }

    .table-toolbar {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;

      .toolbar-buttons {
        width: 100%;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}
</style>