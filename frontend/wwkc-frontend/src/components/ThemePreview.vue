<template>
  <div class="theme-preview">
    <div class="preview-header">
      <h4>{{ theme.name }}</h4>
      <p>{{ theme.description }}</p>
    </div>
    
    <div class="preview-content">
      <!-- 颜色预览 -->
      <div class="color-preview">
        <div class="color-item">
          <div class="color-label">主色调</div>
          <div class="color-swatch" :style="{ backgroundColor: theme.colors.primary }"></div>
          <span class="color-code">{{ theme.colors.primary }}</span>
        </div>
        
        <div class="color-item">
          <div class="color-label">强调色</div>
          <div class="color-swatch" :style="{ backgroundColor: theme.colors.accent }"></div>
          <span class="color-code">{{ theme.colors.accent }}</span>
        </div>
        
        <div class="color-item">
          <div class="color-label">背景色</div>
          <div class="color-swatch" :style="{ backgroundColor: theme.colors.background }"></div>
          <span class="color-code">{{ theme.colors.background }}</span>
        </div>
        
        <div class="color-item">
          <div class="color-label">文字色</div>
          <div class="color-swatch" :style="{ backgroundColor: theme.colors.text }"></div>
          <span class="color-code">{{ theme.colors.text }}</span>
        </div>
      </div>
      
      <!-- 界面预览 -->
      <div class="ui-preview" :style="{ 
        '--preview-primary': theme.colors.primary,
        '--preview-accent': theme.colors.accent,
        '--preview-background': theme.colors.background,
        '--preview-text': theme.colors.text,
        '--preview-border': theme.colors.border
      }">
        <div class="preview-navbar">
          <div class="preview-logo">WWKC</div>
          <div class="preview-menu">
            <span class="preview-menu-item">首页</span>
            <span class="preview-menu-item">库存</span>
            <span class="preview-menu-item">订单</span>
          </div>
        </div>
        
        <div class="preview-sidebar">
          <div class="preview-sidebar-item">仪表盘</div>
          <div class="preview-sidebar-item">库存管理</div>
          <div class="preview-sidebar-item">订单管理</div>
          <div class="preview-sidebar-item">报表</div>
        </div>
        
        <div class="preview-main">
          <div class="preview-card">
            <h3>库存概览</h3>
            <div class="preview-stats">
              <div class="preview-stat">
                <span class="stat-number">1,234</span>
                <span class="stat-label">总商品</span>
              </div>
              <div class="preview-stat">
                <span class="stat-number">567</span>
                <span class="stat-label">库存充足</span>
              </div>
              <div class="preview-stat">
                <span class="stat-number">89</span>
                <span class="stat-label">库存不足</span>
              </div>
            </div>
          </div>
          
          <div class="preview-table">
            <div class="preview-table-header">
              <span>商品名称</span>
              <span>SKU</span>
              <span>库存</span>
              <span>状态</span>
            </div>
            <div class="preview-table-row">
              <span>示例商品1</span>
              <span>SKU001</span>
              <span>100</span>
              <span class="status-normal">正常</span>
            </div>
            <div class="preview-table-row">
              <span>示例商品2</span>
              <span>SKU002</span>
              <span>5</span>
              <span class="status-warning">不足</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="preview-actions">
      <el-button 
        type="primary" 
        size="small" 
        @click="$emit('apply', theme.id)"
        :disabled="isCurrentTheme"
      >
        {{ isCurrentTheme ? '当前主题' : '应用主题' }}
      </el-button>
      
      <el-button 
        size="small" 
        @click="$emit('customize', theme)"
        v-if="!isCurrentTheme"
      >
        自定义
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PresetTheme } from '@/types/settings'

interface Props {
  theme: PresetTheme
  isCurrentTheme?: boolean
}

interface Emits {
  (e: 'apply', themeId: string): void
  (e: 'customize', theme: PresetTheme): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.theme-preview {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-bg-color);
  transition: all 0.3s ease;
}

.theme-preview:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.preview-header {
  padding: 16px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9) 0%, var(--el-color-primary-light-8) 100%);
  border-bottom: 1px solid var(--el-border-color);
}

.preview-header h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-header p {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.preview-content {
  padding: 16px;
}

.color-preview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  min-width: 40px;
}

.color-swatch {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid var(--el-border-color);
}

.color-code {
  font-family: monospace;
  font-size: 11px;
  color: var(--el-text-color-secondary);
}

.ui-preview {
  border: 1px solid var(--preview-border);
  border-radius: 6px;
  overflow: hidden;
  background: var(--preview-background);
  color: var(--preview-text);
}

.preview-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--preview-primary);
  color: white;
  font-size: 12px;
}

.preview-logo {
  font-weight: bold;
  font-size: 14px;
}

.preview-menu {
  display: flex;
  gap: 16px;
}

.preview-menu-item {
  cursor: pointer;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.preview-menu-item:hover {
  opacity: 1;
}

.preview-sidebar {
  display: flex;
  flex-direction: column;
  width: 80px;
  background: var(--preview-background);
  border-right: 1px solid var(--preview-border);
}

.preview-sidebar-item {
  padding: 8px 12px;
  font-size: 11px;
  border-bottom: 1px solid var(--preview-border);
  cursor: pointer;
  transition: background-color 0.2s;
}

.preview-sidebar-item:hover {
  background: var(--preview-primary);
  color: white;
}

.preview-main {
  padding: 12px;
}

.preview-card {
  background: white;
  border: 1px solid var(--preview-border);
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 12px;
}

.preview-card h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--preview-text);
}

.preview-stats {
  display: flex;
  gap: 16px;
}

.preview-stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 18px;
  font-weight: bold;
  color: var(--preview-primary);
}

.stat-label {
  font-size: 10px;
  color: var(--preview-text);
  opacity: 0.7;
}

.preview-table {
  border: 1px solid var(--preview-border);
  border-radius: 4px;
  overflow: hidden;
  background: white;
}

.preview-table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 12px;
  background: var(--preview-primary-light-9);
  font-size: 11px;
  font-weight: 500;
  color: var(--preview-text);
}

.preview-table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 6px 12px;
  font-size: 11px;
  border-bottom: 1px solid var(--preview-border);
}

.preview-table-row:last-child {
  border-bottom: none;
}

.status-normal {
  color: var(--preview-accent);
  font-weight: 500;
}

.status-warning {
  color: #E6A23C;
  font-weight: 500;
}

.preview-actions {
  padding: 16px;
  border-top: 1px solid var(--el-border-color);
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .color-preview {
    grid-template-columns: 1fr;
  }
  
  .preview-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .preview-table-header,
  .preview-table-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
