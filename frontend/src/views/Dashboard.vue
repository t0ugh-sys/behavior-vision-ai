<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h2>系统概览</h2>
      <el-button type="primary" @click="refreshAll" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" :xs="12" :sm="12" :md="6">
        <div class="stat-card" @click="goToRecords">
          <div class="stat-icon-wrapper">
            <div class="stat-icon" style="background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);">
              <el-icon :size="32"><Document /></el-icon>
            </div>
          </div>
          <div class="stat-content">
            <div class="stat-title">检测总数</div>
            <div class="stat-value">{{ detectionStats.total_records || 0 }}</div>
            <div class="stat-subtitle">Total Detections</div>
          </div>
          <div class="stat-progress">
            <el-progress 
              :percentage="100" 
              :show-text="false" 
              :stroke-width="4"
              color="#6495ED"
            />
          </div>
        </div>
      </el-col>
      
      <el-col :span="6" :xs="12" :sm="12" :md="6">
        <div class="stat-card" @click="goToRecords">
          <div class="stat-icon-wrapper">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
          </div>
          <div class="stat-content">
            <div class="stat-title">异常检测</div>
            <div class="stat-value">{{ detectionStats.abnormal_records || 0 }}</div>
            <div class="stat-subtitle">Abnormal Detections</div>
          </div>
          <div class="stat-progress">
            <el-progress 
              :percentage="abnormalPercentage" 
              :show-text="false" 
              :stroke-width="4"
              color="#f5576c"
            />
          </div>
        </div>
      </el-col>
      
      <el-col :span="6" :xs="12" :sm="12" :md="6">
        <div class="stat-card" @click="goToAlerts">
          <div class="stat-icon-wrapper">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
              <el-icon :size="32"><Bell /></el-icon>
            </div>
          </div>
          <div class="stat-content">
            <div class="stat-title">未处理告警</div>
            <div class="stat-value">{{ alertStats.unhandled_alerts || 0 }}</div>
            <div class="stat-subtitle">Pending Alerts</div>
          </div>
          <div class="stat-progress">
            <el-progress 
              :percentage="unhandledPercentage" 
              :show-text="false" 
              :stroke-width="4"
              color="#fa709a"
            />
          </div>
        </div>
      </el-col>
      
      <el-col :span="6" :xs="12" :sm="12" :md="6">
        <div class="stat-card" @click="goToRecords">
          <div class="stat-icon-wrapper">
            <div class="stat-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
              <el-icon :size="32"><SuccessFilled /></el-icon>
            </div>
          </div>
          <div class="stat-content">
            <div class="stat-title">正常检测</div>
            <div class="stat-value">{{ detectionStats.normal_records || 0 }}</div>
            <div class="stat-subtitle">Normal Detections</div>
          </div>
          <div class="stat-progress">
            <el-progress 
              :percentage="normalPercentage" 
              :show-text="false" 
              :stroke-width="4"
              color="#10b981"
            />
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="action-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="goToDetection">
              <el-icon><VideoCamera /></el-icon>
              开始检测
            </el-button>
            <el-button type="success" size="large" @click="goToRecords">
              <el-icon><Document /></el-icon>
              查看记录
            </el-button>
            <el-button type="warning" size="large" @click="goToAlerts">
              <el-icon><Bell /></el-icon>
              告警管理
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近告警</span>
          </template>
          <div class="recent-alerts">
            <div v-if="recentAlerts.length === 0" class="empty">
              <el-empty description="暂无告警" :image-size="80" />
            </div>
            <div
              v-for="alert in recentAlerts"
              :key="alert.id"
              class="alert-item"
            >
              <el-tag :type="getAlertType(alert.alertLevel)" size="small">
                {{ alert.alertType }}
              </el-tag>
              <span class="alert-desc">{{ alert.description }}</span>
              <span class="alert-time">{{ formatTime(alert.createdAt) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 系统状态 -->
    <el-row>
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="header">
              <span>系统状态</span>
              <el-button size="small" @click="refreshServiceStatus">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="后端服务">
              <el-tag :type="serviceStatus.backend?.status === 'UP' ? 'success' : 'danger'">
                {{ serviceStatus.backend?.status === 'UP' ? '运行中' : '已停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Python检测服务">
              <el-tag :type="serviceStatus.python?.status === 'UP' ? 'success' : 'danger'">
                {{ serviceStatus.python?.status === 'UP' ? '运行中' : '已停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="WebSocket连接">
              <el-tag :type="serviceStatus.websocket?.status === 'UP' ? 'success' : 'warning'">
                {{ serviceStatus.websocket?.status === 'UP' ? '已连接' : '未连接' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="检测模型">
              <span>YOLOv8 Pose</span>
              <el-tag v-if="pythonDetails?.model_loaded" type="success" size="small" style="margin-left: 10px;">已加载</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库">
              <el-tag :type="serviceStatus.database?.status === 'UP' ? 'success' : 'danger'">
                {{ serviceStatus.database?.status === 'UP' ? 'MySQL 8.0' : '不可用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="Python服务内存" v-if="pythonDetails?.system">
              {{ (pythonDetails.system.memory_used_mb / 1024).toFixed(2) }} GB / 
              {{ (pythonDetails.system.memory_total_mb / 1024).toFixed(2) }} GB
              ({{ pythonDetails.system.memory_percent.toFixed(1) }}%)
            </el-descriptions-item>
            <el-descriptions-item label="Python服务CPU" v-if="pythonDetails?.system">
              {{ pythonDetails.system.cpu_percent.toFixed(1) }}%
            </el-descriptions-item>
            <el-descriptions-item label="Python服务运行时间" v-if="pythonDetails?.uptime_seconds">
              {{ formatUptime(pythonDetails.uptime_seconds) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserStatistics } from '@/api/detection'
import { getAlertStatistics, getUnhandledAlerts } from '@/api/alert'
import { getAllServicesStatus, getPythonHealth } from '@/api/health'
import { ElMessage } from 'element-plus'
import {
  Document,
  Warning,
  Bell,
  SuccessFilled,
  VideoCamera,
  Refresh
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const detectionStats = ref({})
const alertStats = ref({})
const recentAlerts = ref([])
const serviceStatus = ref({})
const pythonDetails = ref(null)
const loading = ref(false)

// 计算百分比
const abnormalPercentage = computed(() => {
  const total = detectionStats.value.total_records || 0
  const abnormal = detectionStats.value.abnormal_records || 0
  return total > 0 ? Math.round((abnormal / total) * 100) : 0
})

const normalPercentage = computed(() => {
  const total = detectionStats.value.total_records || 0
  const normal = detectionStats.value.normal_records || 0
  return total > 0 ? Math.round((normal / total) * 100) : 0
})

const unhandledPercentage = computed(() => {
  const total = alertStats.value.total_alerts || 0
  const unhandled = alertStats.value.unhandled_alerts || 0
  return total > 0 ? Math.round((unhandled / total) * 100) : 0
})

onMounted(() => {
  // 检查token是否存在，避免无效请求
  const token = localStorage.getItem('token')
  if (token) {
    loadStatistics()
    loadServiceStatus()
  }
})

const loadStatistics = async () => {
  const user = userStore.getUserInfo()
  if (!user) {
    console.log('用户信息不存在，跳过加载统计')
    return
  }
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('Token不存在，跳过加载统计')
    return
  }
  
  try {
    // 加载检测统计
    const detectionRes = await getUserStatistics(user.id)
    detectionStats.value = detectionRes.data
    
    // 加载告警统计
    const alertRes = await getAlertStatistics(user.id)
    alertStats.value = alertRes.data
    
    // 加载最近告警
    const recentAlertsRes = await getUnhandledAlerts(user.id)
    recentAlerts.value = recentAlertsRes.data.slice(0, 5)
  } catch (error) {
    // 静默处理错误，避免重复提示
    console.error('加载统计数据失败:', error)
  }
}

const getAlertType = (level) => {
  const typeMap = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info'
  }
  return typeMap[level] || 'info'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadServiceStatus = async () => {
  try {
    // 获取所有服务状态
    const statusRes = await getAllServicesStatus()
    serviceStatus.value = statusRes.data
    
    // 获取Python服务详细信息
    try {
      const pythonRes = await getPythonHealth()
      if (pythonRes.data && pythonRes.data.details) {
        pythonDetails.value = pythonRes.data.details
      }
    } catch (error) {
      console.error('获取Python服务详情失败:', error)
    }
  } catch (error) {
    console.error('加载服务状态失败:', error)
  }
}

const refreshServiceStatus = () => {
  loadServiceStatus()
}

const refreshAll = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStatistics(),
      loadServiceStatus()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}天 ${hours}小时 ${minutes}分钟`
  } else if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

const goToDetection = () => router.push('/detection')
const goToRecords = () => router.push('/records')
const goToAlerts = () => router.push('/alerts')
</script>

<style scoped>
.dashboard {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.06);
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.stat-icon-wrapper {
  margin-bottom: 16px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  margin-bottom: 12px;
}

.stat-title {
  font-size: 14px;
  color: #718096;
  margin-bottom: 8px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-subtitle {
  font-size: 12px;
  color: #a0aec0;
  font-weight: 400;
}

.stat-progress {
  margin-top: 12px;
}

.action-row {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 140px;
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.recent-alerts {
  max-height: 280px;
  overflow-y: auto;
}

.recent-alerts::-webkit-scrollbar {
  width: 6px;
}

.recent-alerts::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.recent-alerts::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.recent-alerts::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.2s;
  border-radius: 8px;
}

.alert-item:hover {
  background: #f7fafc;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-desc {
  flex: 1;
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
}

.alert-time {
  font-size: 12px;
  color: #a0aec0;
  white-space: nowrap;
}

.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 240px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Card styling */
.el-card {
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.el-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.el-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 16px;
  color: #1a202c;
}

.el-card :deep(.el-card__body) {
  padding: 20px;
}

/* Descriptions styling */
.el-descriptions :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #4a5568;
}

.el-descriptions :deep(.el-descriptions__content) {
  color: #2d3748;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .dashboard-header h2 {
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 28px;
  }
  
  .action-buttons .el-button {
    min-width: 100%;
  }
}
</style>

