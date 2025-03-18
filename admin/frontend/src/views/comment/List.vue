<template>
  <base-list
    :columns="columns"
    :data-source="commentList"
    :loading="loading"
    :pagination="pagination"
    :search-form="searchForm"
    @search="handleSearch"
    @reset="handleReset"
    @table-change="handleTableChange"
  >
    <!-- 搜索表单 -->
    <template #search-form>
      <a-form-item label="评论内容">
        <a-input
          v-model:value="searchForm.keyword"
          placeholder="评论内容"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="文章标题">
        <a-input
          v-model:value="searchForm.article_title"
          placeholder="文章标题"
          allow-clear
        />
      </a-form-item>
      <a-form-item label="状态">
        <a-select
          v-model:value="searchForm.status"
          style="width: 120px"
          :options="COMMENT_STATUS_OPTIONS"
        />
      </a-form-item>
      <a-form-item label="时间范围">
        <a-range-picker
          v-model:value="dateRange"
          @change="onDateRangeChange"
        />
      </a-form-item>
    </template>

    <!-- 表格列内容 -->
    <template #column-content="{ column, record }">
      <template v-if="column.key === 'content'">
        <div class="comment-content" @click="handleViewDetail(record)">
          {{ record.content }}
        </div>
      </template>

      <template v-if="column.key === 'status'">
        <a-tag :color="getStatusColor(record)">
          {{ getStatusText(record) }}
        </a-tag>
      </template>

      <template v-if="column.key === 'action'">
        <a-space>
          <a-button type="link" @click="handleViewDetail(record)">
            查看
          </a-button>
          <a-button
            v-if="!record.is_approved && !record.is_spam"
            type="link"
            @click="handleApprove(record)"
          >
            通过
          </a-button>
          <a-button
            v-if="!record.is_spam"
            type="link"
            danger
            @click="handleMarkSpam(record)"
          >
            标记垃圾
          </a-button>
          <a-popconfirm
            title="确定要删除这条评论吗？"
            @confirm="handleDelete(record)"
            ok-text="确定"
            cancel-text="取消"
          >
            <a-button type="link" danger>删除</a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </template>
  </base-list>

  <!-- 评论详情弹窗 -->
  <comment-detail
    v-model:visible="detailVisible"
    :comment="currentComment"
    @deleted="handleSearch"
  />
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { TablePaginationConfig } from 'ant-design-vue/es/table/interface'
import type { CommentResponse, CommentQuery } from '@/types/comment'
import type { PageResponse, ApiResponse } from '@/types/response'
import { COMMENT_STATUS_OPTIONS } from '@/types/comment'
import { getComments, approveComment, markCommentAsSpam, deleteComment } from '@/api/comment'
import { message } from 'ant-design-vue/es'
import dayjs from 'dayjs'
import BaseList from '@/components/BaseList.vue'
import CommentDetail from './Detail.vue'

// 搜索表单数据
const searchForm = reactive<CommentQuery>({
  keyword: '',
  article_title: '',
  status: 'all',
  start_date: undefined,
  end_date: undefined,
  page: 1,
  size: 10
})

// 日期范围
const dateRange = ref<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)

// 评论列表数据
const commentList = ref<CommentResponse[]>([])
const loading = ref(false)
const pagination = reactive<TablePaginationConfig>({
  total: 0,
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showQuickJumper: true
})

// 详情弹窗控制
const detailVisible = ref(false)
const currentComment = ref<CommentResponse | null>(null)

// 表格列定义
const columns = [
  {
    title: '评论内容',
    dataIndex: 'content',
    key: 'content',
    width: '30%',
    className: 'comment-content-cell'
  },
  {
    title: '文章标题',
    dataIndex: 'article_title',
    key: 'article_title',
    width: '20%'
  },
  {
    title: '评论用户',
    dataIndex: 'user_name',
    key: 'user_name',
    width: '10%'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '10%'
  },
  {
    title: '评论时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: '15%'
  },
  {
    title: '操作',
    key: 'action',
    width: '15%',
    className: 'operation-column'
  }
]

// 获取评论列表
const fetchCommentList = async () => {
  loading.value = true
  try {
    const response = await getComments(searchForm)
    const { items, total, page, size } = response.data
    commentList.value = items
    pagination.total = total
    pagination.current = page
    pagination.pageSize = size
  } catch (error) {
    message.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  fetchCommentList()
}

// 重置搜索条件
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.article_title = ''
  searchForm.status = 'all'
  dateRange.value = null
  searchForm.start_date = undefined
  searchForm.end_date = undefined
  handleSearch()
}

// 日期范围变化
const onDateRangeChange = (dates: [dayjs.Dayjs, dayjs.Dayjs] | null) => {
  if (dates) {
    searchForm.start_date = dates[0].format('YYYY-MM-DD')
    searchForm.end_date = dates[1].format('YYYY-MM-DD')
  } else {
    searchForm.start_date = undefined
    searchForm.end_date = undefined
  }
}

// 表格变化事件
const handleTableChange = (pag: TablePaginationConfig) => {
  searchForm.page = pag.current || 1
  searchForm.size = pag.pageSize
  fetchCommentList()
}

// 获取状态文本
const getStatusText = (record: CommentResponse) => {
  if (record.is_spam) return '垃圾评论'
  if (record.is_approved) return '已通过'
  return '待审核'
}

// 获取状态标签颜色
const getStatusColor = (record: CommentResponse) => {
  if (record.is_spam) return 'red'
  if (record.is_approved) return 'green'
  return 'orange'
}

// 查看详情
const handleViewDetail = (record: CommentResponse) => {
  currentComment.value = record
  detailVisible.value = true
}

// 通过评论
const handleApprove = async (record: CommentResponse) => {
  try {
    await approveComment(record.id)
    message.success('评论已通过')
    fetchCommentList()
  } catch (error) {
    message.error('操作失败')
  }
}

// 标记垃圾评论
const handleMarkSpam = async (record: CommentResponse) => {
  try {
    await markCommentAsSpam(record.id)
    message.success('已标记为垃圾评论')
    fetchCommentList()
  } catch (error) {
    message.error('操作失败')
  }
}

// 删除评论
const handleDelete = async (record: CommentResponse) => {
  try {
    await deleteComment(record.id)
    message.success('评论已删除')
    fetchCommentList()
  } catch (error) {
    message.error('删除失败')
  }
}

// 初始化
onMounted(() => {
  fetchCommentList()
})
</script>

<style scoped>
.comment-content {
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  cursor: pointer;
  color: #1890ff;
}

.comment-content:hover {
  text-decoration: underline;
}
</style>