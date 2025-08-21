<template>
  <div class="loading-page" v-if="show">
    <div class="loading-content">
      <div class="logo-container">
        <div class="logo-icon">
          <el-icon><Box /></el-icon>
        </div>
        <h1 class="system-title">WWKC</h1>
      </div>
      
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ progress }}%</div>
      </div>
      
      <div class="status-text">{{ currentStatus }}</div>
      
      <div class="version-info">v1.0.0</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Box } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  show?: boolean
  duration?: number
}>(), {
  show: true,
  duration: 3000
})

const progress = ref(0)
const currentStatus = ref('正在初始化系统...')
const show = ref(props.show)

const loadingStatuses = [
  '正在初始化系统...',
  '正在加载用户配置...',
  '正在连接数据库...',
  '正在加载界面组件...',
  '正在验证用户权限...',
  '系统启动完成！'
]

let progressTimer: NodeJS.Timeout | null = null
let statusTimer: NodeJS.Timeout | null = null

const startLoading = () => {
  progressTimer = setInterval(() => {
    if (progress.value < 100) {
      progress.value += Math.random() * 15
      if (progress.value > 100) progress.value = 100
    } else {
      if (progressTimer) {
        clearInterval(progressTimer)
        progressTimer = null
      }
    }
  }, 200)
  
  let statusIndex = 0
  statusTimer = setInterval(() => {
    if (statusIndex < loadingStatuses.length - 1) {
      statusIndex++
      currentStatus.value = loadingStatuses[statusIndex]
    } else {
      if (statusTimer) {
        clearInterval(statusTimer)
        statusTimer = null
      }
      setTimeout(() => {
        show.value = false
      }, 1000)
    }
  }, props.duration / loadingStatuses.length)
}

onMounted(() => {
  startLoading()
})

onUnmounted(() => {
  if (progressTimer) clearInterval(progressTimer)
  if (statusTimer) clearInterval(statusTimer)
})

defineExpose({
  show,
  progress,
  currentStatus
})
</script>

<style scoped>
.loading-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, var(--primary-ultra-light) 0%, var(--background-color) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  max-width: 400px;
  padding: var(--spacing-xl);
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.logo-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.system-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.loading-spinner {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto var(--spacing-xl);
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 4px solid transparent;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.spinner-ring:nth-child(2) {
  width: 80%;
  height: 80%;
  top: 10%;
  left: 10%;
  border-top-color: var(--primary-light);
  animation-delay: 0.5s;
}

.spinner-ring:nth-child(3) {
  width: 60%;
  height: 60%;
  top: 20%;
  left: 20%;
  border-top-color: var(--primary-dark);
  animation-delay: 1s;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress-container {
  margin-bottom: var(--spacing-lg);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
}

.progress-text {
  color: var(--primary-color);
  font-weight: 600;
  font-size: 14px;
}

.status-text {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
  margin-bottom: var(--spacing-lg);
  min-height: 24px;
}

.version-info {
  color: var(--text-secondary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .system-title {
    font-size: 2rem;
  }
  
  .logo-icon {
    width: 60px;
    height: 60px;
    font-size: 28px;
  }
  
  .loading-spinner {
    width: 80px;
    height: 80px;
  }
}
</style>
