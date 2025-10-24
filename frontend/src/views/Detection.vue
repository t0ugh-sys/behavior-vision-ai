<template>
  <div class="detection-page">
    <el-card>
      <template #header>
        <span>人体异常行为检测</span>
      </template>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 文件上传检测 -->
        <el-tab-pane label="文件检测" name="file">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="upload-section">
                <el-radio-group v-model="sourceType" class="source-type-group">
                  <el-radio-button label="IMAGE">图片</el-radio-button>
                  <el-radio-button label="VIDEO">视频</el-radio-button>
                </el-radio-group>
                
                <el-upload
                  ref="uploadRef"
                  class="upload-area"
                  drag
                  :auto-upload="false"
                  :limit="1"
                  :accept="sourceType === 'IMAGE' ? 'image/*' : 'video/*'"
                  :on-change="handleFileChange"
                  :file-list="fileList"
                  :show-file-list="false"
                >
                  <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                  <div class="el-upload__text">
                    拖拽文件到此处或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      {{ sourceType === 'IMAGE' ? '支持JPG、PNG格式' : '支持MP4、AVI格式' }}
                    </div>
                  </template>
                </el-upload>
                
                <!-- 文件预览 -->
                <div v-if="previewUrl" class="file-preview">
                  <div class="preview-header">
                    <span class="preview-title">{{ currentFileName }}</span>
                    <el-button type="danger" size="small" text @click="removeFile">
                      <el-icon><Close /></el-icon> 移除
                    </el-button>
                  </div>
                  <div class="preview-content">
                    <img v-if="sourceType === 'IMAGE'" :src="previewUrl" alt="预览图片" />
                    <video v-else :src="previewUrl" controls></video>
                  </div>
                </div>
                
                <div class="button-group">
                  <el-button
                    type="primary"
                    size="large"
                    :loading="detecting"
                    :disabled="!currentFile || detecting"
                    @click="startDetection"
                    class="detect-button"
                  >
                    开始检测
                  </el-button>
                  <el-button
                    v-if="detectionResult"
                    type="success"
                    size="large"
                    @click="resetUpload"
                    class="detect-button"
                  >
                    重新上传
                  </el-button>
                </div>
              </div>
            </el-col>
            
            <el-col :span="12">
              <div class="result-section">
                <h3>检测结果</h3>
                <div v-if="!detectionResult" class="empty-result">
                  <el-empty description="等待检测..." />
                </div>
                <div v-else class="result-content">
                  <!-- 可视化结果（图片或视频） -->
                  <div v-if="detectionResult.visualization_url" class="visualization-container">
                    <!-- 图片类型 -->
                    <template v-if="sourceType === 'IMAGE'">
                      <el-image
                        :src="detectionResult.visualization_url"
                        :preview-src-list="[detectionResult.visualization_url]"
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
                      <div class="visualization-tip">
                        <el-icon><ZoomIn /></el-icon>
                        点击图片可放大查看
                      </div>
                    </template>
                    
                    <!-- 视频类型 -->
                    <template v-else-if="sourceType === 'VIDEO'">
                      <div class="video-player-wrapper">
                        <!-- 视频加载动画 -->
                        <div v-if="detectionVideoLoading" class="video-loading-overlay">
                          <el-icon class="is-loading" :size="50">
                            <Loading />
                          </el-icon>
                          <p>加载视频中...</p>
                        </div>
                        
                        <video
                          ref="detectionVideoRef"
                          :src="detectionResult.visualization_url"
                          controls
                          class="visualization-video"
                          @loadstart="handleDetectionVideoLoadStart"
                          @canplay="handleDetectionVideoCanPlay"
                          @error="handleDetectionVideoError"
                        >
                          您的浏览器不支持视频播放
                        </video>
                      </div>
                      <div class="visualization-tip">
                        <el-icon><VideoCamera /></el-icon>
                        可视化检测结果视频
                      </div>
                    </template>
                  </div>
                  
                  <el-alert
                    :title="detectionResult.has_abnormal ? '检测到异常行为！' : '未检测到异常'"
                    :type="detectionResult.has_abnormal ? 'error' : 'success'"
                    :closable="false"
                    show-icon
                  />
                  
                  <!-- 检测详细信息 -->
                  <el-descriptions :column="2" border style="margin-top: 20px;">
                    <el-descriptions-item label="检测状态">
                      <el-tag :type="detectionResult.has_abnormal ? 'danger' : 'success'" size="large">
                        {{ detectionResult.has_abnormal ? '异常' : '正常' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="检测人数">
                      <el-tag type="info" size="large">{{ detectionResult.person_count }} 人</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item v-if="detectionResult.has_abnormal" label="行为类型" :span="2">
                      <el-tag type="danger" size="large">{{ getBehaviorTypeName(detectionResult.behavior_type) }}</el-tag>
                    </el-descriptions-item>
                    
                    <el-descriptions-item v-if="detectionResult.has_abnormal" label="置信度" :span="2">
                      <el-progress
                        :percentage="parseFloat((detectionResult.confidence * 100).toFixed(1))"
                        :color="getConfidenceColor(detectionResult.confidence)"
                        :stroke-width="20"
                      />
                    </el-descriptions-item>
                    
                    <el-descriptions-item label="描述" :span="2">
                      {{ detectionResult.description }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>
        
        <!-- 实时摄像头检测 -->
        <el-tab-pane label="摄像头检测" name="realtime">
          <div class="realtime-section">
            <el-alert
              title="摄像头检测功能"
              type="info"
              description="此功能需要访问您的摄像头权限，检测到异常行为时会自动发送告警。"
              :closable="false"
            />
            
            <div class="camera-container">
              <video
                ref="videoRef"
                class="camera-video"
                autoplay
                playsinline
                style="display: none;"
              ></video>
              <canvas 
                ref="canvasRef" 
                class="camera-canvas"
              ></canvas>
            </div>
            
            <div class="camera-controls">
              <el-button
                v-if="!cameraActive"
                type="primary"
                size="large"
                @click="startCamera"
              >
                启动摄像头
              </el-button>
              <el-button
                v-else
                type="danger"
                size="large"
                @click="stopCamera"
              >
                停止检测
              </el-button>
            </div>
            
            <div v-if="realtimeResult" class="realtime-result">
              <el-alert
                :title="realtimeResult.has_abnormal ? '检测到异常行为！' : '监控正常'"
                :type="realtimeResult.has_abnormal ? 'error' : 'success'"
                :closable="false"
                show-icon
                style="margin-bottom: 20px;"
              />
              
              <el-descriptions :column="2" border>
                <el-descriptions-item label="检测状态">
                  <el-tag :type="realtimeResult.has_abnormal ? 'danger' : 'success'" size="large">
                    {{ realtimeResult.has_abnormal ? '异常' : '正常' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="检测人数">
                  <el-tag type="info" size="large">{{ realtimeResult.person_count }} 人</el-tag>
                </el-descriptions-item>
                
                <el-descriptions-item v-if="realtimeResult.has_abnormal" label="异常类型" :span="2">
                  <el-tag type="danger" size="large">{{ getBehaviorTypeName(realtimeResult.behavior_type) }}</el-tag>
                </el-descriptions-item>
                
                <el-descriptions-item v-if="realtimeResult.has_abnormal" label="置信度" :span="2">
                  <el-progress
                    :percentage="parseFloat((realtimeResult.confidence * 100).toFixed(1))"
                    :color="getConfidenceColor(realtimeResult.confidence)"
                    :stroke-width="20"
                  />
                </el-descriptions-item>
                
                <el-descriptions-item label="描述" :span="2">
                  {{ realtimeResult.description || '实时监控中...' }}
                </el-descriptions-item>
                
                <el-descriptions-item label="最后更新" :span="2">
                  {{ formatRealtimeUpdateTime() }}
                </el-descriptions-item>
              </el-descriptions>
              
              <!-- 异常历史记录 -->
              <div v-if="realtimeAbnormalHistory.length > 0" class="abnormal-history">
                <el-divider content-position="left">
                  <el-text tag="b">异常检测历史</el-text>
                </el-divider>
                <el-timeline>
                  <el-timeline-item
                    v-for="(item, index) in realtimeAbnormalHistory.slice(0, 5)"
                    :key="index"
                    :timestamp="item.timestamp"
                    :type="item.type"
                  >
                    <el-tag type="danger" size="small">{{ getBehaviorTypeName(item.behavior_type) }}</el-tag>
                    <span style="margin-left: 10px;">置信度: {{ (item.confidence * 100).toFixed(1) }}%</span>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- RTSP流检测 -->
        <el-tab-pane label="RTSP流检测" name="rtsp">
          <div class="rtsp-section">
            <el-alert
              title="RTSP流检测功能"
              type="info"
              description="连接到IP摄像头或RTSP流进行实时检测，支持多种视频流协议。"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <!-- RTSP URL 输入 -->
            <el-card class="rtsp-config-card">
              <template #header>
                <div class="card-header">
                  <span>流配置</span>
                </div>
              </template>
              
              <el-form :model="rtspConfig" label-width="120px">
                <el-form-item label="RTSP URL">
                  <el-input
                    v-model="rtspConfig.url"
                    placeholder="rtsp://username:password@ip:port/stream"
                    :disabled="rtspActive"
                  >
                    <template #prepend>
                      <el-icon><VideoCamera /></el-icon>
                    </template>
                  </el-input>
                  <div class="help-text">
                    示例: rtsp://admin:12345@192.168.1.100:554/stream1
                  </div>
                </el-form-item>
                
                <el-form-item label="检测间隔">
                  <el-select v-model="rtspConfig.interval" :disabled="rtspActive">
                    <el-option label="1秒" :value="1000" />
                    <el-option label="2秒" :value="2000" />
                    <el-option label="3秒" :value="3000" />
                    <el-option label="5秒" :value="5000" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="启用告警">
                  <el-switch v-model="rtspConfig.enableAlert" />
                </el-form-item>
              </el-form>
              
              <div class="rtsp-controls">
                <el-button
                  v-if="!rtspActive"
                  type="primary"
                  size="large"
                  @click="startRTSP"
                  :disabled="!rtspConfig.url"
                >
                  <el-icon><VideoPlay /></el-icon>
                  连接RTSP流
                </el-button>
                <el-button
                  v-else
                  type="danger"
                  size="large"
                  @click="stopRTSP"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止检测
                </el-button>
              </div>
            </el-card>
            
            <!-- RTSP视频显示 -->
            <div v-if="rtspActive" class="rtsp-video-container">
              <canvas ref="rtspCanvasRef" class="rtsp-canvas"></canvas>
            </div>
            
            <!-- RTSP检测结果 -->
            <div v-if="rtspResult" class="rtsp-result">
              <el-alert
                :title="rtspResult.has_abnormal ? '检测到异常行为！' : '监控正常'"
                :type="rtspResult.has_abnormal ? 'error' : 'success'"
                :closable="false"
                show-icon
                style="margin-bottom: 20px;"
              />
              
              <el-descriptions :column="2" border>
                <el-descriptions-item label="检测状态">
                  <el-tag :type="rtspResult.has_abnormal ? 'danger' : 'success'" size="large">
                    {{ rtspResult.has_abnormal ? '异常' : '正常' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="检测人数">
                  <el-tag type="info" size="large">{{ rtspResult.person_count }} 人</el-tag>
                </el-descriptions-item>
                
                <el-descriptions-item v-if="rtspResult.has_abnormal" label="异常类型" :span="2">
                  <el-tag type="danger" size="large">{{ getBehaviorTypeName(rtspResult.behavior_type) }}</el-tag>
                </el-descriptions-item>
                
                <el-descriptions-item v-if="rtspResult.has_abnormal" label="置信度" :span="2">
                  <el-progress
                    :percentage="parseFloat((rtspResult.confidence * 100).toFixed(1))"
                    :color="getConfidenceColor(rtspResult.confidence)"
                    :stroke-width="20"
                  />
                </el-descriptions-item>
                
                <el-descriptions-item label="描述" :span="2">
                  {{ rtspResult.description || 'RTSP流监控中...' }}
                </el-descriptions-item>
                
                <el-descriptions-item label="最后更新" :span="2">
                  {{ formatRTSPUpdateTime() }}
                </el-descriptions-item>
              </el-descriptions>
              
              <!-- 异常历史记录 -->
              <div v-if="rtspAbnormalHistory.length > 0" class="abnormal-history">
                <el-divider content-position="left">
                  <el-text tag="b">异常检测历史</el-text>
                </el-divider>
                <el-timeline>
                  <el-timeline-item
                    v-for="(item, index) in rtspAbnormalHistory.slice(0, 5)"
                    :key="index"
                    :timestamp="item.timestamp"
                    :type="item.type"
                  >
                    <el-tag type="danger" size="small">{{ getBehaviorTypeName(item.behavior_type) }}</el-tag>
                    <span style="margin-left: 10px;">置信度: {{ (item.confidence * 100).toFixed(1) }}%</span>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadAndDetect, getDetectionRecord } from '@/api/detection'
import { useUserStore } from '@/stores/user'
import { VideoCamera, VideoPlay, VideoPause, PictureFilled, ZoomIn, Loading } from '@element-plus/icons-vue'
import axios from 'axios'

const userStore = useUserStore()

const activeTab = ref('file')
const sourceType = ref('IMAGE')
const currentFile = ref(null)
const currentFileName = ref('')
const fileList = ref([])
const previewUrl = ref('')
const detecting = ref(false)
const detectionResult = ref(null)
const detectionVideoRef = ref(null)
const detectionVideoLoading = ref(false)

const videoRef = ref(null)
const canvasRef = ref(null)
const cameraActive = ref(false)
const cameraStream = ref(null)
const realtimeResult = ref(null)
const realtimeAbnormalHistory = ref([])
const realtimeUpdateTime = ref(null)
let detectionInterval = null
let renderLoop = null

// RTSP相关
const rtspCanvasRef = ref(null)
const rtspActive = ref(false)
const rtspResult = ref(null)
const rtspAbnormalHistory = ref([])
const rtspUpdateTime = ref(null)
const rtspConfig = ref({
  url: '',
  interval: 2000,
  enableAlert: true
})
let rtspDetectionInterval = null
let rtspRenderLoop = null

const handleTabChange = () => {
  // 切换标签页时重置状态
  detectionResult.value = null
  realtimeResult.value = null
}

const handleFileChange = (file) => {
  // 如果已经有文件，提示用户是否替换
  if (currentFile.value) {
    const hasResult = detectionResult.value !== null
    const message = hasResult 
      ? '已有检测结果，上传新文件将清空当前结果，是否继续？'
      : '已有文件，是否替换为新文件？'
    
    ElMessageBox.confirm(
      message,
      '确认替换',
      {
        confirmButtonText: '替换',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    ).then(() => {
      // 用户确认替换
      replaceFile(file)
    }).catch(() => {
      // 用户取消，恢复文件列表（阻止el-upload更新）
      fileList.value = currentFile.value ? [{
        name: currentFileName.value,
        url: previewUrl.value
      }] : []
    })
  } else {
    // 没有文件，直接设置
    replaceFile(file)
  }
}

// 替换文件的函数
const replaceFile = (file) => {
  currentFile.value = file.raw
  currentFileName.value = file.name
  fileList.value = [file]
  detectionResult.value = null
  
  // 清除旧的预览URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  // 生成新的预览URL
  previewUrl.value = URL.createObjectURL(file.raw)
  
  ElMessage.success('文件已更新')
}

const removeFile = () => {
  currentFile.value = null
  currentFileName.value = ''
  fileList.value = []
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  detectionResult.value = null
}

const resetUpload = () => {
  // 重置所有上传相关的状态
  currentFile.value = null
  currentFileName.value = ''
  fileList.value = []
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  detectionResult.value = null
  detecting.value = false
  
  ElMessage.success('已重置，可以上传新文件')
}

const startDetection = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  detecting.value = true
  detectionResult.value = null
  
  try {
    const user = userStore.getUserInfo()
    const formData = new FormData()
    formData.append('file', currentFile.value)
    formData.append('userId', user.id)
    formData.append('sourceType', sourceType.value)
    
    const res = await uploadAndDetect(formData)
    
    if (res.code === 200) {
      const recordId = res.data.id
      ElMessage.success('文件上传成功，正在检测...')
      
      // 轮询获取检测结果
      let pollCount = 0
      const maxPollCount = 120 // 最多轮询2分钟
      
      const pollResult = async () => {
        try {
          pollCount++
          console.log(`轮询检测结果 (${pollCount}/${maxPollCount}), recordId: ${recordId}`)
          
          // 使用配置好的API方法，会自动添加token
          const resultRes = await getDetectionRecord(recordId)
          
          if (resultRes.code === 200) {
            const record = resultRes.data
            console.log('当前状态:', record.status)
            
            if (record.status === 'COMPLETED') {
              // 解析检测结果
              let detailResult = {}
              try {
                if (typeof record.detectionResult === 'string') {
                  detailResult = JSON.parse(record.detectionResult)
                } else {
                  detailResult = record.detectionResult
                }
              } catch (e) {
                console.error('解析检测结果失败:', e)
                detailResult = {}
              }
              
              // 设置检测结果
              detectionResult.value = {
                has_abnormal: record.hasAbnormal || false,
                behavior_type: record.behaviorType || null,
                confidence: record.confidence || 0,
                description: detailResult.description || (record.hasAbnormal ? '检测到异常行为' : '未检测到异常行为'),
                person_count: detailResult.person_count || 0,
                visualization_url: record.visualizationUrl || null
              }
              
              console.log('检测结果:', detectionResult.value)
              console.log('可视化URL:', record.visualizationUrl)
              
              ElMessage.success('检测完成')
              detecting.value = false
            } else if (record.status === 'FAILED') {
              ElMessage.error('检测失败: ' + (record.errorMessage || '未知错误'))
              detecting.value = false
            } else {
              // 检查是否超时
              if (pollCount >= maxPollCount) {
                ElMessage.error('检测超时，请稍后到检测记录中查看结果')
                detecting.value = false
                return
              }
              // 继续轮询
              setTimeout(pollResult, 1000)
            }
          } else {
            // API返回了错误code
            console.error('API返回错误:', resultRes)
            if (pollCount >= maxPollCount) {
              ElMessage.error('获取结果失败: ' + (resultRes.message || '未知错误'))
              detecting.value = false
            } else {
              // 可能是记录还未完全创建，继续轮询
              setTimeout(pollResult, 1000)
            }
          }
        } catch (error) {
          console.error('获取检测结果失败:', error)
          console.error('错误详情:', error.response?.data)
          
          // 如果是401或403错误，说明token有问题
          if (error.response?.status === 401 || error.response?.status === 403) {
            ElMessage.error('登录已过期，请重新登录')
            detecting.value = false
            return
          }
          
          // 如果轮询次数未超限，继续尝试
          if (pollCount < maxPollCount) {
            setTimeout(pollResult, 1000)
          } else {
            ElMessage.error('获取检测结果失败，请到检测记录中查看')
            detecting.value = false
          }
        }
      }
      
      // 延迟2秒后开始轮询，给后端足够时间创建记录
      setTimeout(pollResult, 2000)
    } else {
      ElMessage.error(res.message || '上传失败')
      detecting.value = false
    }
    
  } catch (error) {
    ElMessage.error('检测失败: ' + (error.message || '未知错误'))
    console.error(error)
    detecting.value = false
  }
}

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720, facingMode: 'user' }
    })
    
    cameraStream.value = stream
    const video = videoRef.value
    video.srcObject = stream
    
    // 等待视频加载
    await new Promise((resolve) => {
      video.onloadedmetadata = () => {
        video.play()
        resolve()
      }
    })
    
    // 设置canvas尺寸
    const canvas = canvasRef.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    cameraActive.value = true
    
    // 开始渲染循环
    startRenderLoop()
    
    // 开始定期检测（每2秒检测一次）
    detectionInterval = setInterval(captureAndDetect, 2000)
    
    ElMessage.success('摄像头已启动')
  } catch (error) {
    ElMessage.error('无法访问摄像头: ' + error.message)
    console.error(error)
  }
}

const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(track => track.stop())
    cameraStream.value = null
  }
  
  if (detectionInterval) {
    clearInterval(detectionInterval)
    detectionInterval = null
  }
  
  if (renderLoop) {
    cancelAnimationFrame(renderLoop)
    renderLoop = null
  }
  
  cameraActive.value = false
  realtimeResult.value = null
  realtimeAbnormalHistory.value = []
  realtimeUpdateTime.value = null
  
  ElMessage.info('摄像头已停止')
}

