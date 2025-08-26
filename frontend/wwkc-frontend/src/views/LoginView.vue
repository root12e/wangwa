<template>
  <div class="login-container">
    <div class="login-background">
      <!-- 背景装饰 -->
      <div class="bg-decoration bg-1"></div>
      <div class="bg-decoration bg-2"></div>
      <div class="bg-decoration bg-3"></div>
      
      <!-- 主要内容 -->
      <div class="login-content">
        <div class="login-card card">
          <!-- 系统Logo和标题 -->
          <div class="login-header">
            <div class="logo-container">
              <div class="logo-icon">
                <el-icon><Shop /></el-icon>
              </div>
              <h1 class="system-title">WWKC库存管理系统</h1>
            </div>
            <p class="system-subtitle">专业的库存管理解决方案</p>
          </div>

          <!-- 登录表单 -->
          <div class="login-form" v-if="!showRegister">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账户</p>
            
            <el-form 
              ref="loginFormRef" 
              :model="loginForm" 
              :rules="loginRules" 
              @submit.prevent="handleLogin"
              class="form"
            >
              <el-form-item prop="username_or_phone">
                <el-input
                  v-model="loginForm.username_or_phone"
                  placeholder="用户名或手机号"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
              
              <div class="form-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <el-button type="text" @click="showForgotPassword = true">忘记密码？</el-button>
              </div>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  size="large" 
                  class="submit-btn"
                  :loading="loginLoading"
                  @click="handleLogin"
                >
                  {{ loginLoading ? '登录中...' : '登录' }}
                </el-button>
              </el-form-item>
            </el-form>
            
            <div class="form-footer">
              <p>还没有账户？ 
                <el-button type="text" @click="showRegister = true">立即注册</el-button>
              </p>
            </div>
          </div>

          <!-- 注册表单 -->
          <div class="register-form" v-if="showRegister">
            <h2 class="form-title">创建账户</h2>
            <p class="form-subtitle">请填写以下信息完成注册</p>
            
            <el-form 
              ref="registerFormRef" 
              :model="registerForm" 
              :rules="registerRules" 
              @submit.prevent="handleRegister"
              class="form"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="phone">
                <el-input
                  v-model="registerForm.phone"
                  placeholder="手机号"
                  size="large"
                  :prefix-icon="Phone"
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="邮箱地址"
                  size="large"
                  :prefix-icon="Message"
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="email_verification_code">
                <div class="verification-code-input">
                  <el-input
                    v-model="registerForm.email_verification_code"
                    placeholder="邮箱验证码"
                    size="large"
                    :prefix-icon="Key"
                    clearable
                  />
                  <el-button 
                    type="primary" 
                    :disabled="codeCountdown > 0"
                    @click="sendVerificationCode"
                  >
                    {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
                  </el-button>
                </div>
              </el-form-item>
              
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="confirm_password">
                <el-input
                  v-model="registerForm.confirm_password"
                  type="password"
                  placeholder="确认密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
              
              <el-form-item prop="role">
                <el-select
                  v-model="registerForm.role"
                  placeholder="选择角色"
                  size="large"
                  style="width: 100%"
                  @change="handleRoleChange"
                >
                  <el-option 
                    label="超级管理员" 
                    value="super_admin" 
                    :disabled="!canRegisterSuperAdmin"
                  />
                  <el-option label="部门管理员" value="department_manager" />
                  <el-option label="店铺运营" value="store_operator" />
                  <el-option label="普通员工" value="staff" />
                </el-select>
              </el-form-item>
              
              <el-form-item prop="department" v-if="registerForm.role === 'department_manager'">
                <el-select
                  v-model="registerForm.department"
                  placeholder="选择部门"
                  size="large"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="dept in departments" 
                    :key="dept.id" 
                    :label="dept.name" 
                    :value="dept.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  size="large" 
                  class="submit-btn"
                  :loading="registerLoading"
                  @click="handleRegister"
                >
                  {{ registerLoading ? '注册中...' : '注册' }}
                </el-button>
              </el-form-item>
            </el-form>
            
            <div class="form-footer">
              <p>已有账户？ 
                <el-button type="text" @click="showRegister = false">立即登录</el-button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="showForgotPassword"
      title="忘记密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef">
        <el-form-item prop="email">
          <el-input
            v-model="forgotPasswordForm.email"
            placeholder="请输入注册邮箱"
            :prefix-icon="Message"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showForgotPassword = false">取消</el-button>
          <el-button type="primary" @click="handleForgotPassword">发送重置邮件</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Phone, Message, Key, Shop } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

// 路由和状态管理
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const showRegister = ref(false)
const showForgotPassword = ref(false)
const loginLoading = ref(false)
const registerLoading = ref(false)
const codeCountdown = ref(0)
const rememberMe = ref(false)

// 表单引用
const loginFormRef = ref()
const registerFormRef = ref()
const forgotPasswordFormRef = ref()

// 登录表单
const loginForm = reactive({
  username_or_phone: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  phone: '',
  email: '',
  password: '',
  confirm_password: '',
  email_verification_code: '',
  role: 'staff',
  department: ''
})

// 忘记密码表单
const forgotPasswordForm = reactive({
  email: ''
})

// 部门列表
const departments = ref<Array<{id: string, name: string}>>([])
const canRegisterSuperAdmin = ref(true)

