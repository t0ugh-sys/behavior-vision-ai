<template>
  <div class="records-page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="header-left">
            <span>检测记录</span>
            <el-tag v-if="autoRefresh" type="success" size="small" effect="plain">
              <el-icon><CircleCheck /></el-icon> 自动刷新中
            </el-tag>
          </div>
          <div class="header-right">
            <el-button 
              v-if="selectedRecords.length > 0"
              type="danger" 
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedRecords.length }})
            </el-button>
            <el-dropdown @command="handleExport" style="margin-right: 10px;">
              <el-button type="success">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">导出为Excel</el-dropdown-item>
                  <el-dropdown-item command="csv">导出为CSV</el-dropdown-item>
                  <el-dropdown-item command="json">导出为JSON</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="handlePrint">
              <el-icon><Printer /></el-icon>
              打印
            </el-button>
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
            <el-button type="primary" @click="loadRecords">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="records"
        v-loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="来源类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getSourceTypeColor(row.sourceType)">
              {{ row.sourceType }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="检测结果" width="120">
          <template #default="{ row }">
            <el-tag :type="row.hasAbnormal ? 'danger' : 'success'">
              {{ row.hasAbnormal ? '异常' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="行为类型" width="200">
          <template #default="{ row }">
            <div v-if="row.hasAbnormal" class="behavior-tags">
              <el-tag 
                v-for="behavior in getAllBehaviorTypes(row)" 
                :key="behavior.type"
                type="warning" 
                size="small"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ behavior.name }}
                <span v-if="behavior.count > 1" style="margin-left: 3px;">
                  x{{ behavior.count }}
                </span>
              </el-tag>
            </div>
            <el-tag v-else type="success">正常行为</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="置信度" width="150">
          <template #default="{ row }">
            <el-progress
              v-if="row.confidence !== undefined && row.confidence !== null"
              :percentage="parseFloat((row.confidence * 100).toFixed(1))"
              :color="getConfidenceColor(row.confidence)"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="检测记录详情"
      width="70%"
    >
      <el-descriptions v-if="currentRecord" :column="2" border>
        <el-descriptions-item label="记录ID">{{ currentRecord.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentRecord.userId }}</el-descriptions-item>
        <el-descriptions-item label="来源类型">{{ currentRecord.sourceType }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusColor(currentRecord.status)">
            {{ getStatusText(currentRecord.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否异常">
          <el-tag :type="currentRecord.hasAbnormal ? 'danger' : 'success'">
            {{ currentRecord.hasAbnormal ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="行为类型" :span="2">
          <div v-if="currentRecord.hasAbnormal" class="behavior-tags">
            <el-tag 
              v-for="behavior in getAllBehaviorTypes(currentRecord)" 
              :key="behavior.type"
              type="warning"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ behavior.name }}
              <span v-if="behavior.count > 1" style="margin-left: 5px;">
                (出现{{ behavior.count }}次)
              </span>
            </el-tag>
          </div>
          <el-tag v-else type="success">正常行为</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          {{ currentRecord.confidence !== undefined && currentRecord.confidence !== null ? (currentRecord.confidence * 100).toFixed(1) + '%' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(currentRecord.createdAt) }}
        </el-descriptions-item>
        <el-descriptions-item label="文件路径" :span="2">
          {{ currentRecord.videoPath || currentRecord.imagePath || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="检测结果" :span="2">
          <el-input
            v-model="currentRecord.detectionResult"
            type="textarea"
            :rows="6"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item v-if="currentRecord.errorMessage" label="错误信息" :span="2">
          <el-alert
            :title="currentRecord.errorMessage"
            type="error"
            :closable="false"
          />
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- 可视化检测结果（图片或视频） -->
      <div v-if="currentRecord.visualizationUrl" class="visualization-section">
        <el-divider content-position="left">
          <el-text tag="b">检测可视化结果</el-text>
        </el-divider>
        <div class="visualization-image-container">
          <!-- 图片类型 -->
          <el-image
            v-if="isImageFile(currentRecord.visualizationUrl)"
            :src="currentRecord.visualizationUrl"
            :preview-src-list="[currentRecord.visualizationUrl]"
            fit="contain"
            class="visualization-image"
          >
            <template #error>
              <div class="image-error">
                <el-icon><PictureFilled /></el-icon>
                <span>图片加载失败</span>
              </div>
            </template>
          </el-image>
          
          <!-- 视频类型 -->
          <div v-else-if="isVideoFile(currentRecord.visualizationUrl)" class="video-player-container">
            <!-- 视频加载动画 -->
            <div v-if="videoLoading" class="video-loading-overlay">
              <el-icon class="is-loading" :size="50">
                <Loading />
              </el-icon>
              <p>加载视频中...</p>
            </div>
            
            <video
              ref="videoPlayerRef"
              :src="currentRecord.visualizationUrl"
              class="visualization-video"
              @loadstart="handleVideoLoadStart"
              @canplay="handleVideoCanPlay"
              @timeupdate="handleVideoTimeUpdate"
              @loadedmetadata="handleVideoLoaded"
              @ended="handleVideoEnded"
              @error="handleVideoError"
            >
              您的浏览器不支持视频播放
            </video>
            
            <!-- 自定义视频控制器 -->
            <div class="video-controls">
              <!-- 播放/暂停 -->
              <el-button 
                :icon="videoPlaying ? 'VideoPause' : 'VideoPlay'"
                size="small"
                @click="toggleVideoPlay"
              />
              
              <!-- 进度条 -->
              <div class="progress-container">
                <el-slider
                  v-model="videoProgress"
                  :show-tooltip="false"
                  @change="handleProgressChange"
                  style="flex: 1;"
                />
                <span class="time-display">
                  {{ formatVideoTime(videoCurrentTime) }} / {{ formatVideoTime(videoDuration) }}
                </span>
              </div>
              
              <!-- 播放速度 -->
              <el-dropdown @command="handleSpeedChange">
                <el-button size="small">
                  {{ videoSpeed }}x
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="0.5">0.5x</el-dropdown-item>
                    <el-dropdown-item command="0.75">0.75x</el-dropdown-item>
                    <el-dropdown-item command="1">1.0x</el-dropdown-item>
                    <el-dropdown-item command="1.25">1.25x</el-dropdown-item>
                    <el-dropdown-item command="1.5">1.5x</el-dropdown-item>
                    <el-dropdown-item command="2">2.0x</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <!-- 帧跳转 -->
              <el-button-group size="small">
                <el-button @click="skipFrames(-10)">
                  <el-icon><DArrowLeft /></el-icon>
                  10帧
                </el-button>
                <el-button @click="skipFrames(10)">
                  10帧
                  <el-icon><DArrowRight /></el-icon>
                </el-button>
              </el-button-group>
              
              <!-- 全屏 -->
              <el-button 
                icon="FullScreen"
                size="small"
                @click="toggleFullscreen"
              />
            </div>
          </div>
          
          <!-- 其他类型 -->
          <div v-else class="file-error">
            <el-icon><PictureFilled /></el-icon>
            <span>不支持的文件类型</span>
          </div>
        </div>
      </div>
      
      <!-- 异常行为统计 -->
      <div v-if="currentRecord && currentRecord.hasAbnormal" class="behavior-statistics-section">
        <el-divider content-position="left">
          <el-text tag="b">异常行为统计</el-text>
        </el-divider>
        
        <el-table :data="getAllBehaviorTypes(currentRecord)" border stripe>
          <el-table-column prop="name" label="行为类型" width="150">
            <template #default="scope">
              <el-tag type="warning">{{ scope.row.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="出现次数" width="120">
            <template #default="scope">
              <el-tag type="info">{{ scope.row.count }} 次</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="说明">
            <template #default="scope">
              <span v-if="scope.row.count === 1">
                在检测中发现 1 次该行为
              </span>
              <span v-else>
                在检测中共发现 {{ scope.row.count }} 次该行为（可能在不同帧/时间点）
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 检测片段信息（仅视频） -->
      <div v-if="currentRecord && currentRecord.sourceType === 'VIDEO' && getDetectionSegments(currentRecord).length > 0" class="segments-section">
        <el-divider content-position="left">
          <el-text tag="b">检测片段 ({{ getDetectionSegments(currentRecord).length }})</el-text>
        </el-divider>
        
        <el-table :data="getDetectionSegments(currentRecord)" border stripe>
          <el-table-column prop="start_time" label="开始时间" width="100">
            <template #default="scope">
              {{ scope.row.start_time.toFixed(1) }}s
            </template>
          </el-table-column>
          <el-table-column prop="end_time" label="结束时间" width="100">
            <template #default="scope">
              {{ scope.row.end_time.toFixed(1) }}s
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="时长" width="80">
            <template #default="scope">
              {{ scope.row.duration.toFixed(1) }}s
            </template>
          </el-table-column>
          <el-table-column prop="total_frames" label="总帧数" width="80" />
          <el-table-column prop="person_count_max" label="最多人数" width="90" />
          <el-table-column prop="has_abnormal" label="是否异常" width="90">
            <template #default="scope">
              <el-tag :type="scope.row.has_abnormal ? 'danger' : 'success'" size="small">
                {{ scope.row.has_abnormal ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="abnormal_count" label="异常帧数" width="90">
            <template #default="scope">
              <el-tag v-if="scope.row.abnormal_count > 0" type="warning" size="small">
                {{ scope.row.abnormal_count }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="异常比例" width="100">
            <template #default="scope">
              <el-progress
                v-if="scope.row.abnormal_count > 0"
                :percentage="parseFloat(((scope.row.abnormal_count / scope.row.total_frames) * 100).toFixed(1))"
                :color="scope.row.abnormal_count / scope.row.total_frames > 0.5 ? '#f56c6c' : '#e6a23c'"
                :stroke-width="12"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getDetectionRecords, deleteDetectionRecord, batchDeleteRecords } from '@/api/detection'
import { useUserStore } from '@/stores/user'
import { PictureFilled, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { exportDetectionRecords, exportToCSV, exportToJSON, printTable } from '@/utils/export'

const userStore = useUserStore()

const loading = ref(false)
const records = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRecords = ref([])

const detailVisible = ref(false)
const currentRecord = ref(null)

const autoRefresh = ref(false)
let refreshInterval = null

// 视频播放控制
const videoPlayerRef = ref(null)
const videoLoading = ref(false)
const videoPlaying = ref(false)
const videoProgress = ref(0)
const videoCurrentTime = ref(0)
const videoDuration = ref(0)
const videoSpeed = ref(1)

onMounted(() => {
  // 检查token是否存在
  const token = localStorage.getItem('token')
  if (token) {
    loadRecords()
  }
})

onUnmounted(() => {
  // 清除定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})

// 切换自动刷新
const toggleAutoRefresh = (value) => {
  if (value) {
    // 启动自动刷新（每10秒刷新一次）
    refreshInterval = setInterval(() => {
      const currentToken = localStorage.getItem('token')
      if (currentToken && autoRefresh.value) {
        loadRecords(true) // 静默刷新
      } else {
        clearInterval(refreshInterval)
        refreshInterval = null
        autoRefresh.value = false
      }
    }, 10000)
    ElMessage.success('已启动自动刷新，每10秒刷新一次')
  } else {
    // 停止自动刷新
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
    ElMessage.info('已停止自动刷新')
  }
}

const loadRecords = async (silent = false) => {
  const user = userStore.getUserInfo()
  if (!user) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('Token不存在，跳过加载记录')
    return
  }
  
  if (!silent) {
    loading.value = true
  }
  
  try {
    const res = await getDetectionRecords(user.id, currentPage.value - 1, pageSize.value)
    records.value = res.data.content
    total.value = res.data.totalElements
  } catch (error) {
    if (!silent) {
      console.error('加载记录失败:', error)
    }
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

const handleSizeChange = () => {
  loadRecords()
}

const handleCurrentChange = () => {
  loadRecords()
}

const viewDetail = (row) => {
  currentRecord.value = row
  detailVisible.value = true
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

// 删除单条记录
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除记录ID: ${row.id} 吗？
      
删除记录将同时删除以下文件：
• 上传的原始文件（视频/图片）
• 可视化结果文件
• 相关快照文件

此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        dangerouslyUseHTMLString: true
      }
    )
    
    loading.value = true
    await deleteDetectionRecord(row.id)
    ElMessage.success('删除成功')
    
    // 重新加载当前页
    await loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请先选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条记录吗？

批量删除将同时删除所有记录的相关文件：
• 上传的原始文件（视频/图片）
• 可视化结果文件
• 相关快照文件

此操作不可恢复！`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        dangerouslyUseHTMLString: true
      }
    )
    
    loading.value = true
    const recordIds = selectedRecords.value.map(record => record.id)
    await batchDeleteRecords(recordIds)
    ElMessage.success(`成功删除 ${recordIds.length} 条记录`)
    
    // 清空选择
    selectedRecords.value = []
    
    // 重新加载当前页
    await loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(error.message || '批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 导出功能
const handleExport = (command) => {
  if (records.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  try {
    switch (command) {
      case 'excel':
        exportDetectionRecords(records.value, '检测记录')
        ElMessage.success('导出成功')
        break
      case 'csv':
        exportToCSV(records.value, '检测记录')
        ElMessage.success('导出成功')
        break
      case 'json':
        exportToJSON(records.value, '检测记录')
        ElMessage.success('导出成功')
        break
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 打印功能
const handlePrint = () => {
  if (records.value.length === 0) {
    ElMessage.warning('暂无数据可打印')
    return
  }
  
  const columns = [
    { label: 'ID', prop: 'id' },
    { label: '源类型', prop: 'sourceType' },
    { label: '检测时间', prop: 'createdAt', formatter: (row) => formatTime(row.createdAt) },
    { label: '是否异常', prop: 'hasAbnormal', formatter: (row) => row.hasAbnormal ? '是' : '否' },
    { label: '行为类型', prop: 'behaviorType', formatter: (row) => getBehaviorTypeName(row.behaviorType) },
    { label: '置信度', prop: 'confidence', formatter: (row) => row.confidence ? `${(row.confidence * 100).toFixed(1)}%` : '-' },
    { label: '状态', prop: 'status', formatter: (row) => getStatusText(row.status) }
  ]
  
  printTable('检测记录', columns, records.value)
}

const getSourceTypeColor = (type) => {
  const colorMap = {
    'IMAGE': 'primary',
    'VIDEO': 'success',
    'REALTIME': 'warning'
  }
  return colorMap[type] || 'info'
}

const getStatusColor = (status) => {
  const colorMap = {
    'PROCESSING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger'
  }
  return colorMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'PROCESSING': '处理中',
    'COMPLETED': '已完成',
    'FAILED': '失败'
  }
  return textMap[status] || status
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#f56c6c'
  if (confidence >= 0.7) return '#e6a23c'
  return '#67c23a'
}

const getBehaviorTypeName = (type) => {
  const nameMap = {
    'FALL': '跌倒',
    'FIGHT': '打架',
    'INTRUSION': '入侵',
    'ABNORMAL_POSE': '异常姿态',
    'RUNNING': '奔跑',
    'CLIMBING': '攀爬',
    'GATHERING': '聚集'
  }
  return nameMap[type] || type
}

// 获取记录中所有的异常行为类型及统计
const getAllBehaviorTypes = (record) => {
  if (!record || !record.hasAbnormal) {
    return []
  }
  
  const behaviors = []
  const behaviorCount = {}
  let hasDetailedData = false  // 标记是否找到详细数据
  
  // 解析detectionResult中的详细数据
  if (record.detectionResult) {
    try {
      let result
      if (typeof record.detectionResult === 'string') {
        result = JSON.parse(record.detectionResult)
      } else {
        result = record.detectionResult
      }
      
      // 1. 检查detection_segments（视频片段检测）
      if (result.detection_segments && Array.isArray(result.detection_segments)) {
        result.detection_segments.forEach(segment => {
          if (segment.abnormal_behaviors && Array.isArray(segment.abnormal_behaviors)) {
            segment.abnormal_behaviors.forEach(behavior => {
              const type = behavior.type || behavior.behavior_type
              if (type) {
                behaviorCount[type] = (behaviorCount[type] || 0) + 1
                hasDetailedData = true
              }
            })
          }
        })
      }
      
      // 2. 检查persons数组中的异常行为（图片/单帧检测）
      if (result.persons && Array.isArray(result.persons)) {
        result.persons.forEach(person => {
          // 对于图片检测，每个检测到跌倒的人算一次
          if (person.abnormal_behaviors && Array.isArray(person.abnormal_behaviors)) {
            person.abnormal_behaviors.forEach(behavior => {
              const type = behavior.type || behavior.behavior_type
              if (type) {
                behaviorCount[type] = (behaviorCount[type] || 0) + 1
                hasDetailedData = true
              }
            })
          }
        })
      }
      
      // 3. 如果没有详细数据，使用主behavior_type（避免重复计数）
      if (!hasDetailedData && result.behavior_type) {
        behaviorCount[result.behavior_type] = 1
        hasDetailedData = true
      }
    } catch (error) {
      console.error('解析detectionResult失败:', error)
    }
  }
  
  // 转换为数组格式
  Object.keys(behaviorCount).forEach(type => {
    if (type && type !== 'null' && type !== 'undefined') {
      behaviors.push({
        type: type,
        name: getBehaviorTypeName(type),
        count: behaviorCount[type]
      })
    }
  })
  
  // 如果没有找到任何详细数据，使用record.behaviorType作为兜底
  if (behaviors.length === 0 && record.behaviorType) {
    behaviors.push({
      type: record.behaviorType,
      name: getBehaviorTypeName(record.behaviorType),
      count: 1
    })
  }
  
  return behaviors
}

// 判断是否为图片文件
const isImageFile = (url) => {
  if (!url) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
  const lowerUrl = url.toLowerCase()
  return imageExtensions.some(ext => lowerUrl.includes(ext))
}

// 判断是否为视频文件
const isVideoFile = (url) => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext))
}

// 视频播放控制函数
const toggleVideoPlay = () => {
  if (!videoPlayerRef.value) return
  
  if (videoPlaying.value) {
    videoPlayerRef.value.pause()
  } else {
    videoPlayerRef.value.play()
  }
  videoPlaying.value = !videoPlaying.value
}

const handleVideoTimeUpdate = (e) => {
  const video = e.target
  videoCurrentTime.value = video.currentTime
  if (videoDuration.value > 0) {
    videoProgress.value = (video.currentTime / videoDuration.value) * 100
  }
}

const handleVideoLoadStart = () => {
  videoLoading.value = true
}

const handleVideoCanPlay = () => {
  videoLoading.value = false
}

const handleVideoError = (e) => {
  videoLoading.value = false
  console.error('视频加载失败:', e)
  ElMessage.error('视频加载失败，请检查网络连接')
}

const handleVideoLoaded = (e) => {
  const video = e.target
  videoDuration.value = video.duration
  videoSpeed.value = 1
  videoLoading.value = false
}

const handleVideoEnded = () => {
  videoPlaying.value = false
  videoProgress.value = 0
}

const handleProgressChange = (value) => {
  if (!videoPlayerRef.value) return
  const newTime = (value / 100) * videoDuration.value
  videoPlayerRef.value.currentTime = newTime
}

const handleSpeedChange = (speed) => {
  if (!videoPlayerRef.value) return
  const newSpeed = parseFloat(speed)
  videoPlayerRef.value.playbackRate = newSpeed
  videoSpeed.value = newSpeed
}

const skipFrames = (frames) => {
  if (!videoPlayerRef.value) return
  // 假设视频是30fps，每帧约0.033秒
  const timePerFrame = 1 / 30
  const skipTime = frames * timePerFrame
  const newTime = videoPlayerRef.value.currentTime + skipTime
  videoPlayerRef.value.currentTime = Math.max(0, Math.min(newTime, videoDuration.value))
}

const toggleFullscreen = () => {
  if (!videoPlayerRef.value) return
  
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    videoPlayerRef.value.requestFullscreen()
  }
}

const formatVideoTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 获取检测片段
const getDetectionSegments = (record) => {
  if (!record || !record.detectionResult) {
    return []
  }
  
  try {
    let result = record.detectionResult
    if (typeof result === 'string') {
      result = JSON.parse(result)
    }
    
    return result.detection_segments || []
  } catch (e) {
    console.error('解析检测片段失败:', e)
    return []
  }
}
</script>

<style scoped>
.records-page {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left span {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.header-right .el-button {
  height: 40px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s;
}

.header-right .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.visualization-section {
  margin-top: 24px;
}

.behavior-statistics-section {
  margin-top: 24px;
}

.behavior-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.visualization-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: linear-gradient(135deg, #f8fafc 0%, #e9ecef 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.visualization-image {
  max-width: 100%;
  max-height: 700px;
  width: auto;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
  cursor: pointer;
}

.visualization-image:hover {
  transform: scale(1.02);
}

.video-player-container {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.video-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 16px;
  z-index: 10;
  color: #fff;
  backdrop-filter: blur(4px);
}

.video-loading-overlay p {
  margin-top: 16px;
  font-size: 16px;
  color: #fff;
  font-weight: 500;
}

.visualization-video {
  max-width: 100%;
  max-height: 700px;
  width: 100%;
  height: auto;
  border-radius: 16px;
  background: #000;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.video-controls .el-button {
  border-radius: 8px;
  transition: all 0.3s;
}

.video-controls .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.progress-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-display {
  font-size: 13px;
  color: #4a5568;
  min-width: 110px;
  text-align: right;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.image-error,
.file-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #a0aec0;
  padding: 48px;
}

.image-error .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #cbd5e0;
}

.segments-section {
  margin-top: 24px;
}

.segments-section .el-table {
  margin-top: 12px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Card enhancements */
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
  padding: 20px 24px;
}

.el-card :deep(.el-card__body) {
  padding: 24px;
}

/* Table enhancements */
.el-table {
  font-size: 14px;
}

.el-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  color: #1a202c;
  font-weight: 600;
}

.el-table :deep(.el-table__row:hover) {
  background: #f7fafc;
}

/* Dialog enhancements */
.el-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.el-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.el-dialog :deep(.el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.el-dialog :deep(.el-dialog__body)::-webkit-scrollbar {
  width: 6px;
}

.el-dialog :deep(.el-dialog__body)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.el-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.el-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* Responsive */
@media (max-width: 768px) {
  .records-page {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    width: 100%;
    justify-content: center;
  }
  
  .video-controls {
    flex-wrap: wrap;
  }
  
  .progress-container {
    width: 100%;
    order: -1;
  }
}
</style>

