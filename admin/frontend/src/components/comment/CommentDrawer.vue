<template>
  <a-drawer
    :title="drawerTitle"
    placement="right"
    :width="680"
    :open="visible"
    @close="handleClose"
    :closable="true"
    :body-style="{ paddingBottom: '80px' }"
  >
    <!-- 评论详情区域 -->
    <a-descriptions 
      :column="1" 
      bordered
      size="small"
      class="comment-info"
    >
      <a-descriptions-item label="文章标题">
        <a :href="articleUrl" target="_blank">{{ comment?.article_title }}</a>
      </a-descriptions-item>
      <a-descriptions-item label="评论状态">
        <a-tag :color="getStatusColor(comment)">
          {{ getStatusText(comment) }}
        </a-tag>
      </a-descriptions-item>
      <a-descriptions-item label="评论时间">
        {{ formatDateTime(comment?.created_at) }}
      </a-descriptions-item>
      <a-descriptions-item label="IP地址">
        {{ comment?.ip_address || '-' }}
      </a-descriptions-item>
      <a-descriptions-item label="浏览器信息">
        {{ comment?.user_agent || '-' }}
      </a-descriptions-item>
    </a-descriptions>

    <!-- 评论内容及回复区域 -->
    <div class="comment-thread">
      <!-- 主评论 -->
      <a-comment>
        <template #actions>
          <a-space>
            <a-button 
              v-if="!comment?.is_approved && !comment?.is_spam"
              type="link" 
              @click="() => handleApprove(comment)"
            >
              通过
            </a-button>
            <a-button 
              v-if="!comment?.is_spam"
              type="link" 
              danger 
              @click="() => handleMarkSpam(comment)"
            >
              标记垃圾
            </a-button>
            <a-popconfirm
              title="确定要删除这条评论吗？"
              @confirm="() => handleDelete(comment)"
              ok-text="确定"
              cancel-text="取消"
            >
              <a-button type="link" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
        <template #author>
          <a>{{ comment?.user_name }}</a>
        </template>
        <template #avatar>
          <a-avatar>{{ comment?.user_name?.[0]?.toUpperCase() }}</a-avatar>
        </template>
        <template #content>
          <p>{{ comment?.content }}</p>
        </template>
        <template #datetime>
          <a-tooltip :title="formatDateTime(comment?.created_at)">
            <span>{{ formatDateTime(comment?.created_at) }}</span>
          </a-tooltip>
        </template>
      </a-comment>

      <!-- 回复列表 -->
      <div class="replies-section">
        <a-divider orientation="left">回复列表</a-divider>
        
        <!-- 递归组件：评论回复树 -->
        <comment-tree
          v-if="comment?.replies?.length"
          :comments="comment.replies"
          :loading="repliesLoading"
          @approve="handleApprove"
          @spam="handleMarkSpam"
          @delete="handleDelete"
          @load-replies="handleLoadReplies"
        />
        
        <a-empty v-else description="暂无回复" />
      </div>
    </div>

    <!-- 抽屉底部操作栏 -->
    <div class="drawer-footer">
      <a-space>
        <a-button @click="handleClose">关闭</a-button>
        <a-button 
          type="primary" 
          :loading="loading"
          @click="handleRefresh"
        >
          刷新评论
        </a-button>
      </a-space>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CommentResponse } from '@/types/comment'
import { getCommentTree, approveComment, markCommentAsSpam, deleteComment, getChildComments } from '@/api/comment'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import CommentTree from './CommentTree.vue'

const props = defineProps<{
  visible: boolean
  comment: CommentResponse | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', visible: boolean): void
  (e: 'refresh'): void
}>()

// 状态
const loading = ref(false)
const repliesLoading = ref(false)

// 计算属性
const drawerTitle = computed(() => {
  return `评论详情 ${props.comment ? `#${props.comment.id}` : ''}`
})

const articleUrl = computed(() => {
  return `/articles/${props.comment?.article_id}`
})

// 方法
const handleClose = () => {
  emit('update:visible', false)
}

const handleRefresh = async () => {
  if (!props.comment) return
  loading.value = true
  try {
    await loadCommentTree()
    emit('refresh')
  } finally {
    loading.value = false
  }
}

const loadCommentTree = async () => {
  if (!props.comment) return
  repliesLoading.value = true
  try {
    const response = await getCommentTree(props.comment.article_id)
    // 更新评论树
    emit('refresh')
  } finally {
    repliesLoading.value = false
  }
}

// 加载子评论
const handleLoadReplies = async (comment: CommentResponse) => {
  try {
    const response = await getChildComments(comment.id)
    comment.replies = response.data.items
  } catch (error) {
    message.error('加载回复失败')
  }
}

// 评论操作处理
const handleApprove = async (comment: CommentResponse) => {
  try {
    await approveComment(comment.id)
    message.success('评论已通过审核')
    handleRefresh()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleMarkSpam = async (comment: CommentResponse) => {
  try {
    await markCommentAsSpam(comment.id)
    message.success('已标记为垃圾评论')
    handleRefresh()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleDelete = async (comment: CommentResponse) => {
  try {
    await deleteComment(comment.id)
    message.success('评论已删除')
    handleRefresh()
  } catch (error) {
    message.error('删除失败')
  }
}

// 获取评论状态文本
const getStatusText = (comment: CommentResponse | null) => {
  if (!comment) return ''
  if (comment.is_spam) return '垃圾评论'
  if (comment.is_approved) return '已通过'
  return '待审核'
}

// 获取评论状态颜色
const getStatusColor = (comment: CommentResponse | null) => {
  if (!comment) return ''
  if (comment.is_spam) return 'red'
  if (comment.is_approved) return 'green'
  return 'orange'
}

// 格式化时间
const formatDateTime = (date: string | undefined) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style lang="scss" scoped>
.comment-info {
  margin-bottom: 24px;
}

.comment-thread {
  margin-top: 24px;
}

.replies-section {
  margin-left: 24px;
  margin-top: 16px;
}

.drawer-footer {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 100%;
  border-top: 1px solid #e8e8e8;
  padding: 10px 16px;
  background: #fff;
  text-align: right;
}
</style>