// 表单验证规则
const loginRules = {
  username_or_phone: [
    { required: true, message: '请输入用户名或手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  email_verification_code: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  department: [
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (registerForm.role === 'department_manager' && !value) {
          callback(new Error('部门管理员必须选择部门'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const forgotPasswordRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 发送验证码
const sendVerificationCode = async () => {
  try {
    await registerFormRef.value.validateField('email')
    
    const result = await authStore.sendVerificationCode(registerForm.email)
    
    if (result && result.success) {
      ElMessage.success('验证码已发送到您的邮箱')
      startCountdown()
    } else {
      ElMessage.error('发送失败，请重试')
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error('发送失败，请重试')
  }
}

// 开始倒计时
const startCountdown = () => {
  codeCountdown.value = 60
  const timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 处理登录
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loginLoading.value = true
    
    const result = await authStore.login(loginForm)
    
    if (result && result.success) {
      if (rememberMe.value) {
        localStorage.setItem('rememberMe', 'true')
      }
      
      ElMessage.success('登录成功')
      
      // 检查是否有重定向地址
      const redirect = router.currentRoute.value.query.redirect as string
      if (redirect) {
        router.push(redirect)
      } else {
        router.push('/')
      }
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请重试')
  } finally {
    loginLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    
    const result = await authStore.register(registerForm)
    
    if (result && result.success) {
      ElMessage.success('注册成功！请登录')
      showRegister.value = false
      // 清空注册表单
      Object.keys(registerForm).forEach((key: string) => {
        if (key in registerForm) {
          (registerForm as any)[key] = key === 'role' ? 'staff' : ''
        }
      })
      // 重置倒计时
      codeCountdown.value = 0
    } else {
      // 显示具体的错误信息
      if (result && result.error && result.details) {
        // 如果有字段级别的错误，显示具体字段错误
        const errorMessages = []
        for (const [field, message] of Object.entries(result.details)) {
          const fieldNames: Record<string, string> = {
            'username': '用户名',
            'phone': '手机号',
            'email': '邮箱',
            'email_verification_code': '验证码',
            'password': '密码',
            'confirm_password': '确认密码',
            'role': '角色',
            'department': '部门'
          }
          const fieldName = fieldNames[field] || field
          errorMessages.push(`${fieldName}: ${message}`)
        }
        ElMessage.error(errorMessages.join('\n'))
      } else if (result && result.message) {
        ElMessage.error(result.message)
      } else {
        ElMessage.error('注册失败，请重试')
      }
    }
  } catch (error: any) {
    console.error('注册失败:', error)
    // 显示具体的错误信息
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.details) {
        const errorMessages = []
        for (const [field, message] of Object.entries(errorData.details)) {
          const fieldNames: Record<string, string> = {
            'username': '用户名',
            'phone': '手机号',
            'email': '邮箱',
            'email_verification_code': '验证码',
            'password': '密码',
            'confirm_password': '确认密码',
            'role': '角色',
            'department': '部门'
          }
          const fieldName = fieldNames[field] || field
          errorMessages.push(`${fieldName}: ${message}`)
        }
        ElMessage.error(errorMessages.join('\n'))
      } else if (errorData.message) {
        ElMessage.error(errorData.message)
      } else {
        ElMessage.error('注册失败，请重试')
      }
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    registerLoading.value = false
  }
}

// 处理忘记密码
const handleForgotPassword = async () => {
  try {
    await forgotPasswordFormRef.value.validate()
    
    const result = await authStore.forgotPassword(forgotPasswordForm.email)
    
    if (result && result.success) {
      ElMessage.success('重置密码邮件已发送到您的邮箱')
      showForgotPassword.value = false
      forgotPasswordForm.email = ''
    } else {
      ElMessage.error('发送失败，请重试')
    }
  } catch (error) {
    console.error('忘记密码处理失败:', error)
    ElMessage.error('发送失败，请重试')
  }
}

// 处理角色变化
const handleRoleChange = () => {
  if (registerForm.role !== 'department_manager') {
    registerForm.department = ''
  }
}

// 检查超级管理员是否存在
const checkSuperAdminExists = async () => {
  try {
    // 这里需要调用API检查超级管理员是否存在
    // 暂时设置为true，后续可以通过API调用
    canRegisterSuperAdmin.value = true
  } catch (error) {
    console.error('检查超级管理员失败:', error)
  }
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    // 这里需要调用API获取部门列表
    // 暂时设置为空数组，后续可以通过API调用
    departments.value = []
  } catch (error) {
    console.error('加载部门失败:', error)
  }
}

// 页面加载时的处理
onMounted(() => {
  // 检查是否已经登录
  if (authStore.isAuthenticated) {
    router.push('/')
  }
  
  // 恢复记住我状态
  const remembered = localStorage.getItem('rememberMe')
  if (remembered === 'true') {
    rememberMe.value = true
  }

  // 加载部门列表
  loadDepartments()
  // 检查超级管理员是否存在
  checkSuperAdminExists()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-ultra-light) 0%, var(--background-color) 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.bg-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.bg-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.bg-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.login-content {
  width: 100%;
  max-width: 450px;
  z-index: 1;
}

.login-card {
  padding: var(--spacing-xxl);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.logo-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.system-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.system-subtitle {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  text-align: center;
}

.form-subtitle {
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.form {
  margin-bottom: var(--spacing-lg);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  border: none;
  border-radius: var(--border-radius-large);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.form-footer {
  text-align: center;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.verification-code-input {
  display: flex;
  gap: var(--spacing-md);
}

.verification-code-input .el-input {
  flex: 1;
}

.verification-code-input .el-button {
  width: 120px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    padding: var(--spacing-xl);
  }
  
  .system-title {
    font-size: 1.5rem;
  }
  
  .bg-decoration {
    display: none;
  }
}

/* 动画效果 */
.login-card {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单切换动画 */
.login-form,
.register-form {
  transition: all 0.3s ease;
}

.form-options .el-checkbox {
  color: var(--text-secondary);
}

.form-options .el-button {
  color: var(--primary-color);
  font-weight: 500;
}

.form-footer .el-button {
  color: var(--primary-color);
  font-weight: 600;
}
</style>
