<template>
  <div class="comment-tree">
    <a-spin :spinning="loading">
      <template v-if="comments.length">
        <a-comment
          v-for="comment in comments"
          :key="comment.id"
          :class="{ 'comment-item': true, [`level-${comment.level}`]: true }"
        >
          <template #actions>
            <a-space>
              <a-button 
                v-if="!comment.is_approved && !comment.is_spam"
                type="link" 
                @click="() => $emit('approve', comment)"
              >
                通过
              </a-button>
              <a-button 
                v-if="!comment.is_spam"
                type="link" 
                danger 
                @click="() => $emit('spam', comment)"
              >
                标记垃圾
              </a-button>
              <a-popconfirm
                title="确定要删除这条评论吗？"
                @confirm="() => $emit('delete', comment)"
                ok-text="确定"
                cancel-text="取消"
              >
                <a-button type="link" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
          
          <template #author>
            <a>{{ comment.user_name }}</a>
            <a-tag :color="getStatusColor(comment)" class="status-tag">
              {{ getStatusText(comment) }}
            </a-tag>
          </template>
          
          <template #avatar>
            <a-avatar>{{ comment.user_name?.[0]?.toUpperCase() }}</a-avatar>
          </template>
          
          <template #content>
            <p>{{ comment.content }}</p>
            <div v-if="comment.reply_count > 0 && !comment.replies" class="reply-actions">
              <a-button 
                type="link" 
                size="small"
                :loading="loadingReplies[comment.id]"
                @click="() => handleLoadReplies(comment)"
              >
                <template #icon><DownOutlined /></template>
                显示 {{ comment.reply_count }} 条回复
              </a-button>
            </div>
          </template>
          
          <template #datetime>
            <a-tooltip :title="formatDateTime(comment.created_at)">
              <span>{{ formatDateTime(comment.created_at) }}</span>
            </a-tooltip>
          </template>

          <!-- 递归渲染子评论 -->
          <comment-tree
            v-if="comment.replies?.length"
            :comments="comment.replies"
            :loading="loading"
            @approve="$emit('approve', $event)"
            @spam="$emit('spam', $event)"
            @delete="$emit('delete', $event)"
            @load-replies="$emit('load-replies', $event)"
          />
        </a-comment>
      </template>
      <a-empty v-else description="暂无评论" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { CommentResponse } from '@/types/comment'
import { DownOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'

const props = defineProps<{
  comments: CommentResponse[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'approve', comment: CommentResponse): void
  (e: 'spam', comment: CommentResponse): void
  (e: 'delete', comment: CommentResponse): void
  (e: 'load-replies', comment: CommentResponse): void
}>()

// 记录正在加载回复的评论ID
const loadingReplies = ref<Record<number, boolean>>({})

// 获取评论状态文本
const getStatusText = (comment: CommentResponse) => {
  if (comment.is_spam) return '垃圾评论'
  if (comment.is_approved) return '已通过'
  return '待审核'
}

// 获取评论状态颜色
const getStatusColor = (comment: CommentResponse) => {
  if (comment.is_spam) return 'red'
  if (comment.is_approved) return 'green'
  return 'orange'
}

// 格式化时间
const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载回复
const handleLoadReplies = async (comment: CommentResponse) => {
  loadingReplies.value[comment.id] = true
  try {
    await emit('load-replies', comment)
  } finally {
    loadingReplies.value[comment.id] = false
  }
}
</script>

<style lang="scss" scoped>
.comment-tree {
  .comment-item {
    margin-bottom: 8px;
    
    // 评论层级缩进
    &.level-1 { margin-left: 24px; }
    &.level-2 { margin-left: 48px; }
    &.level-3 { margin-left: 72px; }
    // 最多支持到第4级评论
    &.level-4 { margin-left: 96px; }
  }

  .status-tag {
    margin-left: 8px;
  }

  .reply-actions {
    margin-top: 8px;
  }

  :deep(.ant-comment-nested) {
    margin-top: 12px;
  }
}
</style>