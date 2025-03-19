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
          <a-upload
            v-model:file-list="fileList"
            name="avatar"
            list-type="picture-card"
            class="avatar-uploader"
            :show-upload-list="false"
            :before-upload="beforeAvatarUpload"
            :customRequest="handleCustomUpload"
          >
            <img v-if="previewUrl" :src="previewUrl" alt="avatar" class="avatar" />
            <div v-else>
              <loading-outlined v-if="uploading" />
              <plus-outlined v-else />
              <div class="ant-upload-text">上传头像</div>
            </div>
          </a-upload>
          <div class="upload-tips">
            <p>支持 jpg、png 格式，文件大小不超过 2MB</p>
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
import type { UploadProps } from 'ant-design-vue/es/upload';
import userApi from '@/api/user';
import { 
  PlusOutlined,
  LoadingOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const formRef = ref();
const submitting = ref(false);
const previewUrl = ref('');
const fileList = ref<NonNullable<UploadProps['fileList']>>([]);
const uploading = ref(false);

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
      // 设置文件列表
      fileList.value = [{
        uid: '-1',
        name: 'avatar',
        status: 'done',
        url: user.avatar
      }];
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

// 压缩图片
const compressImage = (file: File): Promise<File> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        // 计算缩放比例，限制最大尺寸为 400x400
        const maxSize = 400;
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
        
        // 转换为 Blob，降低质量到 0.6
        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error('图片压缩失败'));
            return;
          }
          // 检查压缩后的大小是否仍然过大
          if (blob.size / 1024 / 1024 > 1) {
            reject(new Error('压缩后图片仍然过大，请选择更小的图片'));
            return;
          }
          // 创建新的 File 对象
          const compressedFile = new File([blob], file.name, {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });
          resolve(compressedFile);
        }, 'image/jpeg', 0.6); // 使用 JPEG 格式，质量降低到 0.6
      };
      img.onerror = reject;
      const result = e.target?.result;
      if (typeof result !== 'string') {
        reject(new Error('读取图片失败'));
        return;
      }
      img.src = result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// 处理自定义上传
const handleCustomUpload = async ({ file }: { file: File }) => {
  if (beforeAvatarUpload(file)) {
    try {
      uploading.value = true;
      
      // 压缩图片
      const compressedFile = await compressImage(file);
      
      // 创建 FormData
      const formData = new FormData();
      formData.append('file', compressedFile);
      
      // 上传到服务器
      const response = await userApi.updateAvatar(userId.value || 0, compressedFile);
      if (response.code === 200 && response.data?.avatar) {
        message.success('头像上传成功');
        formState.avatar = response.data.avatar;
        previewUrl.value = response.data.avatar;
        // 更新文件列表
        fileList.value = [{
          uid: '-1',
          name: file.name,
          status: 'done',
          url: response.data.avatar
        }];
      } else {
        message.error('头像上传失败');
      }
    } catch (error) {
      message.error('头像上传失败');
      console.error('Upload error:', error);
    } finally {
      uploading.value = false;
    }
  }
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
/* 添加全局样式控制 */
:deep(.ant-modal-body) {
  .avatar-preview {
    max-width: 120px !important;
    max-height: 120px !important;
    margin: 0 auto;
  }
}

.user-edit {
  padding: 24px;
  background: #f0f2f5;
}

.avatar-upload-container {
  text-align: center;
  margin-bottom: 24px;
}

.avatar-uploader {
  :deep(.ant-upload) {
    width: 128px;
    height: 128px;
    margin: 0 auto 8px;
  }

  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
  }

  .avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .ant-upload-text {
    margin-top: 8px;
    color: #666;
  }
}

.upload-tips {
  margin-top: 8px;
  color: #999;
  font-size: 12px;
  text-align: center;
}
</style>