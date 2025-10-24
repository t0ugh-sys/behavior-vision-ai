import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'detection',
        name: 'Detection',
        component: () => import('@/views/Detection.vue'),
        meta: { title: '实时检测' }
      },
      {
        path: 'records',
        name: 'Records',
        component: () => import('@/views/Records.vue'),
        meta: { title: '检测记录' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/Alerts.vue'),
        meta: { title: '告警管理' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue'),
        meta: { title: '统计分析' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 白名单：不需要登录就能访问的页面
const whiteList = ['/login']

// 标记是否正在验证token，避免重复验证
let isValidatingToken = false

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (token) {
    // 有token的情况
    if (to.path === '/login') {
      // 已登录，访问登录页，跳转首页
      next({ path: '/', replace: true })
    } else {
      // Token存在，但可能已过期，让请求拦截器处理401错误
      next()
    }
  } else {
    // 没有token的情况
    if (whiteList.includes(to.path)) {
      // 访问白名单页面，直接放行
      next()
    } else {
      // 访问需要登录的页面，跳转登录页
      // 清除可能存在的无效数据
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 使用replace避免历史记录堆积
      if (from.path === '/login') {
        // 避免从登录页到登录页的循环
        next(false)
      } else {
        next({ path: '/login', replace: true })
      }
    }
  }
})

export default router

