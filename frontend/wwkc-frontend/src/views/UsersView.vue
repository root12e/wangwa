<template>
  <div class="users-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>用户管理</h1>
      <p class="page-description">管理系统用户、角色和权限</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">156</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><Crown /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">3</div>
          <div class="stat-label">超级管理员</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">8</div>
          <div class="stat-label">部门部长</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">24</div>
          <div class="stat-label">店铺运营</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card fade-in-up" style="animation-delay: 0.5s">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="roleFilter" placeholder="选择角色" clearable>
          <el-option label="超级管理员" value="super_admin" />
          <el-option label="部门部长" value="department_manager" />
          <el-option label="店铺运营" value="store_operator" />
          <el-option label="普通员工" value="staff" />
        </el-select>
        
        <el-select v-model="departmentFilter" placeholder="选择部门" clearable>
          <el-option label="技术部" value="tech" />
          <el-option label="销售部" value="sales" />
          <el-option label="运营部" value="operations" />
          <el-option label="财务部" value="finance" />
        </el-select>
      </div>
      
      <div class="action-right">
        <el-button type="primary" class="btn-primary">
          <el-icon><Plus /></el-icon>
          添加用户
        </el-button>
        <el-button class="btn-secondary">
          <el-icon><Setting /></el-icon>
          角色管理
        </el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-table card fade-in-up" style="animation-delay: 0.6s">
      <el-table :data="usersData" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.avatar" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="getRoleTagType(scope.row.role)">
              {{ getRoleDisplayName(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="store" label="所属店铺" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" width="180" />
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
            <el-button 
              size="small" 
              :type="scope.row.status === 'active' ? 'warning' : 'success'" 
              text
            >
              <el-icon><Lock v-if="scope.row.status === 'active'" /><Unlock v-else /></el-icon>
              {{ scope.row.status === 'active' ? '禁用' : '激活' }}
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
import { ref } from 'vue'

// 响应式数据
const searchQuery = ref('')
const roleFilter = ref('')
const departmentFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(156)

// 模拟用户数据
const usersData = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@wwkc.com',
    phone: '13800000000',
    role: 'super_admin',
    department: '技术部',
    store: '总部',
    status: 'active',
    lastLogin: '2024-01-15 15:30:00',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 2,
    username: 'manager001',
    email: 'manager001@wwkc.com',
    phone: '13800000001',
    role: 'department_manager',
    department: '销售部',
    store: '北京店',
    status: 'active',
    lastLogin: '2024-01-15 14:20:00',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 3,
    username: 'operator001',
    email: 'operator001@wwkc.com',
    phone: '13800000002',
    role: 'store_operator',
    department: '运营部',
    store: '上海店',
    status: 'active',
    lastLogin: '2024-01-15 13:15:00',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  },
  {
    id: 4,
    username: 'staff001',
    email: 'staff001@wwkc.com',
    phone: '13800000003',
    role: 'staff',
    department: '财务部',
    store: '总部',
    status: 'active',
    lastLogin: '2024-01-15 12:45:00',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
  }
])

// 计算属性
const getRoleTagType = (role: string) => {
  const typeMap: Record<string, string> = {
    'super_admin': 'danger',
    'department_manager': 'warning',
    'store_operator': 'primary',
    'staff': 'info'
  }
  return typeMap[role] || 'info'
}

const getRoleDisplayName = (role: string) => {
  const nameMap: Record<string, string> = {
    'super_admin': '超级管理员',
    'department_manager': '部门部长',
    'store_operator': '店铺运营',
    'staff': '普通员工'
  }
  return nameMap[role] || role
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
.users-view {
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

.users-table {
  padding: 0;
  overflow: hidden;
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
