<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <a-row :gutter="[16, 16]">
      <a-col :span="6" v-for="stat in statistics" :key="stat.title">
        <a-card hoverable>
          <a-statistic
            :title="stat.title"
            :value="stat.value"
            :precision="stat.precision || 0"
            :valueStyle="{ color: stat.color }"
          >
            <template #prefix>
              <component :is="stat.icon" />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="[16, 16]" class="mt-4">
      <a-col :span="16">
        <a-card title="文章发布趋势">
          <article-chart :loading="loading" :data="chartData" />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="最近活动" :loading="loading">
          <a-list :data-source="activities" :pagination="false">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.title"
                  :description="item.time"
                >
                  <template #avatar>
                    <a-avatar :src="item.avatar" />
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <!-- 系统状态 -->
    <a-row :gutter="[16, 16]" class="mt-4">
      <a-col :span="12">
        <a-card title="分类统计" :loading="loading">
          <category-pie :data="categoryData" />
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="系统状态" :loading="loading">
          <a-row :gutter="[16, 16]">
            <a-col :span="12" v-for="item in systemStatus" :key="item.title">
              <a-progress
                type="dashboard"
                :percent="item.value"
                :format="() => `${item.value}%`"
                :status="item.status"
              />
              <div class="text-center mt-2">{{ item.title }}</div>
            </a-col>
          </a-row>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  FileTextOutlined,
  CommentOutlined,
  EyeOutlined,
  UserOutlined
} from '@ant-design/icons-vue'
import ArticleChart from './components/ArticleChart.vue'
import CategoryPie from './components/CategoryPie.vue'

// 统计数据
const statistics = ref([
  {
    title: '文章总数',
    value: 0,
    icon: FileTextOutlined,
    color: '#1890ff'
  },
  {
    title: '评论总数',
    value: 0,
    icon: CommentOutlined,
    color: '#52c41a'
  },
  {
    title: '访问量',
    value: 0,
    icon: EyeOutlined,
    color: '#722ed1'
  },
  {
    title: '用户数',
    value: 0,
    icon: UserOutlined,
    color: '#faad14'
  }
])

// 图表数据
const chartData = ref({
  dates: [],
  counts: []
})

// 最近活动
const activities = ref([])

// 分类数据
const categoryData = ref([])

// 系统状态
const systemStatus = ref([
  {
    title: 'CPU使用率',
    value: 0,
    status: 'normal'
  },
  {
    title: '内存使用率',
    value: 0,
    status: 'normal'
  },
  {
    title: '磁盘使用率',
    value: 0,
    status: 'normal'
  }
])

// 加载状态
const loading = ref(true)

// 模拟获取数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // TODO: 替换为实际的API调用
    setTimeout(() => {
      statistics.value[0].value = 156
      statistics.value[1].value = 324
      statistics.value[2].value = 1503
      statistics.value[3].value = 89

      chartData.value = {
        dates: ['1月', '2月', '3月', '4月', '5月', '6月'],
        counts: [30, 45, 38, 52, 41, 56]
      }

      activities.value = [
        {
          title: '张三发布了新文章《Vue3最佳实践》',
          time: '2024-03-19 13:45',
          avatar: 'https://api.dicebear.com/7.x/miniavs/svg?seed=1'
        },
        {
          title: '李四更新了文章《TypeScript入门指南》',
          time: '2024-03-19 11:20',
          avatar: 'https://api.dicebear.com/7.x/miniavs/svg?seed=2'
        },
        {
          title: '王五回复了评论',
          time: '2024-03-19 10:15',
          avatar: 'https://api.dicebear.com/7.x/miniavs/svg?seed=3'
        }
      ]

      categoryData.value = [
        { name: '技术', value: 45 },
        { name: '生活', value: 25 },
        { name: '随笔', value: 18 },
        { name: '其他', value: 12 }
      ]

      systemStatus.value = [
        { title: 'CPU使用率', value: 45, status: 'normal' },
        { title: '内存使用率', value: 68, status: 'normal' },
        { title: '磁盘使用率', value: 82, status: 'warning' }
      ]

      loading.value = false
    }, 1000)
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.mt-4 {
  margin-top: 16px;
}

.text-center {
  text-align: center;
}
</style>