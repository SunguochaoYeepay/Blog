<!-- 保持模板部分不变 -->
<template>
  <div class="user-edit">
    <a-card :bordered="false" :title="isEdit ? '编辑用户' : '新增用户'">
      <a-form
        ref="formRef"
        :model="formState"
        :rules="rules"
        layout="vertical"
        @finish="handleSubmit"
      >
        <!-- 头像上传区域 -->
        <div class="avatar-upload-container">
          <div class="avatar-preview">
            <img v-if="previewUrl" :src="previewUrl" alt="Avatar Preview" />
            <a-avatar v-else :style="{ backgroundColor: getAvatarColor(formState.username) }" :size="100">
              {{ formState.username ? formState.username.charAt(0).toUpperCase() : 'U' }}
            </a-avatar>
          </div>
          <div class="avatar-upload-action">
            <a-upload
              name="avatar"
              :show-upload-list="false"
              :before-upload="beforeAvatarUpload"
              :customRequest="handleCustomUpload"
              :action="null"
            >
              <a-button>
                <template #icon><UploadOutlined /></template>
                更换头像
              </a-button>
            </a-upload>
          </div>
        </div>

        <!-- 基本信息表单 -->
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item name="username" label="用户名" required>
              <a-input 
                v-model:value="formState.username" 
                placeholder="请输入用户名"
                :disabled="isEdit"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item name="email" label="邮箱" required>
              <a-input 
                v-model:value="formState.email" 
                placeholder="请输入邮箱"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item name="full_name" label="姓名" required>
              <a-input 
                v-model:value="formState.full_name" 
                placeholder="请输入姓名"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item name="role" label="角色" required>
              <a-select
                v-model:value="formState.role"
                placeholder="请选择角色"
                :options="roleOptions"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item name="password" :label="isEdit ? '密码（不填则不修改）' : '密码'" :required="!isEdit">
              <a-input-password 
                v-model:value="formState.password" 
                placeholder="请输入密码"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item name="department" label="部门">
              <a-input 
                v-model:value="formState.department" 
                placeholder="请输入部门"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item name="phone" label="电话">
              <a-input 
                v-model:value="formState.phone" 
                placeholder="请输入电话号码"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item name="bio" label="个人简介">
              <a-textarea 
                v-model:value="formState.bio" 
                placeholder="请输入个人简介"
                :rows="4"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="submitting">保存</a-button>
            <a-button @click="goBack">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue/es';
import userApi from '@/api/user';
import { 
  UploadOutlined,
  UserOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const formRef = ref();
const submitting = ref(false);
const previewUrl = ref('');
const avatarFile = ref<File | null>(null);

// 判断是否为编辑模式
const isEdit = computed(() => {
  return route.params.id !== undefined;
});

// 用户ID
const userId = computed(() => {
  return isEdit.value ? Number(route.params.id) : undefined;
});

// 角色选项
const roleOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'user', label: '普通用户' }
];

// 表单状态
const formState = reactive<{
  username: string;
  email: string;
  password: string;
  role: string;
  department: string;
  phone: string;
  bio: string;
  avatar: string;
  full_name: string;
}>({
  username: '',
  email: '',
  password: '',
  role: 'user',
  department: '',
  phone: '',
  bio: '',
  avatar: '',
  full_name: ''
});

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
};

// 获取用户信息
const fetchUserData = async () => {
  if (!isEdit.value || !userId.value) return;
  
  try {
    const response = await userApi.getById(userId.value);
    const user = response.data;
    Object.assign(formState, {
      username: user.username,
      email: user.email,
      password: '', // 不回显密码
      role: user.role,
      department: user.department || '',
      phone: user.phone || '',
      bio: user.bio || '',
      avatar: user.avatar || '',
      full_name: user.full_name || ''
    });
    
    if (user.avatar) {
      previewUrl.value = user.avatar;
    }
  } catch (error) {
    message.error('获取用户信息失败');
    goBack();
  }
};

// 上传前校验
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

// 处理自定义上传
const handleCustomUpload = ({ file }: { file: File }) => {
  if (beforeAvatarUpload(file)) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const base64 = e.target?.result as string;
      previewUrl.value = base64;
      formState.avatar = base64;
    };
    reader.readAsDataURL(file);
  }
  return false;
};

// 获取头像背景色
const getAvatarColor = (username: string) => {
  if (!username) return '#1890ff';
  
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae'];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

// 处理表单提交
const handleSubmit = async (values: any) => {
  if (submitting.value) return;
  submitting.value = true;
  
  try {
    const submitData = { ...values };
    
    if (isEdit.value && userId.value) {
      // 编辑模式：只发送一个更新请求，包含所有数据（包括头像）
      await userApi.update(userId.value, submitData);
      message.success('更新成功');
    } else {
      // 创建模式
      await userApi.create(submitData);
      message.success('创建成功');
    }
    
    goBack();
  } catch (error: any) {
    message.error(error.response?.data?.message || '操作失败');
  } finally {
    submitting.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.push('/admin/user');
};

// 组件挂载时获取用户数据
onMounted(() => {
  if (isEdit.value) {
    fetchUserData();
  }
});
</script>

<style scoped>
.user-edit {
  padding: 24px;
  background: #f0f2f5;
}

.avatar-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.avatar-preview {
  margin-bottom: 16px;
  
  img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
  }
}

.avatar-upload-action {
  display: flex;
  gap: 8px;
}
</style>