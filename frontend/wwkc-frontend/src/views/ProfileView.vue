<template>
  <div class="profile-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>个人资料</h1>
      <p class="page-description">管理您的个人信息和账户设置</p>
    </div>

    <!-- 个人资料卡片 -->
    <div class="profile-card card fade-in-up" style="animation-delay: 0.1s">
      <div class="card-header">
        <h2>基本信息</h2>
        <el-button 
          type="primary" 
          @click="editMode = !editMode"
          :icon="editMode ? Close : Edit"
        >
          {{ editMode ? '取消编辑' : '编辑资料' }}
        </el-button>
      </div>

      <el-form 
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="120px"
        :disabled="!editMode"
      >
        <div class="form-row">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="profileForm.username" placeholder="请输入用户名" />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            <div class="field-hint">
              <el-tag v-if="profileForm.is_email_verified" type="success" size="small">
                <el-icon><Check /></el-icon>
                已验证
              </el-tag>
              <el-tag v-else type="warning" size="small">
                <el-icon><Warning /></el-icon>
                未验证
              </el-tag>
            </div>
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          
          <el-form-item label="角色">
            <el-input v-model="roleDisplayName" disabled />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="所属部门">
            <el-input v-model="departmentDisplayName" disabled />
          </el-form-item>
          
          <el-form-item label="所属店铺">
            <el-input v-model="storeDisplayName" disabled />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="账户状态">
            <el-tag :type="getStatusTagType(profileForm.status)">
              {{ getStatusDisplayName(profileForm.status) }}
            </el-tag>
          </el-form-item>
          
          <el-form-item label="注册时间">
            <span>{{ formatDate(profileForm.created_at) }}</span>
          </el-form-item>
        </div>

        <div v-if="editMode" class="form-actions">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="saveProfile" :loading="saving">
            保存更改
          </el-button>
        </div>
      </el-form>
    </div>

    <!-- 修改密码卡片 -->
    <div class="password-card card fade-in-up" style="animation-delay: 0.2s">
      <div class="card-header">
        <h2>修改密码</h2>
        <el-button 
          type="warning" 
          @click="showPasswordDialog = true"
          :icon="Lock"
        >
          修改密码
        </el-button>
      </div>
      
      <div class="password-info">
        <p>为了账户安全，建议定期更换密码。密码应包含字母、数字和特殊字符。</p>
      </div>
    </div>

    <!-- 账户安全卡片 -->
    <div class="security-card card fade-in-up" style="animation-delay: 0.3s">
      <div class="card-header">
        <h2>账户安全</h2>
      </div>
      
      <div class="security-items">
        <div class="security-item">
          <div class="security-info">
            <el-icon class="security-icon"><Message /></el-icon>
            <div class="security-details">
              <h4>邮箱验证</h4>
              <p>{{ profileForm.is_email_verified ? '已验证' : '未验证' }}</p>
            </div>
          </div>
          <el-button 
            v-if="!profileForm.is_email_verified"
            type="primary" 
            size="small"
            @click="sendVerificationEmail"
            :loading="sendingEmail"
          >
            发送验证码
          </el-button>
        </div>
        
        <div class="security-item">
          <div class="security-info">
            <el-icon class="security-icon"><Phone /></el-icon>
            <div class="security-details">
              <h4>手机号绑定</h4>
              <p>{{ profileForm.phone ? '已绑定' : '未绑定' }}</p>
            </div>
          </div>
        </div>
        
        <div class="security-item">
          <div class="security-info">
            <el-icon class="security-icon"><Message /></el-icon>
            <div class="security-details">
              <h4>消息中心</h4>
              <p>
                未读消息: 
                <span v-if="loadingUnreadCount" class="loading-state">
                  <el-icon class="loading-icon"><Loading /></el-icon>
                  <span class="loading-text">正在加载...</span>
                </span>
                <span v-else-if="unreadCountError" class="error-text">
                  加载失败
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="loadUnreadMessageCount"
                    class="retry-btn"
                  >
                    重试
                  </el-button>
                </span>
                <span v-else-if="unreadMessageCount === 0" class="no-unread">无未读消息</span>
                <el-badge 
                  v-else
                  :value="unreadMessageCount" 
                  type="danger"
                  class="unread-badge"
                />
              </p>
            </div>
          </div>
          <div class="security-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="goToMessages"
              title="查看所有消息"
              :disabled="loadingUnreadCount"
            >
              查看消息
            </el-button>
            <el-button 
              type="success" 
              size="small"
              @click="goToChatRooms"
              title="进入聊天室"
              :disabled="loadingUnreadCount"
            >
              聊天室
            </el-button>
            <el-button 
              type="info" 
              size="small"
              @click="refreshUnreadCount"
              :icon="Refresh"
              :loading="loadingUnreadCount"
              title="刷新未读消息数量"
            >
              刷新
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
      @close="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="120px"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input 
            v-model="passwordForm.old_password" 
            type="password" 
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="new_password">
          <el-input 
            v-model="passwordForm.new_password" 
            type="password" 
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input 
            v-model="passwordForm.confirm_password" 
            type="password" 
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="changePassword"
            :loading="changingPassword"
          >
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 邮箱验证对话框 -->
    <el-dialog
      v-model="showEmailDialog"
      title="邮箱验证"
      width="500px"
    >
      <div class="email-verification">
        <p>验证码已发送到您的邮箱：<strong>{{ profileForm.email }}</strong></p>
        <p>请输入收到的验证码：</p>
        
        <el-form
          ref="emailFormRef"
          :model="emailForm"
          :rules="emailRules"
          label-width="80px"
        >
          <el-form-item label="验证码" prop="code">
            <el-input 
              v-model="emailForm.code" 
              placeholder="请输入6位验证码"
              maxlength="6"
              show-word-limit
            />
          </el-form-item>
        </el-form>
        
        <div class="verification-actions">
          <el-button 
            @click="resendVerificationCode"
            :disabled="countdown > 0"
          >
            {{ countdown > 0 ? `${countdown}秒后重发` : '重新发送' }}
          </el-button>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEmailDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="verifyEmailCode"
            :loading="verifyingEmail"
          >
            验证
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit,
  Close,
  Check,
  Warning,
  Lock,
  Message,
  Phone,
  Clock,
  Refresh,
  Loading
} from '@element-plus/icons-vue'
import { 
  getCurrentUserProfile, 
  updateCurrentUserProfile,
  changePassword
} from '@/api/user'
import { useAuthStore } from '@/stores/auth'

