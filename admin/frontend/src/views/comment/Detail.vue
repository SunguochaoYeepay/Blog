<template>
  <div class="comment-detail">
    <a-modal
      :open="visible"
      title="评论详情"
      :footer="null"
      width="700px"
      @cancel="handleClose"
      @update:open="$emit('update:visible', $event)"
    >
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="评论内容">
          {{ comment?.content }}
        </a-descriptions-item>
        <a-descriptions-item label="评论状态">
          <a-tag :color="getStatusColor(comment)">
            {{ getStatusText(comment) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="文章ID">
          {{ comment?.article_id }}
        </a-descriptions-item>
        <a-descriptions-item label="用户ID">
          {{ comment?.user_id }}
        </a-descriptions-item>
        <a-descriptions-item label="IP地址">
          {{ comment?.ip_address || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="浏览器信息">
          {{ comment?.user_agent || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="点赞数">
          {{ comment?.like_count || 0 }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ formatDateTime(comment?.created_at) }}
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          {{ formatDateTime(comment?.updated_at) }}
        </a-descriptions-item>
      </a-descriptions>

      <div class="actions" style="margin-top: 24px; text-align: right;">
        <a-space>
          <a-button @click="handleClose">关闭</a-button>
          <a-popconfirm
            title="确定要删除这条评论吗？"
            @confirm="handleDelete"
            ok-text="确定"
            cancel-text="取消"
          >
            <a-button type="primary" danger>删除评论</a-button>
          </a-popconfirm>
        </a-space>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import type { CommentResponse } from '@/types/comment'
import { deleteComment } from '@/api/comment'
import { message } from 'ant-design-vue/es'
import dayjs from 'dayjs'

const props = defineProps<{
  visible: boolean
  comment: CommentResponse | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', visible: boolean): void
  (e: 'deleted'): void
}>()

const handleClose = () => {
  emit('update:visible', false)
}

const handleDelete = async () => {
  if (!props.comment) return
  
  try {
    await deleteComment(props.comment.id)
    message.success('评论删除成功')
    emit('deleted')
    handleClose()
  } catch (error) {
    message.error('删除评论失败')
  }
}

const getStatusText = (comment: CommentResponse | null) => {
  if (!comment) return ''
  if (comment.is_spam) return '垃圾评论'
  if (comment.is_approved) return '已通过'
  return '待审核'
}

const getStatusColor = (comment: CommentResponse | null) => {
  if (!comment) return ''
  if (comment.is_spam) return 'red'
  if (comment.is_approved) return 'green'
  return 'orange'
}

const formatDateTime = (date: string | undefined) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style scoped>
.comment-detail {
  :deep(.ant-descriptions-item-label) {
    width: 100px;
  }
}
</style> 