// 渲染循环 - 持续绘制视频帧和检测结果
const startRenderLoop = () => {
  const render = () => {
    if (!cameraActive.value) return
    
    const video = videoRef.value
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    
    if (video && canvas && ctx) {
      // 绘制视频帧
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // 绘制检测结果
      if (realtimeResult.value && realtimeResult.value.persons) {
        drawDetectionResults(ctx, realtimeResult.value)
      }
    }
    
    renderLoop = requestAnimationFrame(render)
  }
  
  render()
}

// 绘制检测结果
const drawDetectionResults = (ctx, result) => {
  const scaleX = canvasRef.value.width / 640  // 假设检测时缩放到640
  const scaleY = canvasRef.value.height / 480
  
  // 骨架连接定义
  const skeleton = [
    [15, 13], [13, 11], [16, 14], [14, 12], [11, 12],  // 腿部
    [5, 11], [6, 12],  // 躯干
    [5, 7], [6, 8], [7, 9], [8, 10],  // 手臂
    [5, 6],  // 肩膀
    [0, 1], [0, 2], [1, 3], [2, 4], [5, 0], [6, 0]  // 头部
  ]
  
  // 遍历每个人
  result.persons.forEach((person, personIndex) => {
    const keypoints = person.keypoints
    const box = person.box
    
    // 绘制边界框
    if (box) {
      const [x1, y1, x2, y2] = box
      const color = result.has_abnormal ? '#ff4444' : '#00ff00'
      
      ctx.strokeStyle = color
      ctx.lineWidth = 3
      ctx.strokeRect(x1 * scaleX, y1 * scaleY, (x2 - x1) * scaleX, (y2 - y1) * scaleY)
      
      // 绘制标签
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      ctx.fillRect(x1 * scaleX, y1 * scaleY - 30, 150, 30)
      
      ctx.fillStyle = color
      ctx.font = 'bold 16px Arial'
      ctx.fillText(`Person ${personIndex + 1}`, x1 * scaleX + 5, y1 * scaleY - 8)
    }
    
    // 绘制骨架
    skeleton.forEach(([idx1, idx2]) => {
      if (idx1 < keypoints.length && idx2 < keypoints.length) {
        const kpt1 = keypoints[idx1]
        const kpt2 = keypoints[idx2]
        
        if (kpt1[2] > 0.5 && kpt2[2] > 0.5) {
          const color = result.has_abnormal ? '#ff4444' : '#00ff00'
          ctx.strokeStyle = color
          ctx.lineWidth = 4
          ctx.beginPath()
          ctx.moveTo(kpt1[0] * scaleX, kpt1[1] * scaleY)
          ctx.lineTo(kpt2[0] * scaleX, kpt2[1] * scaleY)
          ctx.stroke()
        }
      }
    })
    
    // 绘制关键点
    keypoints.forEach((kpt) => {
      if (kpt[2] > 0.5) {
        const x = kpt[0] * scaleX
        const y = kpt[1] * scaleY
        
        // 外圈白色
        ctx.fillStyle = '#ffffff'
        ctx.beginPath()
        ctx.arc(x, y, 6, 0, 2 * Math.PI)
        ctx.fill()
        
        // 内圈红色
        ctx.fillStyle = '#ff0000'
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fill()
      }
    })
  })
  
  // 绘制顶部状态信息
  drawStatusInfo(ctx, result)
}