// 响应式数据
const editMode = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const sendingEmail = ref(false)
const verifyingEmail = ref(false)
const showPasswordDialog = ref(false)
const showEmailDialog = ref(false)
const countdown = ref(0)
const unreadMessageCount = ref(0)
const loadingUnreadCount = ref(false)
const unreadCountError = ref(false)

// 表单引用
const profileFormRef = ref()
const passwordFormRef = ref()
const emailFormRef = ref()

// 权限存储
const authStore = useAuthStore()
const router = useRouter()

// 个人资料表单
const profileForm = ref({
  id: '',
  username: '',
  email: '',
  phone: '',
  role: '',
  department: null as any,
  store: null as any,
  status: '',
  is_email_verified: false,
  created_at: '',
  last_login: ''
})

// 修改密码表单
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 邮箱验证表单
const emailForm = ref({
  code: ''
})

// 计算属性
const roleDisplayName = computed(() => {
  return getRoleDisplayName(profileForm.value.role)
})

const departmentDisplayName = computed(() => {
  return profileForm.value.department?.name || '未分配'
})

const storeDisplayName = computed(() => {
  return profileForm.value.store?.name || '未分配'
})

// 表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const emailRules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码长度应为6位', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  loadProfile()
  loadUnreadMessageCount()
  
  // 每30秒自动刷新未读消息数量
  const interval = setInterval(() => {
    if (authStore.isAuthenticated) {
      loadUnreadMessageCount()
    }
  }, 30000)
  
  // 组件卸载时清理定时器
  onUnmounted(() => {
    clearInterval(interval)
  })
})

// 加载个人资料
const loadProfile = async () => {
  try {
    const response = await getCurrentUserProfile()
    if (response && response.data) {
      profileForm.value = { ...response.data }
    }
  } catch (error) {
    console.error('加载个人资料失败:', error)
    ElMessage.error('加载个人资料失败')
  }
}

