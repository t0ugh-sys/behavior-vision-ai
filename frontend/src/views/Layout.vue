<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo" :class="{ 'logo-collapse': isCollapse }">
        <div class="logo-icon">
          <el-icon :size="28"><Monitor /></el-icon>
        </div>
        <transition name="fade">
          <div v-show="!isCollapse" class="logo-content">
            <div class="logo-title">行为检测</div>
            <div class="logo-subtitle">AI Detection System</div>
          </div>
        </transition>
      </div>
      
      <el-scrollbar class="menu-scrollbar">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>
              <span>首页概览</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/detection">
            <el-icon><VideoCamera /></el-icon>
            <template #title>
              <span>实时检测</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/records">
            <el-icon><Document /></el-icon>
            <template #title>
              <span>检测记录</span>
              <el-badge v-if="recordsCount > 0" :value="recordsCount" class="item-badge" />
            </template>
          </el-menu-item>
          
          <el-menu-item index="/alerts">
            <el-icon><Bell /></el-icon>
            <template #title>
              <span>告警管理</span>
              <el-badge v-if="alertStore.unreadCount > 0" :value="alertStore.unreadCount" class="item-badge" type="danger" />
            </template>
          </el-menu-item>
          
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>
              <span>统计分析</span>
            </template>
          </el-menu-item>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <template #title>
              <span>系统设置</span>
            </template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
      
      <!-- 折叠按钮 -->
      <div class="collapse-trigger" @click="toggleCollapse">
        <el-icon>
          <component :is="isCollapse ? 'DArrowRight' : 'DArrowLeft'" />
        </el-icon>
      </div>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header class="header" height="64px">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">
              <el-icon><HomeFilled /></el-icon>
              首页
            </el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 搜索 -->
          <el-tooltip content="搜索" placement="bottom">
            <div class="header-action">
              <el-icon><Search /></el-icon>
            </div>
          </el-tooltip>
          
          <!-- 全屏 -->
          <el-tooltip content="全屏" placement="bottom">
            <div class="header-action" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
            </div>
          </el-tooltip>
          
          <!-- 告警 -->
          <el-badge :value="alertStore.unreadCount" :hidden="alertStore.unreadCount === 0" :max="99" class="header-badge">
            <div class="header-action" @click="showAlertDrawer = true">
              <el-icon><Bell /></el-icon>
            </div>
          </el-badge>
          
          <el-divider direction="vertical" />
          
          <!-- 用户 -->
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown">
              <el-avatar :size="40" class="user-avatar">
                <el-icon :size="24"><User /></el-icon>
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ userStore.userInfo?.username }}</div>
                <div class="user-role">超级管理员</div>
              </div>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主要内容 -->
      <el-main class="main-content">
        <transition name="fade-transform" mode="out-in">
          <router-view :key="route.fullPath" />
        </transition>
      </el-main>
    </el-container>
    
    <!-- 告警抽屉 -->
    <el-drawer
      v-model="showAlertDrawer"
      title="实时告警"
      :size="480"
      direction="rtl"
      class="alert-drawer"
      @open="alertStore.markAsRead()"
    >
      <template #header>
        <div class="drawer-header">
          <div class="drawer-title">
            <div class="drawer-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div>
              <div class="drawer-title-text">实时告警通知</div>
              <div class="drawer-subtitle">Real-time Alerts</div>
            </div>
          </div>
          <el-tag v-if="alertStore.unreadCount > 0" type="danger" effect="dark" round>
            {{ alertStore.unreadCount }} 条未读
          </el-tag>
        </div>
      </template>
      
      <div class="alert-list">
        <el-empty v-if="alertStore.alerts.length === 0" description="暂无告警信息">
          <template #image>
            <div class="empty-icon">
              <el-icon :size="80"><Bell /></el-icon>
            </div>
          </template>
        </el-empty>
        
        <div v-else class="alert-timeline">
          <div
            v-for="(alert, index) in alertStore.alerts"
            :key="alert.id"
            class="alert-item"
          >
            <div class="alert-line" v-if="index < alertStore.alerts.length - 1"></div>
            <div class="alert-dot" :class="`alert-dot-${alert.alertLevel?.toLowerCase()}`"></div>
            <el-card class="alert-card" shadow="hover" :body-style="{ padding: '16px' }">
              <div class="alert-card-header">
                <div class="alert-tags">
                  <el-tag :type="getAlertLevelType(alert.alertLevel)" effect="dark" size="small">
                    {{ getAlertTypeLabel(alert.alertType) }}
                  </el-tag>
                  <el-tag type="info" size="small">{{ alert.alertLevel }}</el-tag>
                </div>
                <div class="alert-time">{{ formatTime(alert.createdAt) }}</div>
              </div>
              
              <div class="alert-card-body">
                <p>{{ alert.description }}</p>
              </div>
              
              <div class="alert-card-footer">
                <div class="confidence-label">置信度</div>
                <el-progress 
                  :percentage="(alert.confidence * 100)" 
                  :stroke-width="8"
                  :color="getConfidenceColor(alert.confidence)"
                  :show-text="true"
                  :format="() => `${(alert.confidence * 100).toFixed(1)}%`"
                />
              </div>
            </el-card>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="showAlertDrawer = false" size="large">关闭</el-button>
          <el-button type="primary" @click="$router.push('/alerts')" size="large">
            <el-icon><View /></el-icon>
            查看全部
          </el-button>
        </div>
      </template>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Monitor, 
  HomeFilled, 
  VideoCamera, 
  Document, 
  Bell, 
  DataAnalysis, 
  Setting, 
  User,
  DArrowLeft,
  DArrowRight,
  FullScreen,
  ArrowDown,
  SwitchButton,
  Search,
  View
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAlertStore } from '@/stores/alert'
import websocket from '@/utils/websocket'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const alertStore = useAlertStore()