// 绘制状态信息
const drawStatusInfo = (ctx, result) => {
  const canvas = canvasRef.value
  
  // 半透明背景
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
  ctx.fillRect(10, 10, 300, result.has_abnormal ? 120 : 80)
  
  // 状态文字
  if (result.has_abnormal) {
    ctx.fillStyle = '#ff4444'
    ctx.font = 'bold 24px Arial'
    ctx.fillText('⚠ ABNORMAL', 20, 40)
    
    ctx.fillStyle = '#ffffff'
    ctx.font = '18px Arial'
    ctx.fillText(`类型: ${getBehaviorTypeName(result.behavior_type)}`, 20, 70)
    ctx.fillText(`置信度: ${(result.confidence * 100).toFixed(1)}%`, 20, 95)
    ctx.fillText(`人数: ${result.person_count}`, 20, 120)
  } else {
    ctx.fillStyle = '#00ff00'
    ctx.font = 'bold 24px Arial'
    ctx.fillText('✓ NORMAL', 20, 40)
    
    ctx.fillStyle = '#ffffff'
    ctx.font = '18px Arial'
    ctx.fillText(`人数: ${result.person_count}`, 20, 70)
  }
  
  // 右下角时间戳
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
  ctx.fillRect(canvas.width - 210, canvas.height - 40, 200, 30)
  
  ctx.fillStyle = '#ffffff'
  ctx.font = '16px Arial'
  const now = new Date()
  const timeStr = now.toLocaleTimeString('zh-CN')
  ctx.fillText(timeStr, canvas.width - 200, canvas.height - 15)
}

