<template>
  <div class="login-container">
    <!-- 背景动画圆圈 -->
    <div class="bg-circles">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
    
    <div class="login-box">
      <!-- Logo和标题 -->
      <div class="logo-section">
        <div class="logo-icon">
          <el-icon :size="50"><VideoCamera /></el-icon>
        </div>
        <h2 class="login-title">人体异常行为检测系统</h2>
        <p class="login-subtitle">AI-Powered Behavior Detection</p>
      </div>
      
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button"
                :loading="loading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱（选填）"
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-button"
                :loading="loading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'
import { login, register } from '@/api/user'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  email: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await login(loginForm)
        console.log('登录响应:', res)
        
        // 保存用户信息和token
        userStore.setUserInfo(res.data)
        
        ElMessage.success('登录成功')
        
        // 延迟跳转，确保token已保存
        setTimeout(() => {
          router.replace('/')
        }, 100)
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.response?.data?.message || error.message || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await register(registerForm)
        ElMessage.success('注册成功，请登录')
        activeTab.value = 'login'
        loginForm.username = registerForm.username
      } catch (error) {
        console.error('注册失败:', error)
        ElMessage.error(error.response?.data?.message || error.message || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #ecf0f1 0%, #f8f9fa 50%, #e9ecef 100%);
  overflow: hidden;
}

/* 背景动画圆圈 */
.bg-circles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(100, 149, 237, 0.12);
  animation: float 20s infinite ease-in-out;
  box-shadow: 0 0 60px rgba(100, 149, 237, 0.15);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 20%;
  right: 15%;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: 80%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-50px) rotate(180deg);
  }
}

/* 登录框 - 玻璃拟态效果 */
.login-box {
  position: relative;
  width: 480px;
  padding: 50px 45px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(100, 149, 237, 0.1) inset,
    0 8px 32px rgba(100, 149, 237, 0.12);
  animation: slideIn 0.5s ease-out;
  z-index: 10;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 35px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  border-radius: 22px;
  box-shadow: 
    0 10px 30px rgba(100, 149, 237, 0.4),
    0 0 0 2px rgba(100, 149, 237, 0.15);
  animation: pulse 2s infinite;
}

.logo-icon :deep(.el-icon) {
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 
      0 10px 30px rgba(100, 149, 237, 0.4),
      0 0 0 2px rgba(100, 149, 237, 0.15);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 
      0 15px 40px rgba(100, 149, 237, 0.6),
      0 0 0 2px rgba(100, 149, 237, 0.25);
  }
}

.login-title {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  margin: 0;
  font-size: 14px;
  color: #888;
  letter-spacing: 1px;
}

/* 标签页样式 */
.login-tabs {
  margin-top: 10px;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  color: #666;
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #6495ED;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #6495ED 0%, #8B7FED 100%);
  height: 3px;
}

/* 表单样式 */
.login-form {
  margin-top: 30px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(100, 149, 237, 0.15);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(100, 149, 237, 0.3);
  border-color: #6495ED;
}

.login-form :deep(.el-input__inner) {
  font-size: 15px;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6495ED 0%, #8B7FED 100%);
  border: none;
  box-shadow: 0 8px 20px rgba(100, 149, 237, 0.4);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(100, 149, 237, 0.6);
  background: linear-gradient(135deg, #5885E0 0%, #7569E0 100%);
}

.login-button:active {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    width: 90%;
    padding: 40px 30px;
  }
  
  .circle {
    display: none;
  }
}
</style>

