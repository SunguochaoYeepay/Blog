import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/login'
      },
      {
        path: 'login',
        component: () => import('@/views/auth/Login.vue'),
        meta: {
          title: '登录',
          requiresAuth: false
        }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/BasicLayout.vue'),
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '',
        redirect: '/admin/article',
        meta: {
          requiresAuth: true
        }
      },
      // 文章管理路由
      {
        path: 'article',
        name: 'ArticleList',
        component: () => import('@/views/article/List.vue'),
        meta: {
          title: '文章管理',
          requiresAuth: true
        }
      },
      {
        path: 'article/create',
        name: 'ArticleCreate',
        component: () => import('@/views/article/Edit.vue'),
        meta: {
          title: '创建文章',
          requiresAuth: true
        }
      },
      {
        path: 'article/edit/:id',
        name: 'ArticleEdit',
        component: () => import('@/views/article/Edit.vue'),
        meta: {
          title: '编辑文章',
          requiresAuth: true
        }
      },
      // 用户管理路由
      {
        path: 'user',
        name: 'UserList',
        component: () => import('@/views/user/List.vue'),
        meta: {
          title: '用户管理',
          requiresAuth: true
        }
      },
      {
        path: 'user/create',
        name: 'UserCreate',
        component: () => import('@/views/user/Edit.vue'),
        meta: {
          title: '创建用户',
          requiresAuth: true
        }
      },
      {
        path: 'user/edit/:id',
        name: 'UserEdit',
        component: () => import('@/views/user/Edit.vue'),
        meta: {
          title: '编辑用户',
          requiresAuth: true
        }
      },
      {
        path: 'tag',
        name: 'Tag',
        component: () => import('@/views/tag/TagList.vue'),
        meta: {
          title: '标签管理',
          requiresAuth: true
        }
      }
    ]
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = (to.meta.title as string) || '管理系统'

  console.log('Route guard - Current path:', to.path)
  console.log('Route guard - Token exists:', !!userStore.token)
  console.log('Route guard - User info exists:', !!userStore.userInfo)

  // 如果已登录且要去登录页，重定向到文章管理页面
  if (to.path === '/login' && userStore.token) {
    console.log('Route guard - Redirecting from login to admin because already logged in')
    next('/admin/article')
    return
  }

  // 如果需要登录
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果没有token，重定向到登录页
    if (!userStore.token) {
      console.log('Route guard - Redirecting to login because no token')
      // 修改重定向地址的处理逻辑
      const redirectPath = to.path === '/admin' ? '/admin/article' : to.fullPath
      next({
        path: '/login',
        query: { redirects: redirectPath }
      })
      return
    }
    
    // 如果有token但没有用户信息，获取用户信息
    if (!userStore.userInfo) {
      try {
        console.log('Route guard - Fetching user info')
        await userStore.getUserInfo()
        console.log('Route guard - User info fetched successfully')
        
        // 用户信息获取成功后继续导航
        if (to.path === '/admin') {
          next('/admin/article')
        } else {
          next()
        }
      } catch (error) {
        console.error('Route guard - Failed to fetch user info:', error)
        // 修改重定向地址的处理逻辑
        const redirectPath = to.path === '/admin' ? '/admin/article' : to.fullPath
        next({
          path: '/login',
          query: { redirects: redirectPath }
        })
      }
      return
    }

    // 如果有token和用户信息，且访问 /admin，重定向到 /admin/article
    if (to.path === '/admin') {
      next('/admin/article')
      return
    }
  }

  next()
})

export default router