<template>
  <div class="redis-status-monitor">
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Monitor /></el-icon>
          <span>Redis缓存状态监控</span>
          <el-tag 
            :type="overallStatusType" 
            size="small"
            class="status-tag"
          >
            {{ overallStatusText }}
          </el-tag>
        </div>
      </template>
      
      <div class="status-content">
        <!-- 整体状态概览 -->
        <div class="overview-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="metric-item">
                <div class="metric-value">{{ cacheStats.totalModels }}</div>
                <div class="metric-label">总模型数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-item">
                <div class="metric-value">{{ cacheStats.cachedModels }}</div>
                <div class="metric-label">已缓存</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-item">
                <div class="metric-value">{{ cacheStats.syncProgress }}%</div>
                <div class="metric-label">同步进度</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-item">
                <div class="metric-value">{{ cacheStats.avgResponseTime }}ms</div>
                <div class="metric-label">平均响应</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 模型状态详情 -->
        <div class="models-section">
          <h4>模型缓存状态</h4>
          <el-table :data="modelStatusList" size="small" stripe>
            <el-table-column prop="model" label="模型名称" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getStatusType(scope.row.status)" 
                  size="small"
                >
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cacheSize" label="缓存大小" width="100" />
            <el-table-column prop="lastSync" label="最后同步" width="150" />
            <el-table-column prop="ttl" label="TTL" width="80" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="handleSyncModel(scope.row.model)"
                  :loading="syncingModels.includes(scope.row.model)"
                  :disabled="scope.row.status === 'syncing'"
                >
                  同步
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 性能指标 -->
        <div class="performance-section">
          <h4>性能指标</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="performance-chart">
                <div class="chart-title">缓存命中率</div>
                <el-progress 
                  :percentage="performanceMetrics.cacheHitRate" 
                  :color="getProgressColor"
                  :stroke-width="12"
                />
                <div class="chart-value">{{ performanceMetrics.cacheHitRate }}%</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="performance-chart">
                <div class="chart-title">平均响应时间</div>
                <div class="chart-value">{{ performanceMetrics.avgResponseTime }}ms</div>
                <div class="chart-trend">
                  <el-icon :class="getTrendIcon(performanceMetrics.responseTimeTrend)">
                    {{ getTrendIcon(performanceMetrics.responseTimeTrend) }}
                  </el-icon>
                  {{ performanceMetrics.responseTimeTrend === 'up' ? '上升' : '下降' }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="performance-chart">
                <div class="chart-title">内存使用率</div>
                <el-progress 
                  :percentage="performanceMetrics.memoryUsage" 
                  :color="getMemoryColor"
                  :stroke-width="12"
                />
                <div class="chart-value">{{ performanceMetrics.memoryUsage }}%</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 操作按钮 -->
        <div class="actions-section">
          <el-button 
            type="primary" 
            @click="handleSyncAll"
            :loading="syncingAll"
            :disabled="hasSyncingModels"
          >
            <el-icon><Refresh /></el-icon>
            同步所有模型
          </el-button>
          <el-button 
            type="warning" 
            @click="handleClearAllCache"
            :disabled="hasSyncingModels"
          >
            <el-icon><Delete /></el-icon>
            清除所有缓存
          </el-button>
          <el-button 
            type="info" 
            @click="handleRefreshStats"
            :loading="refreshing"
          >
            <el-icon><Refresh /></el-icon>
            刷新统计
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor, Refresh, Delete, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { etsySyncManagementAPI } from '@/api/etsy'

// 定义组件属性
interface Props {
  autoRefresh?: boolean
  refreshInterval?: number
}

// 定义事件
interface Emits {
  (e: 'sync-model', model: string): void
  (e: 'sync-all'): void
  (e: 'clear-all-cache'): void
  (e: 'stats-updated', stats: any): void
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 30000 // 30秒
})

const emit = defineEmits<Emits>()

// 响应式数据
const cacheStats = ref({
  totalModels: 0,
  cachedModels: 0,
  syncProgress: 0,
  avgResponseTime: 0
})

const modelStatusList = ref<any[]>([])
const performanceMetrics = ref({
  cacheHitRate: 0,
  avgResponseTime: 0,
  responseTimeTrend: 'stable',
  memoryUsage: 0
})

const syncingModels = ref<string[]>([])
const syncingAll = ref(false)
const refreshing = ref(false)
let refreshTimer: NodeJS.Timeout | null = null

// 计算属性
const overallStatusType = computed(() => {
  const progress = cacheStats.value.syncProgress
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return 'danger'
})

const overallStatusText = computed(() => {
  const progress = cacheStats.value.syncProgress
  if (progress === 100) return '完全同步'
  if (progress >= 80) return '基本同步'
  return '同步异常'
})

const hasSyncingModels = computed(() => {
  return modelStatusList.value.some(model => model.status === 'syncing')
})

