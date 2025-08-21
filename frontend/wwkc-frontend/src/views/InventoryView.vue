<template>
  <div class="inventory-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>库存管理</h1>
      <p class="page-description">管理商品库存、分类和供应商信息</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">1,234</div>
          <div class="stat-label">总商品数</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">89</div>
          <div class="stat-label">库存预警</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">¥45,678</div>
          <div class="stat-label">库存总值</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">12</div>
          <div class="stat-label">供应商</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card fade-in-up" style="animation-delay: 0.5s">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索商品..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="categoryFilter" placeholder="选择分类" clearable>
          <el-option label="电子产品" value="electronics" />
          <el-option label="服装鞋帽" value="clothing" />
          <el-option label="食品饮料" value="food" />
          <el-option label="家居用品" value="home" />
        </el-select>
      </div>
      
      <div class="action-right">
        <el-button type="primary" class="btn-primary">
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>
        <el-button class="btn-secondary">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="inventory-table card fade-in-up" style="animation-delay: 0.6s">
      <el-table :data="inventoryData" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" min-width="200">
          <template #default="scope">
            <div class="product-info">
              <el-avatar :size="40" :src="scope.row.image" />
              <div class="product-details">
                <div class="product-name">{{ scope.row.name }}</div>
                <div class="product-category">{{ scope.row.category }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="scope">
            <el-tag :type="getStockTagType(scope.row.stock)">
              {{ scope.row.stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="lastUpdated" label="最后更新" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" text>
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="success" text>
              <el-icon><View /></el-icon>
              查看
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 响应式数据
const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(100)

// 模拟库存数据
const inventoryData = ref([
  {
    id: 1,
    name: 'iPhone 15 Pro',
    category: '电子产品',
    sku: 'IP15P-001',
    stock: 45,
    price: 8999,
    supplier: '苹果官方',
    lastUpdated: '2024-01-15 14:30:00',
    image: 'https://via.placeholder.com/40x40/4A90E2/FFFFFF?text=IP'
  },
  {
    id: 2,
    name: 'MacBook Air M2',
    category: '电子产品',
    sku: 'MBA-M2-001',
    stock: 12,
    price: 9999,
    supplier: '苹果官方',
    lastUpdated: '2024-01-15 10:20:00',
    image: 'https://via.placeholder.com/40x40/7BB3F0/FFFFFF?text=MB'
  },
  {
    id: 3,
    name: 'Nike Air Max',
    category: '服装鞋帽',
    sku: 'NA-001',
    stock: 89,
    price: 1299,
    supplier: '耐克官方',
    lastUpdated: '2024-01-14 16:45:00',
    image: 'https://via.placeholder.com/40x40/52C41A/FFFFFF?text=NK'
  },
  {
    id: 4,
    name: '星巴克咖啡豆',
    category: '食品饮料',
    sku: 'SB-001',
    stock: 5,
    price: 199,
    supplier: '星巴克',
    lastUpdated: '2024-01-15 09:15:00',
    image: 'https://via.placeholder.com/40x40/FAAD14/FFFFFF?text=SB'
  }
])

// 计算属性
const getStockTagType = (stock: number) => {
  if (stock <= 10) return 'danger'
  if (stock <= 50) return 'warning'
  return 'success'
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
.inventory-view {
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

.inventory-table {
  padding: 0;
  overflow: hidden;
}

.product-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.product-details {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: 600;
  color: var(--text-primary);
}

.product-category {
  font-size: 12px;
  color: var(--text-secondary);
}

.pagination-wrapper {
  padding: var(--spacing-lg);
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
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
}
</style>
