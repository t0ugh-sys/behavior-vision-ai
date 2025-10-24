<template>
  <div class="settings-page">
    <h2>系统设置</h2>
    
    <el-row :gutter="20">
      <!-- 个人信息 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          
          <el-form :model="userForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input v-model="userForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item label="手机号">
              <el-input v-model="userForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateUserInfo">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 修改密码 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>修改密码</span>
          </template>
          
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入原密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 检测配置 -->
    <el-row>
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>检测配置</span>
          </template>
          
          <el-form :model="detectionConfig" label-width="150px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="检测置信度阈值">
                  <el-slider
                    v-model="detectionConfig.confidence_threshold"
                    :min="0.3"
                    :max="0.95"
                    :step="0.05"
                    show-input
                    :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
                  />
                  <div class="form-tip">检测结果置信度低于此阈值将被过滤</div>
                </el-form-item>
                
                <el-form-item label="告警阈值">
                  <el-slider
                    v-model="detectionConfig.alert_threshold"
                    :min="0.5"
                    :max="0.95"
                    :step="0.05"
                    show-input
                    :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
                  />
                  <div class="form-tip">异常行为置信度高于此阈值将触发告警</div>
                </el-form-item>
                
                <el-form-item label="自动保存记录">
                  <div class="form-control-wrapper">
                    <el-switch v-model="detectionConfig.auto_save_record" />
                    <span class="control-tip">自动保存检测记录到数据库</span>
                  </div>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用告警通知">
                  <div class="form-control-wrapper">
                    <el-switch v-model="detectionConfig.enable_alert" />
                    <span class="control-tip">检测到异常时发送告警通知</span>
                  </div>
                </el-form-item>
                
                <el-form-item label="告警声音">
                  <div class="form-control-wrapper">
                    <el-switch v-model="detectionConfig.alert_sound" />
                    <span class="control-tip">告警时播放提示音</span>
                  </div>
                </el-form-item>
                
                <el-form-item label="检测间隔(秒)">
                  <div class="form-control-wrapper">
                    <el-input-number
                      v-model="detectionConfig.detection_interval"
                      :min="1"
                      :max="60"
                      :step="1"
                    />
                    <span class="control-tip">实时检测的帧采样间隔</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="saveDetectionConfig">保存配置</el-button>
              <el-button @click="resetDetectionConfig">恢复默认</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 系统配置 -->
    <el-row>
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统配置</span>
          </template>
          
          <el-form :model="systemConfig" label-width="150px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="语言">
                  <el-select v-model="systemConfig.language" style="width: 100%;">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="主题">
                  <el-select v-model="systemConfig.theme" style="width: 100%;">
                    <el-option label="浅色" value="light" />
                    <el-option label="深色" value="dark" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="自动刷新">
                  <div class="form-control-wrapper">
                    <el-switch v-model="systemConfig.auto_refresh" />
                    <span class="control-tip">页面数据自动刷新</span>
                  </div>
                </el-form-item>
                
                <el-form-item label="刷新间隔(秒)">
                  <div class="form-control-wrapper">
                    <el-input-number
                      v-model="systemConfig.refresh_interval"
                      :min="5"
                      :max="300"
                      :step="5"
                      :disabled="!systemConfig.auto_refresh"
                    />
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="saveSystemConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const passwordFormRef = ref(null)

// 用户信息表单
const userForm = reactive({
  username: '',
  email: '',
  phone: ''
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 检测配置
const detectionConfig = reactive({
  confidence_threshold: 0.6,
  alert_threshold: 0.7,
  auto_save_record: true,
  enable_alert: true,
  alert_sound: true,
  detection_interval: 2
})

// 系统配置
const systemConfig = reactive({
  language: 'zh-CN',
  theme: 'light',
  auto_refresh: false,
  refresh_interval: 30
})

onMounted(() => {
  loadUserInfo()
  loadDetectionConfig()
  loadSystemConfig()
})

// 加载用户信息
const loadUserInfo = () => {
  const user = userStore.getUserInfo()
  if (user) {
    userForm.username = user.username
    userForm.email = user.email || ''
    userForm.phone = user.phone || ''
  }
}

// 更新用户信息
const updateUserInfo = async () => {
  try {
    // TODO: 调用后端API更新用户信息
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败: ' + error.message)
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: 调用后端API修改密码
        ElMessage.success('密码修改成功，请重新登录')
        setTimeout(() => {
          userStore.logout()
        }, 1500)
      } catch (error) {
        ElMessage.error('修改失败: ' + error.message)
      }
    }
  })
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordFormRef.value?.clearValidate()
}

// 加载检测配置
const loadDetectionConfig = () => {
  const saved = localStorage.getItem('detection_config')
  if (saved) {
    Object.assign(detectionConfig, JSON.parse(saved))
  }
}

// 保存检测配置
const saveDetectionConfig = () => {
  localStorage.setItem('detection_config', JSON.stringify(detectionConfig))
  ElMessage.success('检测配置已保存')
}