const captureAndDetect = async () => {
  const video = videoRef.value
  
  if (!video || !video.videoWidth) return
  
  // 创建临时canvas用于捕获帧
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = 640  // 降低分辨率以加快检测速度
  tempCanvas.height = 480
  const context = tempCanvas.getContext('2d')
  
  // 绘制当前帧
  context.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height)
  
  // 将canvas转为blob并发送到Python服务
  tempCanvas.toBlob(async (blob) => {
    if (!blob) return
    
    try {
      const user = userStore.getUserInfo()
      if (!user) return
      
      const formData = new FormData()
      formData.append('frame_data', blob, 'frame.jpg')
      formData.append('user_id', user.id)
      formData.append('enable_alert', 'true')
      formData.append('alert_threshold', '0.7')
      formData.append('save_record', 'false')  // 实时检测不保存记录
      
      const response = await axios.post('http://localhost:5000/detect/realtime', formData, {
        timeout: 5000
      })
      
      realtimeResult.value = response.data
      
      // 更新时间戳
      realtimeUpdateTime.value = new Date()
      
      // 如果检测到异常，添加到历史记录
      if (response.data.has_abnormal) {
        const now = new Date()
        const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
        
        realtimeAbnormalHistory.value.unshift({
          behavior_type: response.data.behavior_type,
          confidence: response.data.confidence,
          timestamp: timestamp,
          type: 'danger'
        })
        
        // 只保留最近20条记录
        if (realtimeAbnormalHistory.value.length > 20) {
          realtimeAbnormalHistory.value = realtimeAbnormalHistory.value.slice(0, 20)
        }
      }
    } catch (error) {
      console.error('实时检测失败:', error)
    }
  }, 'image/jpeg', 0.85)  // 85%质量
}

