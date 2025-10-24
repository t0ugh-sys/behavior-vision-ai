<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2>统计分析</h2>
      <div class="header-actions">
        <el-button type="success" @click="exportStatisticsReport">
          <el-icon><Download /></el-icon>
          导出统计报表
        </el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card>
          <el-statistic title="检测总次数" :value="statistics.total_records || 0">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <el-statistic title="异常检测次数" :value="statistics.abnormal_records || 0">
            <template #prefix>
              <el-icon style="color: #f56c6c;"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <el-statistic title="告警总数" :value="alertStatistics.total_alerts || 0">
            <template #prefix>
              <el-icon style="color: #e6a23c;"><Bell /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>检测结果分布</span>
          </template>
          <div ref="detectionChartRef" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>告警状态分布</span>
          </template>
          <div ref="alertChartRef" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="header">
              <span>检测趋势</span>
              <el-radio-group v-model="trendPeriod" @change="loadTrendData">
                <el-radio-button label="7">最近7天</el-radio-button>
                <el-radio-button label="30">最近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getUserStatistics } from '@/api/detection'
import { getAlertStatistics } from '@/api/alert'
import { exportStatistics } from '@/utils/export'
import * as echarts from 'echarts'

const userStore = useUserStore()

const statistics = ref({})
const alertStatistics = ref({})
const trendPeriod = ref('7')

const detectionChartRef = ref(null)
const alertChartRef = ref(null)
const trendChartRef = ref(null)

let detectionChart = null
let alertChart = null
let trendChart = null

onMounted(async () => {
  // 检查token是否存在
  const token = localStorage.getItem('token')
  if (token) {
    await loadStatistics()
    await nextTick()
    initCharts()
  }
})

const loadStatistics = async () => {
  const user = userStore.getUserInfo()
  if (!user) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('Token不存在，跳过加载统计')
    return
  }
  
  try {
    const detectionRes = await getUserStatistics(user.id)
    statistics.value = detectionRes.data
    
    const alertRes = await getAlertStatistics(user.id)
    alertStatistics.value = alertRes.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const initCharts = () => {
  initDetectionChart()
  initAlertChart()
  initTrendChart()
}

const initDetectionChart = () => {
  if (!detectionChartRef.value) return
  
  detectionChart = echarts.init(detectionChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '0%',
      left: 'center'
    },
    series: [
      {
        name: '检测结果',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)'
        },
        data: [
          {
            value: statistics.value.normal_records || 0,
            name: '正常',
            itemStyle: { color: '#67c23a' }
          },
          {
            value: statistics.value.abnormal_records || 0,
            name: '异常',
            itemStyle: { color: '#f56c6c' }
          }
        ]
      }
    ]
  }
  
  detectionChart.setOption(option)
}

const initAlertChart = () => {
  if (!alertChartRef.value) return
  
  alertChart = echarts.init(alertChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '0%',
      left: 'center'
    },
    series: [
      {
        name: '告警状态',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)'
        },
        data: [
          {
            value: alertStatistics.value.unhandled_alerts || 0,
            name: '未处理',
            itemStyle: { color: '#e6a23c' }
          },
          {
            value: alertStatistics.value.handled_alerts || 0,
            name: '已处理',
            itemStyle: { color: '#67c23a' }
          }
        ]
      }
    ]
  }
  
  alertChart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  
  // 使用真实数据
  const trendKey = trendPeriod.value === '7' ? 'trend_7_days' : 'trend_30_days'
  const trendData = statistics.value[trendKey] || []
  
  const dates = []
  const detectionData = []
  const abnormalData = []
  const normalData = []
  
  // 从后端数据中提取
  trendData.forEach(item => {
    dates.push(item.date)
    detectionData.push(item.total_count || 0)
    abnormalData.push(item.abnormal_count || 0)
    normalData.push(item.normal_count || 0)
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].axisValueLabel + '<br/>'
        params.forEach(param => {
          result += param.marker + param.seriesName + ': ' + param.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['检测次数', '异常次数', '正常次数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: trendPeriod.value === '30' ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '检测次数',
        type: 'line',
        smooth: true,
        data: detectionData,
        itemStyle: { color: '#409eff' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0)' }
          ])
        }
      },
      {
        name: '异常次数',
        type: 'line',
        smooth: true,
        data: abnormalData,
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0)' }
          ])
        }
      },
      {
        name: '正常次数',
        type: 'line',
        smooth: true,
        data: normalData,
        itemStyle: { color: '#67c23a' },
        lineStyle: { width: 2, type: 'dashed' }
      }
    ]
  }
  
  trendChart.setOption(option)
}

const loadTrendData = () => {
  initTrendChart()
}

// 导出统计报表
const exportStatisticsReport = () => {
  if (!statistics.value || Object.keys(statistics.value).length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  try {
    exportStatistics(statistics.value, '统计报表')
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  }
}
</script>

<style scoped>
.statistics-page {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
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

.stats-row {
  margin-bottom: 24px;
}

.chart-row {
  margin-bottom: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.el-card :deep(.el-card__body) {
  padding: 24px;
}

/* Chart containers */
.chart-row .el-card :deep(.el-card__body) {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Stat card specific styling */
.stats-row .el-card {
  cursor: pointer;
}

.stats-row .el-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

/* Responsive */
@media (max-width: 768px) {
  .statistics-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  h2 {
    font-size: 24px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .chart-row .el-card :deep(.el-card__body) {
    min-height: 300px;
  }
}
</style>