const showAlertDrawer = ref(false)
const alertSound = ref(null)
const isCollapse = ref(false)
const recordsCount = ref(0)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '')

// 切换侧边栏折叠
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 连接WebSocket
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('未登录，跳过WebSocket连接')
    return
  }
  
  const user = userStore.getUserInfo()
  if (user && user.id) {
    try {
      await websocket.connect(user.id, handleAlertMessage)
      console.log('WebSocket已连接')
    } catch (error) {
      console.error('WebSocket连接失败:', error)
    }
  }
  
  alertSound.value = new Audio('/alert.mp3')
})

onUnmounted(() => {
  websocket.disconnect()
})

// 处理告警消息
const handleAlertMessage = (data) => {
  console.log('收到告警:', data)
  
  if (data.action === 'handled') {
    return
  }
  
  alertStore.addAlert(data)
  
  ElMessage({
    message: `${data.alertType}: ${data.description}`,
    type: 'warning',
    duration: 5000,
    showClose: true
  })
  
  try {
    alertSound.value?.play()
  } catch (error) {
    console.error('播放提示音失败:', error)
  }
}

// 获取告警类型标签
const getAlertTypeLabel = (type) => {
  const labels = {
    'FALL': '跌倒',
    'FIGHT': '打架',
    'ABNORMAL_POSE': '异常姿态',
    'INTRUSION': '区域入侵'
  }
  return labels[type] || type
}

// 获取告警级别类型
const getAlertLevelType = (level) => {
  const typeMap = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'success'
  }
  return typeMap[level] || 'info'
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#ef4444'
  if (confidence >= 0.7) return '#f59e0b'
  return '#10b981'
}

// 格式化时间
const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

// 处理用户菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？退出后需要重新登录。', '退出确认', {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'logout-confirm'
      }).then(() => {
        websocket.disconnect()
        userStore.clearUserInfo()
        router.push('/login')
        ElMessage.success('已安全退出')
      }).catch(() => {})
      break
  }
}
</script>