// 方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'cached': 'success',
    'syncing': 'warning',
    'failed': 'danger',
    'expired': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'cached': '已缓存',
    'syncing': '同步中',
    'failed': '同步失败',
    'expired': '已过期'
  }
  return statusMap[status] || '未知'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#f56c6c'
  if (percentage < 80) return '#e6a23c'
  return '#67c23a'
}

const getMemoryColor = (percentage: number) => {
  if (percentage > 80) return '#f56c6c'
  if (percentage > 60) return '#e6a23c'
  return '#67c23a'
}

const getTrendIcon = (trend: string) => {
  if (trend === 'up') return 'ArrowUp'
  if (trend === 'down') return 'ArrowDown'
  return ''
}

const fetchCacheStats = async () => {
  try {
    const [statsResponse, redisStatsResponse] = await Promise.all([
      etsySyncManagementAPI.getCacheInfo(),
      etsySyncManagementAPI.getRedisStats()
    ])
    
    // 更新缓存统计
    cacheStats.value = {
      totalModels: statsResponse.data.total_models || 0,
      cachedModels: statsResponse.data.cached_models || 0,
      syncProgress: statsResponse.data.sync_progress || 0,
      avgResponseTime: statsResponse.data.avg_response_time || 0
    }
    
    // 更新模型状态列表
    modelStatusList.value = statsResponse.data.model_status || []
    
    // 更新性能指标
    performanceMetrics.value = {
      cacheHitRate: redisStatsResponse.data.cache_hit_rate || 0,
      avgResponseTime: redisStatsResponse.data.avg_response_time || 0,
      responseTimeTrend: redisStatsResponse.data.response_time_trend || 'stable',
      memoryUsage: redisStatsResponse.data.memory_usage || 0
    }
    
    emit('stats-updated', {
      cacheStats: cacheStats.value,
      modelStatus: modelStatusList.value,
      performance: performanceMetrics.value
    })
  } catch (error) {
    console.error('获取缓存统计失败:', error)
    ElMessage.error('获取缓存统计失败')
  }
}

const handleSyncModel = async (model: string) => {
  try {
    syncingModels.value.push(model)
    await etsySyncManagementAPI.triggerRedisSync(model)
    ElMessage.success(`模型 ${model} 同步已启动`)
    emit('sync-model', model)
    
    // 等待一段时间后刷新状态
    setTimeout(() => {
      fetchCacheStats()
    }, 2000)
  } catch (error) {
    console.error('同步模型失败:', error)
    ElMessage.error('同步模型失败')
  } finally {
    const index = syncingModels.value.indexOf(model)
    if (index > -1) {
      syncingModels.value.splice(index, 1)
    }
  }
}

const handleSyncAll = async () => {
  try {
    syncingAll.value = true
    await etsySyncManagementAPI.syncAll()
    ElMessage.success('所有模型同步已启动')
    emit('sync-all')
    
    // 等待一段时间后刷新状态
    setTimeout(() => {
      fetchCacheStats()
    }, 3000)
  } catch (error) {
    console.error('同步所有模型失败:', error)
    ElMessage.error('同步所有模型失败')
  } finally {
    syncingAll.value = false
  }
}

const handleClearAllCache = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有缓存吗？这将重新从数据库加载所有数据，可能需要较长时间。',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await etsySyncManagementAPI.clearAllCache()
    ElMessage.success('所有缓存已清除')
    emit('clear-all-cache')
    
    // 刷新状态
    fetchCacheStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除所有缓存失败:', error)
      ElMessage.error('清除所有缓存失败')
    }
  }
}

const handleRefreshStats = async () => {
  refreshing.value = true
  try {
    await fetchCacheStats()
    ElMessage.success('统计信息已刷新')
  } finally {
    refreshing.value = false
  }
}

const startAutoRefresh = () => {
  if (props.autoRefresh) {
    refreshTimer = setInterval(fetchCacheStats, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  fetchCacheStats()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.redis-status-monitor {
  margin-bottom: 20px;
}

.status-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: #409eff;
}

.status-tag {
  margin-left: auto;
}

.status-content {
  padding: 0;
}

.overview-section {
  margin-bottom: 24px;
}

.metric-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 14px;
  color: #666;
}

.models-section {
  margin-bottom: 24px;
}

.models-section h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.performance-section {
  margin-bottom: 24px;
}

.performance-section h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.performance-chart {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chart-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.chart-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.chart-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.chart-trend .el-icon {
  font-size: 14px;
}

.chart-trend .el-icon.ArrowUp {
  color: #f56c6c;
}

.chart-trend .el-icon.ArrowDown {
  color: #67c23a;
}

.actions-section {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-section .el-col {
    margin-bottom: 16px;
  }
  
  .performance-section .el-col {
    margin-bottom: 16px;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .actions-section .el-button {
    width: 100%;
  }
}
</style>
