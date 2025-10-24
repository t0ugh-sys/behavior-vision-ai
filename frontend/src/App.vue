<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 应用启动时验证token
onMounted(() => {
  const token = localStorage.getItem('token')
  const currentPath = router.currentRoute.value.path
  
  // 如果有token但不在登录页，检查token格式
  if (token && currentPath !== '/login') {
    try {
      // 简单验证token格式（JWT应该是三段式）
      const parts = token.split('.')
      if (parts.length !== 3) {
        console.warn('Token格式无效，清除并跳转登录页')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.replace('/login')
      }
    } catch (error) {
      console.error('Token验证失败:', error)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.replace('/login')
    }
  }
  
  // 如果没有token但不在登录页，跳转登录页
  if (!token && currentPath !== '/login') {
    localStorage.removeItem('user')
    router.replace('/login')
  }
})
</script>

<style scoped>
#app {
  width: 100%;
  height: 100vh;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