<style scoped>
/* 容器 */
.layout-container {
  height: 100vh;
  background: var(--bg-secondary);
}

/* 侧边栏 */
.sidebar {
  background: var(--sidebar-gradient);
  box-shadow: 2px 0 12px rgba(99, 102, 241, 0.15);
  transition: width 0.28s;
  position: relative;
  overflow: visible;
}

.logo {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.28s;
}

.logo-collapse {
  padding: 0;
  justify-content: center;
}

.logo-collapse .logo-icon {
  margin-right: 0;
}

.logo-collapse .logo-content {
  display: none;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  transition: all 0.2s;
}

.logo:hover .logo-icon {
  background: rgba(255, 255, 255, 0.15);
}

.logo-content {
  color: #fff;
  line-height: 1.4;
}

.logo-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.logo-subtitle {
  font-size: 11px;
  opacity: 0.8;
  font-weight: 300;
  letter-spacing: 1px;
}

.menu-scrollbar {
  height: calc(100vh - 64px - 60px);
  overflow-x: hidden;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  padding: 12px 10px;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #343541;
  color: #fff;
  font-weight: 400;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  margin-right: 10px;
  font-size: 20px;
}

/* 折叠状态下图标居中 */
.sidebar-menu.el-menu--collapse :deep(.el-menu-item) {
  padding: 0 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item .el-icon) {
  margin-right: 0 !important;
  margin-left: 0 !important;
  font-size: 22px;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item span),
.sidebar-menu.el-menu--collapse :deep(.el-menu-item .item-badge) {
  display: none !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-tooltip__trigger) {
  width: 100%;
  display: flex;
  justify-content: center;
}

.item-badge {
  margin-left: 8px;
}

.collapse-trigger {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-trigger:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

/* 主容器 */
.main-container {
  display: flex;
  flex-direction: column;
}

/* 顶部栏 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-left {
  flex: 1;
}

.header-left :deep(.el-breadcrumb__item) {
  display: flex;
  align-items: center;
}

.header-left :deep(.el-breadcrumb__inner) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: var(--text-secondary);
}

.header-left :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-action {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-secondary);
}

.header-action:hover {
  background: var(--bg-tertiary);
  color: var(--primary-color);
}

.header-badge {
  display: flex;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.user-dropdown:hover {
  background: var(--bg-tertiary);
}

.user-avatar {
  background: var(--gradient-primary);
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-tertiary);
}

.user-arrow {
  color: var(--text-tertiary);
  transition: transform 0.3s;
}

.user-dropdown:hover .user-arrow {
  transform: rotate(180deg);
}

/* 主内容 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--bg-secondary);
}

/* 抽屉 */
.alert-drawer :deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.drawer-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.drawer-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.drawer-title-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.drawer-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.alert-list {
  height: 100%;
  overflow-y: auto;
}

.empty-icon {
  color: var(--text-tertiary);
  opacity: 0.5;
}

.alert-timeline {
  position: relative;
}

.alert-item {
  position: relative;
  padding-left: 40px;
  margin-bottom: 20px;
}

.alert-line {
  position: absolute;
  left: 15px;
  top: 32px;
  bottom: -20px;
  width: 2px;
  background: var(--border-color);
}

.alert-dot {
  position: absolute;
  left: 8px;
  top: 20px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid var(--bg-primary);
  background: var(--primary-color);
  z-index: 1;
}

.alert-dot-critical,
.alert-dot-high {
  background: var(--danger-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
}

.alert-dot-medium {
  background: var(--warning-color);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}

.alert-dot-low {
  background: var(--success-color);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}

.alert-card {
  border-radius: 12px;
  border: 1px solid var(--border-light);
  transition: all 0.3s;
}

.alert-card:hover {
  border-color: var(--primary-lighter);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.15);
}

.alert-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.alert-tags {
  display: flex;
  gap: 8px;
}

.alert-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.alert-card-body p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.alert-card-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.confidence-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.28s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
