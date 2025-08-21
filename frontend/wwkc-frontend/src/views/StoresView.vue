<template>
  <div class="stores-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>店铺管理</h1>
      <p class="page-description">管理店铺信息、业绩和运营数据</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">24</div>
          <div class="stat-label">总店铺数</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">¥89,456</div>
          <div class="stat-label">今日销售额</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">156</div>
          <div class="stat-label">店铺员工</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><Location /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">8</div>
          <div class="stat-label">覆盖城市</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card fade-in-up" style="animation-delay: 0.5s">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索店铺..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="cityFilter" placeholder="选择城市" clearable>
          <el-option label="北京" value="beijing" />
          <el-option label="上海" value="shanghai" />
          <el-option label="广州" value="guangzhou" />
          <el-option label="深圳" value="shenzhen" />
        </el-select>
        
        <el-select v-model="statusFilter" placeholder="选择状态" clearable>
          <el-option label="营业中" value="open" />
          <el-option label="装修中" value="renovating" />
          <el-option label="暂停营业" value="closed" />
        </el-select>
      </div>
      
      <div class="action-right">
        <el-button type="primary" class="btn-primary">
          <el-icon><Plus /></el-icon>
          添加店铺
        </el-button>
        <el-button class="btn-secondary">
          <el-icon><DataAnalysis /></el-icon>
          业绩分析
        </el-button>
      </div>
    </div>

    <!-- 店铺列表 -->
    <div class="stores-table card fade-in-up" style="animation-delay: 0.6s">
      <el-table :data="storesData" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="店铺名称" min-width="200">
          <template #default="scope">
            <div class="store-info">
              <el-avatar :size="40" :src="scope.row.logo" />
              <div class="store-details">
                <div class="store-name">{{ scope.row.name }}</div>
                <div class="store-code">{{ scope.row.code }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="manager" label="店长" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusDisplayName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="今日销售额" width="120">
          <template #default="scope">
            ¥{{ scope.row.sales.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="employees" label="员工数" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" text>
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="success" text>
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="warning" text>
              <el-icon><DataAnalysis /></el-icon>
              分析
            </el-button>
            <el-button size="small" type="danger" text>
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 地图视图 -->
    <div class="map-section card fade-in-up" style="animation-delay: 0.7s">
      <div class="section-header">
        <h3>店铺分布地图</h3>
        <el-button type="text" class="refresh-btn">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="map-placeholder">
        <el-icon class="map-icon"><Location /></el-icon>
        <p>地图组件将在这里显示店铺分布</p>
        <p class="map-hint">支持缩放、拖拽和点击查看店铺详情</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 响应式数据
const searchQuery = ref('')
const cityFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(24)

// 模拟店铺数据
const storesData = ref([
  {
    id: 1,
    name: '北京朝阳店',
    code: 'BJ-CY-001',
    city: '北京',
    address: '北京市朝阳区建国门外大街1号',
    phone: '010-12345678',
    manager: '张经理',
    status: 'open',
    sales: 12500,
    employees: 12,
    logo: 'https://via.placeholder.com/40x40/4A90E2/FFFFFF?text=BJ'
  },
  {
    id: 2,
    name: '上海浦东店',
    code: 'SH-PD-001',
    city: '上海',
    address: '上海市浦东新区陆家嘴环路1000号',
    phone: '021-87654321',
    manager: '李经理',
    status: 'open',
    sales: 18900,
    employees: 15,
    logo: 'https://via.placeholder.com/40x40/7BB3F0/FFFFFF?text=SH'
  },
  {
    id: 3,
    name: '广州天河店',
    code: 'GZ-TH-001',
    city: '广州',
    address: '广州市天河区天河路385号',
    phone: '020-11223344',
    manager: '王经理',
    status: 'renovating',
    sales: 0,
    employees: 8,
    logo: 'https://via.placeholder.com/40x40/52C41A/FFFFFF?text=GZ'
  },
  {
    id: 4,
    name: '深圳南山店',
    code: 'SZ-NS-001',
    city: '深圳',
    address: '深圳市南山区深南大道9966号',
    phone: '0755-55667788',
    manager: '陈经理',
    status: 'open',
    sales: 15600,
    employees: 10,
    logo: 'https://via.placeholder.com/40x40/FAAD14/FFFFFF?text=SZ'
  }
])

// 计算属性
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'open': 'success',
    'renovating': 'warning',
    'closed': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusDisplayName = (status: string) => {
  const nameMap: Record<string, string> = {
    'open': '营业中',
    'renovating': '装修中',
    'closed': '暂停营业'
  }
  return nameMap[status] || status
}

// 事件处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  // 这里可以重新加载数据
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 这里可以重新加载数据
}
</script>

<style scoped>
.stores-view {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
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
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: var(--spacing-xs);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
}

.action-left {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.search-input {
  width: 300px;
}

.action-right {
  display: flex;
  gap: var(--spacing-md);
}

.stores-table {
  padding: 0;
  overflow: hidden;
  margin-bottom: var(--spacing-xl);
}

.store-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.store-details {
  display: flex;
  flex-direction: column;
}

.store-name {
  font-weight: 600;
  color: var(--text-primary);
}

.store-code {
  font-size: 12px;
  color: var(--text-secondary);
}

.pagination-wrapper {
  padding: var(--spacing-lg);
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
}

.map-section {
  padding: var(--spacing-lg);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.refresh-btn {
  color: var(--primary-color);
}

.map-placeholder {
  height: 400px;
  background: linear-gradient(135deg, var(--primary-ultra-light) 0%, var(--background-color) 100%);
  border: 2px dashed var(--primary-light);
  border-radius: var(--border-radius-large);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.map-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: var(--spacing-md);
}

.map-hint {
  font-size: 14px;
  margin-top: var(--spacing-sm);
  opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .action-left {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .action-right {
    justify-content: center;
  }
  
  .map-placeholder {
    height: 300px;
  }
}
</style>