// 保存个人资料
const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    saving.value = true
    
    const updateData = {
      username: profileForm.value.username,
      email: profileForm.value.email,
      phone: profileForm.value.phone
    }
    
    await updateCurrentUserProfile(updateData)
    ElMessage.success('个人资料更新成功')
    editMode.value = false
    
    // 重新加载资料
    await loadProfile()
    
    // 更新认证存储中的用户信息
    authStore.updateUserInfo(updateData)
    
  } catch (error: any) {
    console.error('更新个人资料失败:', error)
    
    let errorMessage = '更新个人资料失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
  // 重置表单数据
  loadProfile()
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    await changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      confirm_password: passwordForm.value.confirm_password
    })
    
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
    resetPasswordForm()
    
  } catch (error: any) {
    console.error('修改密码失败:', error)
    
    let errorMessage = '修改密码失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    }
    
    ElMessage.error(errorMessage)
  } finally {
    changingPassword.value = false
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

// 发送邮箱验证码
const sendVerificationEmail = async () => {
  try {
    sendingEmail.value = true
    // 这里需要调用发送验证码的API
    // await sendEmailVerificationCode({ email: profileForm.value.email })
    
    ElMessage.success('验证码已发送到您的邮箱')
    showEmailDialog.value = true
    startCountdown()
    
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error('发送验证码失败')
  } finally {
    sendingEmail.value = false
  }
}

// 重新发送验证码
const resendVerificationCode = async () => {
  if (countdown.value > 0) return
  
  try {
    await sendVerificationEmail()
  } catch (error) {
    console.error('重新发送验证码失败:', error)
  }
}

// 验证邮箱验证码
const verifyEmailCode = async () => {
  if (!emailFormRef.value) return
  
  try {
    await emailFormRef.value.validate()
    verifyingEmail.value = true
    
    // 这里需要调用验证邮箱的API
    // await verifyEmailCode({ email: profileForm.value.email, code: emailForm.value.code })
    
    ElMessage.success('邮箱验证成功')
    showEmailDialog.value = false
    profileForm.value.is_email_verified = true
    
  } catch (error) {
    console.error('邮箱验证失败:', error)
    ElMessage.error('邮箱验证失败')
  } finally {
    verifyingEmail.value = false
  }
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 工具函数
const getRoleDisplayName = (role: string) => {
  const nameMap: Record<string, string> = {
    'super_admin': '超级管理员',
    'department_manager': '部门部长',
    'store_operator': '店铺运营',
    'staff': '普通员工'
  }
  return nameMap[role] || role
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'active': 'success',
    'approved': 'success',
    'pending': 'warning',
    'inactive': 'danger',
    'rejected': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusDisplayName = (status: string) => {
  const nameMap: Record<string, string> = {
    'active': '激活',
    'approved': '已通过',
    'pending': '待审批',
    'inactive': '禁用',
    'rejected': '拒绝'
  }
  return nameMap[status] || status
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '-'
    return date.toLocaleString('zh-CN')
  } catch (error) {
    return '-'
  }
}

// 加载未读消息数量
const loadUnreadMessageCount = async () => {
  try {
    loadingUnreadCount.value = true
    const response = await fetch('/api/messages/unread_count/', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    if (response.ok) {
      const data = await response.json()
      unreadMessageCount.value = data.unread_count || 0
      unreadCountError.value = false
    }
  } catch (error) {
    console.error('获取未读消息数量失败:', error)
    unreadMessageCount.value = 0
    unreadCountError.value = true
    // 只在开发环境下显示错误信息
    if (import.meta.env.DEV) {
      ElMessage.warning('获取未读消息数量失败')
    }
  } finally {
    loadingUnreadCount.value = false
  }
}

// 刷新未读消息数量
const refreshUnreadCount = async () => {
  await loadUnreadMessageCount()
  if (!unreadCountError.value) {
    ElMessage.success('未读消息数量已更新')
  }
}

// 跳转到消息页面
const goToMessages = () => {
  router.push('/messages')
}

// 跳转到聊天室页面
const goToChatRooms = () => {
  router.push('/chat-rooms')
}
</script>

<style scoped>
.profile-view {
  max-width: 100%;
}

.page-header {
  margin-bottom: var(--spacing-xl);
  text-align: center;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin-top: var(--spacing-sm);
}

.profile-card,
.password-card,
.security-card {
  margin-bottom: var(--spacing-xl);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.card-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.field-hint {
  margin-top: var(--spacing-xs);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.password-info {
  color: var(--text-secondary);
  line-height: 1.6;
}

.security-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
}

.security-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.security-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.security-icon {
  font-size: 24px;
  color: var(--primary-color);
}

.security-details h4 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-primary);
}

.security-details p {
  margin: 0;
  color: var(--text-secondary);
}

.email-verification {
  text-align: center;
}

.email-verification p {
  margin-bottom: var(--spacing-md);
  color: var(--text-secondary);
}

.verification-actions {
  margin-top: var(--spacing-lg);
}

.unread-badge {
  margin-left: var(--spacing-xs);
}

.no-unread {
  color: var(--text-secondary);
  font-style: italic;
}

.error-text {
  color: var(--danger-color);
  font-style: italic;
}

.retry-btn {
  margin-left: var(--spacing-xs);
  color: var(--primary-color);
}

.loading-text {
  color: var(--text-secondary);
  font-style: italic;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.loading-icon {
  color: var(--primary-color);
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .security-item {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
  
  .security-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>
