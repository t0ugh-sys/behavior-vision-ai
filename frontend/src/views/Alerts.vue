<template>
  <div class="alerts-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>告警管理</span>
          <div class="header-actions">
            <el-radio-group v-model="filterStatus" @change="loadAlerts">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="unhandled">未处理</el-radio-button>
              <el-radio-button label="handled">已处理</el-radio-button>
            </el-radio-group>
            <el-button
              v-if="selectedAlerts.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedAlerts.length }})
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
            <el-button type="primary" @click="loadAlerts">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="alerts"
        v-loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="告警类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getAlertTypeColor(row.alertType)">
              {{ row.alertType }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="告警级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getAlertLevelColor(row.alertLevel)">
              {{ row.alertLevel }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" />
        
        <el-table-column label="置信度" width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="(row.confidence * 100).toFixed(1)"
              :color="getConfidenceColor(row.confidence)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isHandled ? 'success' : 'warning'">
              {{ row.isHandled ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="createdAt" label="告警时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" fixed="right" width="260">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(row)"
            >
              详情
            </el-button>
            <el-button
              v-if="!row.isHandled"
              type="success"
              size="small"
              @click="handleAlert(row)"
            >
              处理
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
      title="告警详情"
      width="60%"
    >
      <el-descriptions v-if="currentAlert" :column="2" border>
        <el-descriptions-item label="告警ID">{{ currentAlert.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentAlert.userId }}</el-descriptions-item>
        <el-descriptions-item label="记录ID">{{ currentAlert.recordId }}</el-descriptions-item>
        <el-descriptions-item label="告警类型">
          <el-tag :type="getAlertTypeColor(currentAlert.alertType)">
            {{ currentAlert.alertType }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="告警级别">
          <el-tag :type="getAlertLevelColor(currentAlert.alertLevel)">
            {{ currentAlert.alertLevel }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          {{ (currentAlert.confidence * 100).toFixed(1) }}%
        </el-descriptions-item>
        <el-descriptions-item label="是否已处理">
          <el-tag :type="currentAlert.isHandled ? 'success' : 'warning'">
            {{ currentAlert.isHandled ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="告警时间">
          {{ formatTime(currentAlert.createdAt) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ currentAlert.description }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.snapshotPath" label="告警快照" :span="2">
          <el-image
            :src="getSnapshotUrl(currentAlert.snapshotPath)"
            :preview-src-list="[getSnapshotUrl(currentAlert.snapshotPath)]"
            fit="contain"
            style="max-width: 400px; max-height: 300px; cursor: pointer;"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>图片加载失败</span>
              </div>
            </template>
          </el-image>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.isHandled" label="处理人" :span="2">
          {{ currentAlert.handledBy }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.isHandled" label="处理时间" :span="2">
          {{ formatTime(currentAlert.handledAt) }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert.isHandled" label="处理备注" :span="2">
          {{ currentAlert.handleNote || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <!-- 处理对话框 -->
    <el-dialog
      v-model="handleVisible"
      title="处理告警"
      width="500px"
    >
      <el-form :model="handleForm" label-width="100px">
        <el-form-item label="处理人">
          <el-input v-model="handleForm.handled_by" placeholder="请输入处理人姓名" />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input
            v-model="handleForm.handle_note"
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandle">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAlerts, handleAlert as handleAlertApi, deleteAlert, batchDeleteAlerts } from '@/api/alert'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'
import { exportAlerts, exportToCSV, exportToJSON, printTable } from '@/utils/export'

const userStore = useUserStore()

const loading = ref(false)
const alerts = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterStatus = ref('all')
const selectedAlerts = ref([])

const detailVisible = ref(false)
const currentAlert = ref(null)

const handleVisible = ref(false)
const currentHandleAlert = ref(null)
const handleForm = reactive({
  handled_by: '',
  handle_note: ''
})

onMounted(() => {
  // 检查token是否存在
  const token = localStorage.getItem('token')
  if (token) {
    loadAlerts()
    // 设置默认处理人
    const user = userStore.getUserInfo()
    if (user) {
      handleForm.handled_by = user.username
    }
  }
})

const loadAlerts = async () => {
  const user = userStore.getUserInfo()
  if (!user) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('Token不存在，跳过加载告警')
    return
  }
  
  loading.value = true
  
  try {
    const res = await getAlerts(user.id, currentPage.value - 1, pageSize.value)
    let data = res.data.content
    
    // 根据筛选条件过滤
    if (filterStatus.value === 'unhandled') {
      data = data.filter(item => !item.isHandled)
    } else if (filterStatus.value === 'handled') {
      data = data.filter(item => item.isHandled)
    }
    
    alerts.value = data
    total.value = res.data.totalElements
  } catch (error) {
    console.error('加载告警失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  loadAlerts()
}

const handleCurrentChange = () => {
  loadAlerts()
}

const viewDetail = (row) => {
  currentAlert.value = row
  detailVisible.value = true
}

const handleAlert = (row) => {
  currentHandleAlert.value = row
  handleVisible.value = true
}

const submitHandle = async () => {
  if (!handleForm.handled_by) {
    ElMessage.warning('请输入处理人')
    return
  }
  
  try {
    await handleAlertApi(currentHandleAlert.value.id, handleForm)
    ElMessage.success('处理成功')
    handleVisible.value = false
    handleForm.handle_note = ''
    loadAlerts()
  } catch (error) {
    ElMessage.error('处理失败')
    console.error(error)
  }
}

const getAlertTypeColor = (type) => {
  const colorMap = {
    'FALL': 'danger',
    'FIGHT': 'danger',
    'INTRUSION': 'warning',
    'ABNORMAL_POSE': 'warning'
  }
  return colorMap[type] || 'info'
}

const getAlertLevelColor = (level) => {
  const colorMap = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info'
  }
  return colorMap[level] || 'info'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#f56c6c'
  if (confidence >= 0.7) return '#e6a23c'
  return '#67c23a'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 获取快照URL
const getSnapshotUrl = (snapshotPath) => {
  if (!snapshotPath) return ''
  
  // 如果已经是完整URL，直接返回
  if (snapshotPath.startsWith('http://') || snapshotPath.startsWith('https://')) {
    return snapshotPath
  }
  
  // 否则拼接Python服务地址
  return `http://localhost:5000/${snapshotPath}`
}

// 删除功能
const handleSelectionChange = (selection) => {
  selectedAlerts.value = selection
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      '删除告警将同时删除相关的快照文件，此操作不可恢复，是否继续？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await deleteAlert(row.id)
    ElMessage.success('删除成功')
    loadAlerts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || error))
      console.error('删除失败:', error)
    }
  } finally {
    loading.value = false
  }
}

const handleBatchDelete = async () => {
  if (selectedAlerts.value.length === 0) {
    ElMessage.warning('请先选择要删除的告警')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedAlerts.value.length} 条告警吗？此操作将同时删除相关的快照文件，且不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    const alertIds = selectedAlerts.value.map(alert => alert.id)
    await batchDeleteAlerts(alertIds)
    ElMessage.success(`成功删除 ${alertIds.length} 条告警`)
    selectedAlerts.value = []
    loadAlerts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败: ' + (error.message || error))
      console.error('批量删除失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 导出功能
const handleExport = (command) => {
  if (alerts.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  try {
    switch (command) {
      case 'excel':
        exportAlerts(alerts.value, '告警记录')
        ElMessage.success('导出成功')
        break
      case 'csv':
        exportToCSV(alerts.value, '告警记录')
        ElMessage.success('导出成功')
        break
      case 'json':
        exportToJSON(alerts.value, '告警记录')
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
  if (alerts.value.length === 0) {
    ElMessage.warning('暂无数据可打印')
    return
  }
  
  const columns = [
    { label: 'ID', prop: 'id' },
    { label: '告警类型', prop: 'alertType' },
    { label: '告警级别', prop: 'alertLevel' },
    { label: '置信度', prop: 'confidence', formatter: (row) => `${(row.confidence * 100).toFixed(1)}%` },
    { label: '描述', prop: 'description' },
    { label: '是否已处理', prop: 'isHandled', formatter: (row) => row.isHandled ? '是' : '否' },
    { label: '告警时间', prop: 'createdAt', formatter: (row) => formatTime(row.createdAt) }
  ]
  
  printTable('告警记录', columns, alerts.value)
}
</script>

<style scoped>
.alerts-page {
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

.header span {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.header-actions .el-button {
  height: 40px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s;
}

.header-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #f8fafc 0%, #e9ecef 100%);
  border-radius: 12px;
  color: #a0aec0;
  font-size: 14px;
}

.image-error .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: #cbd5e0;
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
  border-radius: 12px;
  overflow: hidden;
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

/* Alert snapshot styling */
.el-image {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.el-image:hover {
  transform: scale(1.02);
}

/* Responsive */
@media (max-width: 768px) {
  .alerts-page {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>