// 恢复默认检测配置
const resetDetectionConfig = () => {
  detectionConfig.confidence_threshold = 0.6
  detectionConfig.alert_threshold = 0.7
  detectionConfig.auto_save_record = true
  detectionConfig.enable_alert = true
  detectionConfig.alert_sound = true
  detectionConfig.detection_interval = 2
  ElMessage.success('已恢复默认配置')
}

// 加载系统配置
const loadSystemConfig = () => {
  const saved = localStorage.getItem('system_config')
  if (saved) {
    Object.assign(systemConfig, JSON.parse(saved))
  }
}

// 保存系统配置
const saveSystemConfig = () => {
  localStorage.setItem('system_config', JSON.stringify(systemConfig))
  ElMessage.success('系统配置已保存')
}
</script>

<style scoped>
.settings-page {
  padding: 32px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

h2 {
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.el-row {
  margin-bottom: 32px;
}

/* 控件包装容器 */
.form-control-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 控件旁边的说明文字 */
.control-tip {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  flex: 1;
}

/* 滑块下方的说明文字 */
.form-tip {
  font-size: 13px;
  color: #64748b;
  margin-top: 12px;
  line-height: 1.6;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-left: 3px solid #6495ED;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Card enhancements */
.el-card {
  border-radius: 20px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(100, 149, 237, 0.04);
  border: 1px solid rgba(100, 149, 237, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #fff;
  overflow: hidden;
}

.el-card:hover {
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(100, 149, 237, 0.1);
  transform: translateY(-2px);
}

.el-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #fafbfc 0%, #fff 100%);
  border-bottom: 2px solid rgba(100, 149, 237, 0.1);
  padding: 24px 28px;
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.3px;
}

.el-card :deep(.el-card__body) {
  padding: 36px 28px;
}

/* Form enhancements */
.el-form-item {
  margin-bottom: 32px;
}

.el-form-item :deep(.el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
  font-size: 15px;
  padding-bottom: 8px;
}

.el-input :deep(.el-input__inner),
.el-input-number :deep(.el-input__inner),
.el-select :deep(.el-input__inner) {
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  padding: 12px 16px;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-input :deep(.el-input__inner):hover,
.el-input-number :deep(.el-input__inner):hover,
.el-select :deep(.el-input__inner):hover {
  border-color: #cbd5e1;
}

.el-input :deep(.el-input__inner):focus,
.el-input-number :deep(.el-input__inner):focus,
.el-select :deep(.el-input__inner):focus {
  border-color: #6495ED;
  box-shadow: 0 0 0 4px rgba(100, 149, 237, 0.12);
}

.el-button {
  border-radius: 12px;
  font-weight: 600;
  padding: 12px 28px;
  font-size: 15px;
  letter-spacing: 0.3px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.el-button--primary {
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(100, 149, 237, 0.3);
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #5885E0 0%, #7569E0 100%);
  box-shadow: 0 6px 16px rgba(100, 149, 237, 0.4);
}

/* Divider styling */
.el-divider {
  margin: 32px 0;
}

.el-divider :deep(.el-divider__text) {
  background: #fff;
  font-weight: 600;
  color: #1a202c;
  padding: 0 16px;
}

/* Switch styling */
.el-switch {
  margin-top: 4px;
}

.el-switch :deep(.el-switch__core) {
  height: 26px;
  min-width: 50px;
  border-radius: 13px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.el-switch.is-checked :deep(.el-switch__core) {
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  border-color: #6495ED;
  box-shadow: 0 2px 8px rgba(100, 149, 237, 0.3);
}

.el-switch :deep(.el-switch__action) {
  width: 20px;
  height: 20px;
}

/* Slider styling */
.el-slider {
  padding: 4px 12px;
  margin-top: 8px;
}

.el-slider :deep(.el-slider__runway) {
  height: 8px;
  border-radius: 10px;
  background: #e2e8f0;
}

.el-slider :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #6495ED, #8B7FED);
  border-radius: 10px;
}

.el-slider :deep(.el-slider__button) {
  width: 20px;
  height: 20px;
  border: 3px solid #6495ED;
  box-shadow: 0 2px 8px rgba(100, 149, 237, 0.3);
  transition: all 0.3s;
}

.el-slider :deep(.el-slider__button):hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(100, 149, 237, 0.5);
}

/* Input Number styling */
.el-input-number {
  width: auto;
  min-width: 150px;
}

.form-control-wrapper .el-input-number {
  flex-shrink: 0;
}

.el-input-number :deep(.el-input-number__decrease),
.el-input-number :deep(.el-input-number__increase) {
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.3s;
}

.el-input-number :deep(.el-input-number__decrease):hover,
.el-input-number :deep(.el-input-number__increase):hover {
  background: #e2e8f0;
  color: #6495ED;
}

/* Responsive */
@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
  }
  
  h2 {
    font-size: 24px;
  }
  
  .el-card :deep(.el-card__header) {
    padding: 20px 20px;
    font-size: 18px;
  }
  
  .el-card :deep(.el-card__body) {
    padding: 24px 20px;
  }
  
  .form-control-wrapper {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .control-tip {
    padding-left: 0;
    font-size: 13px;
  }
  
  .el-form-item {
    margin-bottom: 24px;
  }
}
</style>

