<template>
  <div class="settings-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>系统设置</h1>
      <p class="page-description">管理系统配置、权限和安全设置</p>
    </div>

    <!-- 设置分类导航 -->
    <div class="settings-nav card fade-in-up" style="animation-delay: 0.1s">
      <el-tabs v-model="activeTab" type="border-card" class="settings-tabs">
        <el-tab-pane label="基本设置" name="basic">
          <div class="tab-content">
            <h3>基本配置</h3>
            <el-form :model="basicSettings" label-width="120px" class="settings-form">
              <el-form-item label="系统名称">
                <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称" />
              </el-form-item>
              <el-form-item label="系统版本">
                <el-input v-model="basicSettings.version" disabled />
              </el-form-item>
              <el-form-item label="管理员邮箱">
                <el-input v-model="basicSettings.adminEmail" placeholder="请输入管理员邮箱" />
              </el-form-item>
              <el-form-item label="系统描述">
                <el-input 
                  v-model="basicSettings.description" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入系统描述"
                />
              </el-form-item>
              <el-form-item label="时区设置">
                <el-select v-model="basicSettings.timezone" placeholder="请选择时区">
                  <el-option label="UTC+8 (北京时间)" value="UTC+8" />
                  <el-option label="UTC+0 (格林威治时间)" value="UTC+0" />
                  <el-option label="UTC-5 (纽约时间)" value="UTC-5" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
                <el-button @click="resetBasicSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="安全设置" name="security">
          <div class="tab-content">
            <h3>安全配置</h3>
            <el-form :model="securitySettings" label-width="120px" class="settings-form">
              <el-form-item label="密码策略">
                <el-checkbox-group v-model="securitySettings.passwordPolicy">
                  <el-checkbox label="minLength">最小长度8位</el-checkbox>
                  <el-checkbox label="uppercase">必须包含大写字母</el-checkbox>
                  <el-checkbox label="lowercase">必须包含小写字母</el-checkbox>
                  <el-checkbox label="numbers">必须包含数字</el-checkbox>
                  <el-checkbox label="special">必须包含特殊字符</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="登录失败锁定">
                <el-input-number 
                  v-model="securitySettings.maxLoginAttempts" 
                  :min="3" 
                  :max="10"
                  placeholder="最大登录失败次数"
                />
              </el-form-item>
              <el-form-item label="会话超时(分钟)">
                <el-input-number 
                  v-model="securitySettings.sessionTimeout" 
                  :min="15" 
                  :max="480"
                  placeholder="会话超时时间"
                />
              </el-form-item>
              <el-form-item label="双因素认证">
                <el-switch v-model="securitySettings.twoFactorAuth" />
                <span class="setting-hint">启用双因素认证提高账户安全性</span>
              </el-form-item>
              <el-form-item label="IP白名单">
                <el-input 
                  v-model="securitySettings.ipWhitelist" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请输入允许访问的IP地址，每行一个"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
                <el-button @click="resetSecuritySettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="通知设置" name="notification">
          <div class="tab-content">
            <h3>通知配置</h3>
            <el-form :model="notificationSettings" label-width="120px" class="settings-form">
              <el-form-item label="邮件通知">
                <el-switch v-model="notificationSettings.emailNotification" />
              </el-form-item>
              <el-form-item label="SMTP服务器" v-if="notificationSettings.emailNotification">
                <el-input v-model="notificationSettings.smtpServer" placeholder="请输入SMTP服务器地址" />
              </el-form-item>
              <el-form-item label="SMTP端口" v-if="notificationSettings.emailNotification">
                <el-input-number v-model="notificationSettings.smtpPort" :min="1" :max="65535" />
              </el-form-item>
              <el-form-item label="系统通知">
                <el-checkbox-group v-model="notificationSettings.systemNotifications">
                  <el-checkbox label="login">登录通知</el-checkbox>
                  <el-checkbox label="password">密码修改通知</el-checkbox>
                  <el-checkbox label="inventory">库存预警通知</el-checkbox>
                  <el-checkbox label="sales">销售异常通知</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="通知频率">
                <el-radio-group v-model="notificationSettings.frequency">
                  <el-radio label="immediate">立即通知</el-radio>
                  <el-radio label="hourly">每小时汇总</el-radio>
                  <el-radio label="daily">每日汇总</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
                <el-button @click="resetNotificationSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="备份设置" name="backup">
          <div class="tab-content">
            <h3>备份配置</h3>
            <div class="backup-info">
              <el-alert
                title="备份说明"
                type="info"
                :closable="false"
                show-icon
              >
                <p>定期备份可以保护您的数据安全，建议至少每周进行一次完整备份。</p>
              </el-alert>
            </div>
            
            <el-form :model="backupSettings" label-width="120px" class="settings-form">
              <el-form-item label="自动备份">
                <el-switch v-model="backupSettings.autoBackup" />
              </el-form-item>
              <el-form-item label="备份频率" v-if="backupSettings.autoBackup">
                <el-select v-model="backupSettings.frequency" placeholder="请选择备份频率">
                  <el-option label="每日" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
              <el-form-item label="保留备份数">
                <el-input-number 
                  v-model="backupSettings.retentionCount" 
                  :min="1" 
                  :max="30"
                  placeholder="保留的备份文件数量"
                />
              </el-form-item>
              <el-form-item label="备份内容">
                <el-checkbox-group v-model="backupSettings.backupContent">
                  <el-checkbox label="database">数据库</el-checkbox>
                  <el-checkbox label="files">文件</el-checkbox>
                  <el-checkbox label="config">配置文件</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBackupSettings">保存设置</el-button>
                <el-button type="success" @click="createBackup">立即备份</el-button>
                <el-button @click="resetBackupSettings">重置</el-button>
              </el-form-item>
            </el-form>
            
            <!-- 备份历史 -->
            <div class="backup-history">
              <h4>备份历史</h4>
              <el-table :data="backupHistory" style="width: 100%" size="small">
                <el-table-column prop="date" label="备份时间" width="180" />
                <el-table-column prop="type" label="备份类型" width="100" />
                <el-table-column prop="size" label="文件大小" width="100" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                      {{ scope.row.status === 'success' ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button size="small" type="primary" text>下载</el-button>
                    <el-button size="small" type="danger" text>删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const activeTab = ref('basic')

// 基本设置
const basicSettings = ref({
  systemName: 'WWKC库存管理系统',
  version: 'v1.0.0',
  adminEmail: 'admin@wwkc.com',
  description: '专业的库存管理系统，支持多店铺、多角色管理',
  timezone: 'UTC+8'
})

// 安全设置
const securitySettings = ref({
  passwordPolicy: ['minLength', 'uppercase', 'numbers'],
  maxLoginAttempts: 5,
  sessionTimeout: 120,
  twoFactorAuth: false,
  ipWhitelist: ''
})

// 通知设置
const notificationSettings = ref({
  emailNotification: true,
  smtpServer: 'smtp.qq.com',
  smtpPort: 587,
  systemNotifications: ['login', 'inventory'],
  frequency: 'immediate'
})

// 备份设置
const backupSettings = ref({
  autoBackup: true,
  frequency: 'weekly',
  retentionCount: 7,
  backupContent: ['database', 'config']
})

// 备份历史
const backupHistory = ref([
  {
    date: '2024-01-15 02:00:00',
    type: '自动备份',
    size: '256MB',
    status: 'success'
  },
  {
    date: '2024-01-08 02:00:00',
    type: '自动备份',
    size: '248MB',
    status: 'success'
  },
  {
    date: '2024-01-01 02:00:00',
    type: '自动备份',
    size: '242MB',
    status: 'success'
  }
])

// 保存设置方法
const saveBasicSettings = () => {
  ElMessage.success('基本设置保存成功')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功')
}

const saveNotificationSettings = () => {
  ElMessage.success('通知设置保存成功')
}

const saveBackupSettings = () => {
  ElMessage.success('备份设置保存成功')
}

// 重置设置方法
const resetBasicSettings = () => {
  ElMessage.info('基本设置已重置')
}

const resetSecuritySettings = () => {
  ElMessage.info('安全设置已重置')
}

const resetNotificationSettings = () => {
  ElMessage.info('通知设置已重置')
}

const resetBackupSettings = () => {
  ElMessage.info('备份设置已重置')
}

// 创建备份
const createBackup = () => {
  ElMessage.success('备份任务已启动，请稍后查看备份历史')
}
</script>

<style scoped>
.settings-view {
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

.settings-nav {
  padding: 0;
  overflow: hidden;
}

.settings-tabs {
  border: none;
}

.settings-tabs :deep(.el-tabs__header) {
  background: var(--primary-ultra-light);
  margin: 0;
}

.settings-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 var(--spacing-lg);
}

.settings-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
  font-weight: 500;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
  font-weight: 600;
}

.tab-content {
  padding: var(--spacing-xl);
}

.tab-content h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--primary-color);
  font-size: 1.5rem;
}

.settings-form {
  max-width: 600px;
}

.setting-hint {
  margin-left: var(--spacing-sm);
  color: var(--text-secondary);
  font-size: 12px;
}

.backup-info {
  margin-bottom: var(--spacing-lg);
}

.backup-history {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.backup-history h4 {
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-form {
    max-width: 100%;
  }
  
  .tab-content {
    padding: var(--spacing-md);
  }
  
  .settings-tabs :deep(.el-tabs__nav-wrap) {
    padding: 0 var(--spacing-md);
  }
}
</style>