const formatRealtimeUpdateTime = () => {
  if (!realtimeUpdateTime.value) return '未更新'
  
  const now = new Date()
  const diff = Math.floor((now - realtimeUpdateTime.value) / 1000)
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}秒前`
  
  const minutes = Math.floor(diff / 60)
  if (minutes < 60) return `${minutes}分钟前`
  
  return realtimeUpdateTime.value.toLocaleTimeString('zh-CN')
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#f56c6c'
  if (confidence >= 0.7) return '#e6a23c'
  return '#67c23a'
}

const getBehaviorTypeName = (type) => {
  if (!type) return '正常'
  
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

// ========== RTSP流检测功能 ==========

const startRTSP = async () => {
  if (!rtspConfig.value.url) {
    ElMessage.warning('请输入RTSP流地址')
    return
  }
  
  try {
    ElMessage.loading('正在连接RTSP流...')
    
    const user = userStore.getUserInfo()
    const response = await axios.post('http://localhost:5000/rtsp/start', {
      rtsp_url: rtspConfig.value.url,
      user_id: user.id,
      enable_alert: rtspConfig.value.enableAlert,
      detection_interval: rtspConfig.value.interval / 1000  // 转换为秒
    })
    
    if (response.data.status === 'success') {
      rtspActive.value = true
      ElMessage.success('RTSP流已连接')
      
      // 初始化canvas
      setTimeout(() => {
        const canvas = rtspCanvasRef.value
        if (canvas) {
          canvas.width = 1280
          canvas.height = 720
        }
      }, 100)
      
      // 开始轮询获取帧和检测结果
      startRTSPPolling()
    } else {
      ElMessage.error(response.data.message || 'RTSP连接失败')
    }
  } catch (error) {
    console.error('RTSP连接失败:', error)
    ElMessage.error('RTSP连接失败: ' + (error.response?.data?.detail || error.message))
  }
}

const stopRTSP = async () => {
  try {
    await axios.post('http://localhost:5000/rtsp/stop')
    
    if (rtspDetectionInterval) {
      clearInterval(rtspDetectionInterval)
      rtspDetectionInterval = null
    }
    
    if (rtspRenderLoop) {
      cancelAnimationFrame(rtspRenderLoop)
      rtspRenderLoop = null
    }
    
    rtspActive.value = false
    rtspResult.value = null
    rtspAbnormalHistory.value = []
    rtspUpdateTime.value = null
    
    ElMessage.info('RTSP流已停止')
  } catch (error) {
    console.error('停止RTSP失败:', error)
    ElMessage.error('停止RTSP失败')
  }
}

const startRTSPPolling = () => {
  // 定期获取最新帧和检测结果
  rtspDetectionInterval = setInterval(async () => {
    try {
      // 获取最新帧
      const frameResponse = await axios.get('http://localhost:5000/rtsp/frame', {
        responseType: 'blob',
        timeout: 5000
      })
      
      if (frameResponse.data && frameResponse.data.size > 0) {
        // 显示帧到canvas
        const canvas = rtspCanvasRef.value
        if (canvas) {
          const ctx = canvas.getContext('2d')
          const img = new Image()
          img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
            URL.revokeObjectURL(img.src)
          }
          img.src = URL.createObjectURL(frameResponse.data)
        }
      }
      
      // 获取检测结果
      const resultResponse = await axios.get('http://localhost:5000/rtsp/result')
      if (resultResponse.data) {
        rtspResult.value = resultResponse.data
        rtspUpdateTime.value = new Date()
        
        // 如果检测到异常，添加到历史
        if (resultResponse.data.has_abnormal) {
          const now = new Date()
          const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
          
          rtspAbnormalHistory.value.unshift({
            behavior_type: resultResponse.data.behavior_type,
            confidence: resultResponse.data.confidence,
            timestamp: timestamp,
            type: 'danger'
          })
          
          if (rtspAbnormalHistory.value.length > 20) {
            rtspAbnormalHistory.value = rtspAbnormalHistory.value.slice(0, 20)
          }
        }
        
        // 绘制检测结果
        if (resultResponse.data.persons) {
          const canvas = rtspCanvasRef.value
          if (canvas) {
            const ctx = canvas.getContext('2d')
            drawDetectionResults(ctx, resultResponse.data)
          }
        }
      }
    } catch (error) {
      if (!error.message.includes('timeout')) {
        console.error('RTSP轮询失败:', error)
      }
    }
  }, 1000)  // 每秒获取一次帧
}

const formatRTSPUpdateTime = () => {
  if (!rtspUpdateTime.value) return '未更新'
  
  const now = new Date()
  const diff = Math.floor((now - rtspUpdateTime.value) / 1000)
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}秒前`
  
  const minutes = Math.floor(diff / 60)
  if (minutes < 60) return `${minutes}分钟前`
  
  return rtspUpdateTime.value.toLocaleTimeString('zh-CN')
}

