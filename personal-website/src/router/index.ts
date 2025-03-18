import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/home/index.vue'
import BlogList from '../views/blog/components/BlogList.vue'
import BlogDetail from '../views/blog/components/BlogDetail.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/blog',
    name: 'blog',
    component: BlogList
  },
  {
    path: '/blog/:id',
    name: 'blog-detail',
    component: BlogDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

export default router