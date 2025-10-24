import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 标记是否正在处理登出，避免重复操作
let isLoggingOut = false
// 存储待处理的请求，用于在登出完成后取消
const pendingRequests = new Map()

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 如果正在登出，取消所有新请求
    if (isLoggingOut) {
      const source = axios.CancelToken.source()
      source.cancel('正在退出登录，取消请求')
      config.cancelToken = source.token
    }
    
    // 添加JWT token到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 保留用户ID（某些API可能需要）
    const user = localStorage.getItem('user')
    if (user) {
      try {
        const userData = JSON.parse(user)
        config.headers['User-Id'] = userData.id
      } catch (e) {
        console.error('解析用户信息失败', e)
      }
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    // 如果请求被取消，静默处理
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }
    
    console.error('请求错误：', error)
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      handleUnauthorized()
      return Promise.reject(error)
    }
    
    // 处理403权限不足错误
    if (error.response && error.response.status === 403) {
      ElMessage.error('权限不足')
      return Promise.reject(error)
    }
    
    // 其他错误静默处理，避免过多提示
    if (error.response) {
      console.error(`API错误 ${error.response.status}:`, error.response.data)
    } else {
      console.error('网络错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// 处理未授权错误（401）
function handleUnauthorized() {
  // 如果已经在处理登出，直接返回
  if (isLoggingOut) {
    console.log('已在处理登出，跳过')
    return
  }
  
  // 设置登出标记
  isLoggingOut = true
  console.log('收到401错误，开始处理登出')
  
  // 清除本地存储
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  
  // 获取当前路由
  const currentPath = router.currentRoute.value.path
  console.log('当前路径:', currentPath)
  
  // 只在不是登录页时跳转和提示
  if (currentPath !== '/login') {
    // 只显示一次提示
    ElMessage.error('登录已过期，请重新登录')
    
    // 跳转到登录页
    console.log('跳转到登录页')
    router.replace('/login').then(() => {
      console.log('成功跳转到登录页')
      // 1秒后重置标记
      setTimeout(() => {
        isLoggingOut = false
        console.log('重置登出标记')
      }, 1000)
    }).catch(err => {
      console.error('跳转登录页失败:', err)
      isLoggingOut = false
    })
  } else {
    // 已经在登录页，静默处理
    console.log('已在登录页，静默处理')
    setTimeout(() => {
      isLoggingOut = false
    }, 500)
  }
}

export default request