// 视频加载处理
const handleDetectionVideoLoadStart = () => {
  detectionVideoLoading.value = true
}

const handleDetectionVideoCanPlay = () => {
  detectionVideoLoading.value = false
}

const handleDetectionVideoError = (e) => {
  detectionVideoLoading.value = false
  console.error('视频加载失败:', e)
  ElMessage.error('视频加载失败，请检查网络连接')
}

// 页面卸载时清理资源
onUnmounted(() => {
  stopCamera()
  stopRTSP()
})
</script>

<style scoped>
.detection-page {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.upload-section {
  padding: 0;
}

.source-type-group {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.source-type-group :deep(.el-radio-button__inner) {
  padding: 12px 32px;
  font-weight: 500;
  border-radius: 12px;
}

.upload-area {
  margin-bottom: 24px;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 48px;
  border-radius: 16px;
  border: 2px dashed #c0c4cc;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.button-group {
  display: flex;
  gap: 12px;
}

.button-group .el-button {
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s;
}

.button-group .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.detect-button {
  flex: 1;
}

.file-preview {
  margin: 24px 0;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  background: #fff;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  border-bottom: 1px solid #e2e8f0;
}

.preview-title {
  font-size: 15px;
  color: #1a202c;
  font-weight: 600;
}

.preview-content {
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fafafa;
}

.preview-content img {
  max-width: 100%;
  max-height: 480px;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-content video {
  max-width: 100%;
  max-height: 480px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-section {
  padding: 0;
}

.result-section h3 {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
}

.visualization-container {
  margin-bottom: 24px;
  border: 2px solid rgba(64, 158, 255, 0.5);
  border-radius: 16px;
  overflow: hidden;
  background: #000;
  position: relative;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.2);
  transition: all 0.3s;
}

.visualization-container:hover {
  border-color: #409eff;
  box-shadow: 0 12px 24px rgba(64, 158, 255, 0.3);
}

.visualization-image {
  width: 100%;
  height: auto;
  display: block;
  min-height: 480px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.visualization-image:hover {
  opacity: 0.95;
}

.video-player-wrapper {
  position: relative;
  width: 100%;
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
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  z-index: 10;
  color: #fff;
  min-height: 400px;
}

.video-loading-overlay p {
  margin-top: 16px;
  font-size: 16px;
  color: #fff;
}

.visualization-video {
  width: 100%;
  height: auto;
  display: block;
  min-height: 400px;
  border-radius: 8px;
  background: #000;
}

.visualization-tip {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  pointer-events: none;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #909399;
}

.image-error .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.result-content {
  max-height: 80vh;
  overflow-y: auto;
}

.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.abnormal-info {
  margin-top: 10px;
}

.realtime-section {
  padding: 0;
}

.camera-container {
  margin: 24px 0;
  display: flex;
  justify-content: center;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.camera-video {
  width: 100%;
  max-width: 100%;
  height: auto;
}

.camera-canvas {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 16px;
  background: #000;
}

.camera-controls {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 24px 0;
}

.camera-controls .el-button {
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s;
}

.camera-controls .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.realtime-result {
  margin-top: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.abnormal-history {
  margin-top: 32px;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.abnormal-history .el-timeline {
  padding-left: 10px;
}

/* RTSP相关样式 */
.rtsp-section {
  padding: 0;
}

.rtsp-config-card {
  margin-bottom: 24px;
}

.help-text {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 8px;
  line-height: 1.5;
}

.rtsp-controls {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.rtsp-controls .el-button {
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s;
}

.rtsp-controls .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.rtsp-video-container {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  min-height: 480px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.rtsp-canvas {
  max-width: 100%;
  max-height: 720px;
  width: auto;
  height: auto;
  border-radius: 16px;
}

.rtsp-result {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}
</style>

