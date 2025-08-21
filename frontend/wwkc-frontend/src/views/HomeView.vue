<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const selectedPeriod = ref('month')
const currentDate = ref('')

// 统计数据
const stats = ref({
  totalProducts: 1247,
  totalStores: 28,
  totalUsers: 156,
  monthlyRevenue: '¥128,450'
})

// 库存状态
const inventoryStatus = ref({
  normal: 892,
  low: 234,
  out: 121
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    type: 'add',
    title: '新增商品：iPhone 15 Pro',
    time: '2分钟前',
    userName: '张三',
    userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 2,
    type: 'update',
    title: '更新库存：MacBook Air',
    time: '15分钟前',
    userName: '李四',
    userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 3,
    type: 'delete',
    title: '删除过期商品：旧款耳机',
    time: '1小时前',
    userName: '王五',
    userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 4,
    type: 'info',
    title: '系统维护完成',
    time: '2小时前',
    userName: '系统',
    userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  }
])

// 生命周期
onMounted(() => {
  currentDate.value = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 快速操作
const quickAction = (action: string) => {
  const actionMap: Record<string, string> = {
    addProduct: '添加商品',
    checkInventory: '检查库存',
    generateReport: '生成报表',
    userManagement: '用户管理',
    systemSettings: '系统设置',
    backupData: '数据备份'
  }
  
  ElMessage.success(`正在执行：${actionMap[action]}`)
}
</script>

<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section fade-in-up">
      <div class="welcome-content">
        <h1>欢迎回来，管理员！</h1>
        <p class="welcome-subtitle">今天是 {{ currentDate }}，让我们开始管理您的库存吧</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" size="large" class="btn-primary">
          <el-icon><Plus /></el-icon>
          快速添加商品
        </el-button>
        <el-button size="large" class="btn-secondary">
          <el-icon><DataAnalysis /></el-icon>
          查看报表
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalProducts }}</div>
          <div class="stat-label">总商品数</div>
          <div class="stat-change positive">
            <el-icon><ArrowUp /></el-icon>
            +12% 本月
          </div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalStores }}</div>
          <div class="stat-label">店铺数量</div>
          <div class="stat-change positive">
            <el-icon><ArrowUp /></el-icon>
            +3 新增
          </div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalUsers }}</div>
          <div class="stat-label">用户数量</div>
          <div class="stat-change positive">
            <el-icon><ArrowUp /></el-icon>
            +8 新增
          </div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.monthlyRevenue }}</div>
          <div class="stat-label">本月营收</div>
          <div class="stat-change positive">
            <el-icon><ArrowUp /></el-icon>
            +15% 增长
          </div>
        </div>
      </div>
    </div>

    <!-- 图表和表格区域 -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- 销售趋势图 -->
        <div class="chart-card card fade-in-up" style="animation-delay: 0.5s">
          <div class="chart-header">
            <h3>销售趋势</h3>
            <el-select v-model="selectedPeriod" size="small" style="width: 120px">
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
              <el-option label="本季度" value="quarter" />
            </el-select>
          </div>
          <div class="chart-placeholder">
            <el-icon class="chart-icon"><TrendCharts /></el-icon>
            <p>销售趋势图表</p>
            <small>这里将显示销售数据的可视化图表</small>
          </div>
        </div>

        <!-- 库存状态 -->
        <div class="chart-card card fade-in-up" style="animation-delay: 0.6s">
          <div class="chart-header">
            <h3>库存状态</h3>
            <el-button type="text" size="small">查看详情</el-button>
          </div>
          <div class="inventory-status">
            <div class="status-item">
              <div class="status-dot normal"></div>
              <span>正常库存</span>
              <span class="status-count">{{ inventoryStatus.normal }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot low"></div>
              <span>库存不足</span>
              <span class="status-count">{{ inventoryStatus.low }}</span>
            </div>
            <div class="status-item">
              <div class="status-dot out"></div>
              <span>缺货</span>
              <span class="status-count">{{ inventoryStatus.out }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="recent-activities card fade-in-up" style="animation-delay: 0.7s">
        <div class="activities-header">
          <h3>最近活动</h3>
          <el-button type="text" size="small">查看全部</el-button>
        </div>
        <div class="activities-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon">
              <el-icon v-if="activity.type === 'add'"><Plus /></el-icon>
              <el-icon v-else-if="activity.type === 'update'"><Edit /></el-icon>
              <el-icon v-else-if="activity.type === 'delete'"><Delete /></el-icon>
              <el-icon v-else><InfoFilled /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
            <div class="activity-user">
              <el-avatar :size="24" :src="activity.userAvatar" />
              <span>{{ activity.userName }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions card fade-in-up" style="animation-delay: 0.8s">
      <h3>快速操作</h3>
      <div class="actions-grid">
        <el-button class="action-btn" @click="quickAction('addProduct')">
          <el-icon><Plus /></el-icon>
          <span>添加商品</span>
        </el-button>
        <el-button class="action-btn" @click="quickAction('checkInventory')">
          <el-icon><Search /></el-icon>
          <span>检查库存</span>
        </el-button>
        <el-button class="action-btn" @click="quickAction('generateReport')">
          <el-icon><Document /></el-icon>
          <span>生成报表</span>
        </el-button>
        <el-button class="action-btn" @click="quickAction('userManagement')">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-button>
        <el-button class="action-btn" @click="quickAction('systemSettings')">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-button>
        <el-button class="action-btn" @click="quickAction('backupData')">
          <el-icon><Download /></el-icon>
          <span>数据备份</span>
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
  border-radius: var(--border-radius-large);
  color: white;
  box-shadow: var(--shadow-medium);
}

.welcome-content h1 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: 2.5rem;
  color: white;
  -webkit-background-clip: unset;
  -webkit-text-fill-color: unset;
}

.welcome-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: var(--spacing-md);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-heavy);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
}

.stat-change {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-change.positive {
  color: var(--success-color);
}

.stat-change.negative {
  color: var(--error-color);
}

/* 图表区域 */
.charts-section {
  margin-bottom: var(--spacing-xl);
}

.chart-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.chart-card {
  min-height: 300px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
  text-align: center;
}

.chart-icon {
  font-size: 3rem;
  color: var(--primary-light);
  margin-bottom: var(--spacing-md);
}

/* 库存状态 */
.inventory-status {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-medium);
  background: var(--background-color);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.normal {
  background: var(--success-color);
}

.status-dot.low {
  background: var(--warning-color);
}

.status-dot.out {
  background: var(--error-color);
}

.status-count {
  margin-left: auto;
  font-weight: 600;
  color: var(--text-primary);
}

/* 最近活动 */
.activities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-medium);
  background: var(--background-color);
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: var(--primary-ultra-light);
  transform: translateX(4px);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-ultra-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.activity-time {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.activity-user {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* 快速操作 */
.quick-actions {
  margin-bottom: var(--spacing-xl);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  height: 100px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-medium);
  background: white;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: var(--primary-color);
  background: var(--primary-ultra-light);
  transform: translateY(-4px);
  box-shadow: var(--shadow-medium);
}

.action-btn .el-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-lg);
  }
  
  .welcome-content h1 {
    font-size: 2rem;
  }
  
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
