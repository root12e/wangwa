<template>
  <div class="settings-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>系统设置</h1>
      <p class="page-description">管理系统配置、外观、语言和个性化设置</p>
    </div>

    <!-- 设置分类导航 -->
    <div class="settings-nav card fade-in-up" style="animation-delay: 0.1s">
      <el-tabs v-model="activeTab" type="border-card" class="settings-tabs">
        
        <!-- 外观设置 -->
        <el-tab-pane label="外观设置" name="appearance">
          <div class="tab-content">
            <h3>外观配置</h3>
            
            <!-- 主题模式 -->
            <div class="setting-section">
              <h4>主题模式</h4>
              <div class="theme-mode-selector">
                <el-radio-group v-model="settings.theme.currentTheme" @change="updateSetting('theme', 'currentTheme', $event)">
                  <el-radio-button label="light">
                    <el-icon><Sunny /></el-icon>
                    浅色模式
                  </el-radio-button>
                  <el-radio-button label="dark">
                    <el-icon><Moon /></el-icon>
                    深色模式
                  </el-radio-button>
                  <el-radio-button label="auto">
                    <el-icon><Monitor /></el-icon>
                    跟随系统
                  </el-radio-button>
                </el-radio-group>
              </div>
            </div>

            <!-- 预设主题 -->
            <div class="setting-section">
              <h4>预设主题</h4>
              <div class="preset-themes">
                <ThemePreview
                  v-for="theme in settingsStore.presetThemes"
                  :key="theme.id"
                  :theme="theme"
                  :is-current-theme="theme.id === 'default'"
                  @apply="applyPresetTheme"
                  @customize="customizeTheme"
                />
              </div>
            </div>

            <!-- 自定义颜色 -->
            <div class="setting-section">
              <h4>自定义颜色</h4>
              <el-form :model="settings.theme" label-width="120px" class="color-form">
                <el-form-item label="主色调">
                  <ColorPicker v-model="settings.theme.primaryColor" @update:modelValue="updateSetting('theme', 'primaryColor', $event)" />
                </el-form-item>
                <el-form-item label="强调色">
                  <ColorPicker v-model="settings.theme.accentColor" @update:modelValue="updateSetting('theme', 'accentColor', $event)" />
                </el-form-item>
                <el-form-item label="背景色">
                  <ColorPicker v-model="settings.theme.backgroundColor" @update:modelValue="updateSetting('theme', 'backgroundColor', $event)" />
                </el-form-item>
                <el-form-item label="文字色">
                  <ColorPicker v-model="settings.theme.textColor" @update:modelValue="updateSetting('theme', 'textColor', $event)" />
                </el-form-item>
                <el-form-item label="边框色">
                  <ColorPicker v-model="settings.theme.borderColor" @update:modelValue="updateSetting('theme', 'borderColor', $event)" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 字体设置 -->
        <el-tab-pane label="字体设置" name="font">
          <div class="tab-content">
            <h3>字体配置</h3>
            
            <!-- 字体大小 -->
            <div class="setting-section">
              <h4>字体大小</h4>
              <div class="font-size-selector">
                <el-radio-group v-model="settings.font.fontSize" @change="updateSetting('font', 'fontSize', $event)">
                  <el-radio-button label="small">小 (14px)</el-radio-button>
                  <el-radio-button label="medium">中 (16px)</el-radio-button>
                  <el-radio-button label="large">大 (18px)</el-radio-button>
                  <el-radio-button label="extra-large">特大 (20px)</el-radio-button>
                </el-radio-group>
              </div>
            </div>

            <!-- 字体族 -->
            <div class="setting-section">
              <h4>字体族</h4>
              <el-select v-model="settings.font.fontFamily" @change="updateSetting('font', 'fontFamily', $event)" placeholder="选择字体">
                <el-option label="Inter (推荐)" value="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" />
                <el-option label="微软雅黑" value="'Microsoft YaHei', sans-serif" />
                <el-option label="苹方" value="'PingFang SC', 'Helvetica Neue', Arial, sans-serif" />
                <el-option label="思源黑体" value="'Source Han Sans CN', 'Noto Sans CJK SC', sans-serif" />
                <el-option label="Arial" value="Arial, sans-serif" />
              </el-select>
            </div>

            <!-- 行高 -->
            <div class="setting-section">
              <h4>行高</h4>
              <el-slider
                v-model="settings.font.lineHeight"
                :min="1.2"
                :max="2.0"
                :step="0.1"
                :show-tooltip="true"
                @change="updateSetting('font', 'lineHeight', $event)"
              />
              <span class="setting-value">{{ settings.font.lineHeight }}</span>
            </div>

            <!-- 字间距 -->
            <div class="setting-section">
              <h4>字间距</h4>
              <el-slider
                v-model="settings.font.letterSpacing"
                :min="-2"
                :max="5"
                :step="0.5"
                :show-tooltip="true"
                @change="updateSetting('font', 'letterSpacing', $event)"
              />
              <span class="setting-value">{{ settings.font.letterSpacing }}px</span>
            </div>

            <!-- 字重 -->
            <div class="setting-section">
              <h4>字重</h4>
              <el-radio-group v-model="settings.font.fontWeight" @change="updateSetting('font', 'fontWeight', $event)">
                <el-radio-button label="lighter">细体</el-radio-button>
                <el-radio-button label="normal">正常</el-radio-button>
                <el-radio-button label="bold">粗体</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </el-tab-pane>

        <!-- 语言设置 -->
        <el-tab-pane label="语言设置" name="language">
          <div class="tab-content">
            <h3>语言配置</h3>
            
            <!-- 当前语言 -->
            <div class="setting-section">
              <h4>当前语言</h4>
              <div class="language-selector">
                <el-select v-model="settings.language.currentLanguage" @change="changeLanguage" placeholder="选择语言">
                  <el-option
                    v-for="lang in settings.language.availableLanguages"
                    :key="lang.code"
                    :label="`${lang.flag} ${lang.name} (${lang.nativeName})`"
                    :value="lang.code"
                  />
                </el-select>
              </div>
            </div>

            <!-- 语言预览 -->
            <div class="setting-section">
              <h4>语言预览</h4>
              <div class="language-preview">
                <div class="preview-item">
                  <span class="preview-label">系统名称:</span>
                  <span class="preview-text">{{ getLanguagePreview('systemName') }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">库存管理:</span>
                  <span class="preview-text">{{ getLanguagePreview('inventory') }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">订单管理:</span>
                  <span class="preview-text">{{ getLanguagePreview('order') }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 布局设置 -->
        <el-tab-pane label="布局设置" name="layout">
          <div class="tab-content">
            <h3>布局配置</h3>
            
            <!-- 侧边栏 -->
            <div class="setting-section">
              <h4>侧边栏设置</h4>
              <el-form :model="settings.layout" label-width="120px">
                <el-form-item label="侧边栏宽度">
                  <el-slider
                    v-model="settings.layout.sidebarWidth"
                    :min="200"
                    :max="300"
                    :step="10"
                    @change="updateSetting('layout', 'sidebarWidth', $event)"
                  />
                  <span class="setting-value">{{ settings.layout.sidebarWidth }}px</span>
                </el-form-item>
                <el-form-item label="默认折叠">
                  <el-switch v-model="settings.layout.sidebarCollapsed" @change="updateSetting('layout', 'sidebarCollapsed', $event)" />
                </el-form-item>
              </el-form>
            </div>

            <!-- 内容区域 -->
            <div class="setting-section">
              <h4>内容区域</h4>
              <el-form :model="settings.layout" label-width="120px">
                <el-form-item label="内容内边距">
                  <el-slider
                    v-model="settings.layout.contentPadding"
                    :min="16"
                    :max="48"
                    :step="4"
                    @change="updateSetting('layout', 'contentPadding', $event)"
                  />
                  <span class="setting-value">{{ settings.layout.contentPadding }}px</span>
                </el-form-item>
                <el-form-item label="显示面包屑">
                  <el-switch v-model="settings.layout.showBreadcrumb" @change="updateSetting('layout', 'showBreadcrumb', $event)" />
                </el-form-item>
                <el-form-item label="显示页面标题">
                  <el-switch v-model="settings.layout.showPageTitle" @change="updateSetting('layout', 'showPageTitle', $event)" />
                </el-form-item>
                <el-form-item label="紧凑模式">
                  <el-switch v-model="settings.layout.compactMode" @change="updateSetting('layout', 'compactMode', $event)" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <div class="tab-content">
            <h3>通知配置</h3>
            
            <el-form :model="settings.notification" label-width="120px" class="settings-form">
              <el-form-item label="声音提醒">
                <el-switch v-model="settings.notification.soundEnabled" @change="updateSetting('notification', 'soundEnabled', $event)" />
              </el-form-item>
              <el-form-item label="桌面通知">
                <el-switch v-model="settings.notification.desktopNotifications" @change="updateSetting('notification', 'desktopNotifications', $event)" />
              </el-form-item>
              <el-form-item label="邮件通知">
                <el-switch v-model="settings.notification.emailNotifications" @change="updateSetting('notification', 'emailNotifications', $event)" />
              </el-form-item>
              <el-form-item label="通知类型">
                <el-checkbox-group v-model="settings.notification.notificationTypes" @change="updateSetting('notification', 'notificationTypes', $event)">
                  <el-checkbox label="system">系统通知</el-checkbox>
                  <el-checkbox label="inventory">库存预警</el-checkbox>
                  <el-checkbox label="order">订单状态</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="免打扰时间">
                <el-switch v-model="settings.notification.quietHours.enabled" @change="updateSetting('notification', 'quietHours', { ...settings.notification.quietHours, enabled: $event })" />
                <div v-if="settings.notification.quietHours.enabled" class="quiet-hours">
                  <el-time-picker
                    v-model="quietStartTime"
                    format="HH:mm"
                    placeholder="开始时间"
                    @change="updateQuietHours"
                  />
                  <span class="time-separator">至</span>
                  <el-time-picker
                    v-model="quietEndTime"
                    format="HH:mm"
                    placeholder="结束时间"
                    @change="updateQuietHours"
                  />
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 性能设置 -->
        <el-tab-pane label="性能设置" name="performance">
          <div class="tab-content">
            <h3>性能配置</h3>
            
            <el-form :model="settings.performance" label-width="120px" class="settings-form">
              <el-form-item label="自动刷新">
                <el-switch v-model="settings.performance.autoRefresh" @change="updateSetting('performance', 'autoRefresh', $event)" />
              </el-form-item>
              <el-form-item label="刷新间隔" v-if="settings.performance.autoRefresh">
                <el-input-number
                  v-model="settings.performance.refreshInterval"
                  :min="10"
                  :max="300"
                  @change="updateSetting('performance', 'refreshInterval', $event)"
                />
                <span class="setting-hint">秒</span>
              </el-form-item>
              <el-form-item label="懒加载">
                <el-switch v-model="settings.performance.lazyLoading" @change="updateSetting('performance', 'lazyLoading', $event)" />
              </el-form-item>
              <el-form-item label="图片优化">
                <el-switch v-model="settings.performance.imageOptimization" @change="updateSetting('performance', 'imageOptimization', $event)" />
              </el-form-item>
              <el-form-item label="启用缓存">
                <el-switch v-model="settings.performance.cacheEnabled" @change="updateSetting('performance', 'cacheEnabled', $event)" />
              </el-form-item>
              <el-form-item label="缓存过期时间" v-if="settings.performance.cacheEnabled">
                <el-input-number
                  v-model="settings.performance.cacheExpiration"
                  :min="300"
                  :max="86400"
                  @change="updateSetting('performance', 'cacheExpiration', $event)"
                />
                <span class="setting-hint">秒</span>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 辅助功能 -->
        <el-tab-pane label="辅助功能" name="accessibility">
          <div class="tab-content">
            <h3>辅助功能配置</h3>
            
            <el-form :model="settings.accessibility" label-width="120px" class="settings-form">
              <el-form-item label="高对比度">
                <el-switch v-model="settings.accessibility.highContrast" @change="updateSetting('accessibility', 'highContrast', $event)" />
              </el-form-item>
              <el-form-item label="减少动画">
                <el-switch v-model="settings.accessibility.reduceMotion" @change="updateSetting('accessibility', 'reduceMotion', $event)" />
              </el-form-item>
              <el-form-item label="屏幕阅读器">
                <el-switch v-model="settings.accessibility.screenReader" @change="updateSetting('accessibility', 'screenReader', $event)" />
              </el-form-item>
              <el-form-item label="键盘导航">
                <el-switch v-model="settings.accessibility.keyboardNavigation" @change="updateSetting('accessibility', 'keyboardNavigation', $event)" />
              </el-form-item>
              <el-form-item label="焦点指示器">
                <el-switch v-model="settings.accessibility.focusIndicator" @change="updateSetting('accessibility', 'focusIndicator', $event)" />
              </el-form-item>
              <el-form-item label="色盲支持">
                <el-switch v-model="settings.accessibility.colorBlindSupport" @change="updateSetting('accessibility', 'colorBlindSupport', $event)" />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 数据设置 -->
        <el-tab-pane label="数据设置" name="data">
          <div class="tab-content">
            <h3>数据配置</h3>
            
            <el-form :model="settings.data" label-width="120px" class="settings-form">
              <el-form-item label="数据保留天数">
                <el-input-number
                  v-model="settings.data.dataRetention"
                  :min="30"
                  :max="1095"
                  @change="updateSetting('data', 'dataRetention', $event)"
                />
                <span class="setting-hint">天</span>
              </el-form-item>
              <el-form-item label="导出格式">
                <el-select v-model="settings.data.exportFormat" @change="updateSetting('data', 'exportFormat', $event)">
                  <el-option label="Excel (.xlsx)" value="excel" />
                  <el-option label="CSV (.csv)" value="csv" />
                  <el-option label="JSON (.json)" value="json" />
                </el-select>
              </el-form-item>
              <el-form-item label="导入验证">
                <el-switch v-model="settings.data.importValidation" @change="updateSetting('data', 'importValidation', $event)" />
              </el-form-item>
              <el-form-item label="备份频率">
                <el-select v-model="settings.data.backupFrequency" @change="updateSetting('data', 'backupFrequency', $event)">
                  <el-option label="每日" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
              <el-form-item label="数据同步">
                <el-switch v-model="settings.data.syncEnabled" @change="updateSetting('data', 'syncEnabled', $event)" />
              </el-form-item>
              <el-form-item label="同步间隔" v-if="settings.data.syncEnabled">
                <el-input-number
                  v-model="settings.data.syncInterval"
                  :min="5"
                  :max="1440"
                  @change="updateSetting('data', 'syncInterval', $event)"
                />
                <span class="setting-hint">分钟</span>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 基本设置 -->
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

        <!-- 安全设置 -->
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

        <!-- 备份设置 -->
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

    <!-- 全局操作 -->
    <div class="global-actions card fade-in-up" style="animation-delay: 0.2s">
      <h3>全局操作</h3>
      <div class="action-buttons">
        <el-button type="primary" @click="exportAllSettings">
          <el-icon><Download /></el-icon>
          导出所有设置
        </el-button>
        <el-button @click="importSettings">
          <el-icon><Upload /></el-icon>
          导入设置
        </el-button>
        <el-button @click="resetAllSettings" type="warning">
          <el-icon><Refresh /></el-icon>
          重置所有设置
        </el-button>
        <input
          ref="fileInput"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleFileImport"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Sunny, 
  Moon, 
  Monitor, 
  Download, 
  Upload, 
  Refresh 
} from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import ColorPicker from '@/components/ColorPicker.vue'
import ThemePreview from '@/components/ThemePreview.vue'
import type { PresetTheme } from '@/types/settings'

// 设置store
const settingsStore = useSettingsStore()

// 响应式数据
const activeTab = ref('appearance')
const fileInput = ref<HTMLInputElement>()

// 从store获取设置
const settings = computed(() => settingsStore.settings)

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

// 免打扰时间
const quietStartTime = ref('22:00')
const quietEndTime = ref('08:00')

// 初始化
onMounted(() => {
  settingsStore.initializeSettings()
})

// 更新设置
const updateSetting = (category: string, key: string, value: any) => {
  settingsStore.updateSetting(category as any, key as any, value)
}

// 应用预设主题
const applyPresetTheme = (themeId: string) => {
  settingsStore.applyPresetTheme(themeId)
  ElMessage.success('主题应用成功')
}

// 自定义主题
const customizeTheme = (theme: PresetTheme) => {
  // 将预设主题的颜色应用到当前设置
  settingsStore.updateSetting('theme', 'primaryColor', theme.colors.primary)
  settingsStore.updateSetting('theme', 'accentColor', theme.colors.accent)
  settingsStore.updateSetting('theme', 'backgroundColor', theme.colors.background)
  settingsStore.updateSetting('theme', 'textColor', theme.colors.text)
  settingsStore.updateSetting('theme', 'borderColor', theme.colors.border)
  ElMessage.success('主题自定义成功')
}

// 切换语言
const changeLanguage = (languageCode: string) => {
  settingsStore.changeLanguage(languageCode)
  ElMessage.success('语言切换成功')
}

// 更新免打扰时间
const updateQuietHours = () => {
  settingsStore.updateSetting('notification', 'quietHours', {
    ...settings.value.notification.quietHours,
    startTime: quietStartTime.value,
    endTime: quietEndTime.value
  })
}

// 语言预览
const getLanguagePreview = (key: string) => {
  const languageMap = {
    'zh-CN': {
      systemName: 'WWKC库存管理系统',
      inventory: '库存管理',
      order: '订单管理'
    },
    'en-US': {
      systemName: 'WWKC Inventory Management System',
      inventory: 'Inventory Management',
      order: 'Order Management'
    },
    'ja-JP': {
      systemName: 'WWKC在庫管理システム',
      inventory: '在庫管理',
      order: '注文管理'
    },
    'ko-KR': {
      systemName: 'WWKC 재고 관리 시스템',
      inventory: '재고 관리',
      order: '주문 관리'
    }
  }
  
  const currentLang = settings.value.language.currentLanguage
  return languageMap[currentLang as keyof typeof languageMap]?.[key as keyof typeof languageMap[keyof typeof languageMap]] || key
}

// 导出所有设置
const exportAllSettings = () => {
  const exportData = settingsStore.exportSettings()
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `wwkc-settings-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success('设置导出成功')
}

// 导入设置
const importSettings = () => {
  fileInput.value?.click()
}

// 处理文件导入
const handleFileImport = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const importData = JSON.parse(e.target?.result as string)
        if (settingsStore.importSettings(importData)) {
          ElMessage.success('设置导入成功')
        } else {
          ElMessage.error('设置导入失败，文件格式不正确')
        }
      } catch (error) {
        ElMessage.error('设置导入失败，文件格式不正确')
      }
    }
    reader.readAsText(file)
    target.value = '' // 清空文件选择
  }
}

// 重置所有设置
const resetAllSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置吗？此操作不可撤销。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    settingsStore.resetSettings()
    ElMessage.success('所有设置已重置')
  } catch {
    // 用户取消
  }
}

// 保存设置方法
const saveBasicSettings = () => {
  ElMessage.success('基本设置保存成功')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功')
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

/* 设置区域样式 */
.setting-section {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--el-bg-color-page);
}

.setting-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--el-text-color-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.setting-value {
  margin-left: var(--spacing-sm);
  color: var(--el-text-color-secondary);
  font-size: 14px;
  font-weight: 500;
}

/* 主题模式选择器 */
.theme-mode-selector {
  margin-bottom: var(--spacing-md);
}

.theme-mode-selector .el-radio-button {
  margin-right: var(--spacing-sm);
}

.theme-mode-selector .el-icon {
  margin-right: 4px;
}

/* 预设主题 */
.preset-themes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

/* 颜色表单 */
.color-form {
  max-width: 100%;
}

.color-form .el-form-item {
  margin-bottom: var(--spacing-md);
}

/* 字体大小选择器 */
.font-size-selector {
  margin-bottom: var(--spacing-md);
}

.font-size-selector .el-radio-button {
  margin-right: var(--spacing-sm);
}

/* 语言选择器 */
.language-selector {
  margin-bottom: var(--spacing-md);
}

.language-preview {
  background: var(--el-bg-color-page);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: var(--spacing-md);
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-color);
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-label {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.preview-text {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

/* 免打扰时间 */
.quiet-hours {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.time-separator {
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

/* 全局操作 */
.global-actions {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-xl);
  text-align: center;
}

.global-actions h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--primary-color);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 120px;
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
  
  .preset-themes {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .el-button {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .setting-section {
    padding: var(--spacing-md);
  }
  
  .theme-mode-selector .el-radio-button {
    display: block;
    margin-right: 0;
    margin-bottom: var(--spacing-sm);
  }
  
  .font-size-selector .el-radio-button {
    display: block;
    margin-right: 0;
    margin-bottom: var(--spacing-sm);
  }
}
</style>
