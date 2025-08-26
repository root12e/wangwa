<template>
  <div class="invitation-container">
    <el-card class="invitation-card">
      <template #header>
        <div class="card-header">
          <h2>管理员邀请</h2>
        </div>
      </template>
      
      <div v-if="invitation" class="invitation-details">
        <el-descriptions title="邀请详情" :column="1" border>
          <el-descriptions-item label="邀请人">
            {{ invitation.inviter }}
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            {{ invitation.role_display }}
          </el-descriptions-item>
          <el-descriptions-item label="部门" v-if="invitation.department">
            {{ invitation.department }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(invitation.status)">
              {{ invitation.status_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(invitation.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="过期时间">
            {{ formatDate(invitation.expires_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="invitation.status === 'pending'" class="action-buttons">
          <el-button 
            type="success" 
            @click="acceptInvitation" 
            :loading="loading"
            size="large"
          >
            接受邀请
          </el-button>
          <el-button 
            type="danger" 
            @click="rejectInvitation" 
            :loading="loading"
            size="large"
          >
            拒绝邀请
          </el-button>
        </div>
        
        <el-alert
          v-if="invitation.status === 'expired'"
          title="邀请已过期"
          type="warning"
          show-icon
          :closable="false"
          style="margin-top: 20px"
        />
        
        <el-alert
          v-if="invitation.status === 'accepted'"
          title="邀请已接受"
          type="success"
          show-icon
          :closable="false"
          style="margin-top: 20px"
        />
        
        <el-alert
          v-if="invitation.status === 'rejected'"
          title="邀请已拒绝"
          type="info"
          show-icon
          :closable="false"
          style="margin-top: 20px"
        />
      </div>
      
      <div v-else-if="error" class="error-message">
        <el-alert
          :title="error"
          type="error"
          show-icon
          :closable="false"
        />
        <el-button 
          type="primary" 
          @click="$router.push('/login')"
          style="margin-top: 20px"
        >
          返回登录页
        </el-button>
      </div>
      
      <div v-else class="loading">
        <el-skeleton :rows="6" animated />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInvitationByToken, acceptInvitation, rejectInvitation } from '@/api/adminInvitation'

const route = useRoute()
const router = useRouter()
const invitation = ref(null)
const loading = ref(false)
const error = ref('')

const getStatusType = (status: string) => {
  const statusMap = {
    'pending': 'warning',
    'accepted': 'success',
    'rejected': 'info',
    'expired': 'danger'
  }
  return statusMap[status] || 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadInvitation = async () => {
  try {
    const token = route.params.token as string
    const response = await getInvitationByToken(token)
    invitation.value = response.data
  } catch (error: any) {
    this.error = error.response?.data?.error || '邀请链接无效或已过期'
  }
}

const handleAcceptInvitation = async () => {
  try {
    loading.value = true
    await acceptInvitation(invitation.value.id)
    invitation.value.status = 'accepted'
    ElMessage.success('邀请已接受')
    
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '接受邀请失败')
  } finally {
    loading.value = false
  }
}

const handleRejectInvitation = async () => {
  try {
    loading.value = true
    await rejectInvitation(invitation.value.id)
    invitation.value.status = 'rejected'
    ElMessage.success('邀请已拒绝')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '拒绝邀请失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadInvitation()
})
</script>

<style scoped>
.invitation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.invitation-card {
  width: 100%;
  max-width: 600px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.invitation-details {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

.error-message {
  text-align: center;
  padding: 40px 20px;
}

.loading {
  padding: 40px 20px;
}

.el-descriptions {
  margin-top: 20px;
}

.el-tag {
  font-size: 14px;
}
</style>
