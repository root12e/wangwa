<script setup lang="ts">
import { useRouter } from 'vue-router'
import WelcomeItem from './WelcomeItem.vue'

const router = useRouter()

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="welcome">
    <div class="welcome-header">
      <h1>欢迎使用库存管理系统</h1>
      <p>选择您要进行的操作</p>
    </div>
    
    <div class="welcome-grid">
      <WelcomeItem
        icon="🏪"
        title="店铺管理"
        description="管理店铺信息、员工分配和运营数据"
        @click="navigateTo('/stores')"
      />
      
      <WelcomeItem
        icon="📦"
        title="库存管理"
        description="查看和管理商品库存、出入库记录"
        @click="navigateTo('/inventory')"
      />
      
      <WelcomeItem
        icon="👥"
        title="用户管理"
        description="管理系统用户、权限和角色分配"
        @click="navigateTo('/users')"
      />
      
      <WelcomeItem
        icon="🏢"
        title="部门管理"
        description="管理组织架构和部门设置"
        @click="navigateTo('/departments')"
      />
      
      <WelcomeItem
        icon="💬"
        title="消息系统"
        description="聊天室、库存预警和通知管理"
        @click="navigateTo('/messages')"
      />
      
      <WelcomeItem
        icon="⚙️"
        title="系统设置"
        description="系统配置、主题设置和个性化"
        @click="navigateTo('/settings')"
      />
    </div>
  </div>
</template>

<style scoped>
.welcome {
  padding: 2rem;
  text-align: center;
}

.welcome-header {
  margin-bottom: 3rem;
}

.welcome-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.welcome-header p {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.welcome-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .welcome-grid {
    grid-template-columns: 1fr;
  }
}
</style>
