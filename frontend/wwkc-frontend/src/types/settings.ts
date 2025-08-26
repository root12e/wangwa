// 设置相关类型定义

// 语言设置
export interface LanguageSettings {
  currentLanguage: string
  availableLanguages: LanguageOption[]
}

export interface LanguageOption {
  code: string
  name: string
  nativeName: string
  flag?: string
}

// 主题设置
export interface ThemeSettings {
  currentTheme: 'light' | 'dark' | 'auto'
  primaryColor: string
  accentColor: string
  backgroundColor: string
  textColor: string
  borderColor: string
  customColors: CustomColor[]
}

export interface CustomColor {
  name: string
  value: string
  description: string
}

// 字体设置
export interface FontSettings {
  fontSize: 'small' | 'medium' | 'large' | 'extra-large'
  fontFamily: string
  lineHeight: number
  letterSpacing: number
  fontWeight: 'normal' | 'bold' | 'lighter'
}

// 布局设置
export interface LayoutSettings {
  sidebarCollapsed: boolean
  sidebarWidth: number
  headerHeight: number
  contentPadding: number
  showBreadcrumb: boolean
  showPageTitle: boolean
  compactMode: boolean
}

// 通知设置
export interface NotificationSettings {
  soundEnabled: boolean
  desktopNotifications: boolean
  emailNotifications: boolean
  notificationTypes: string[]
  quietHours: {
    enabled: boolean
    startTime: string
    endTime: string
  }
}

// 性能设置
export interface PerformanceSettings {
  autoRefresh: boolean
  refreshInterval: number
  lazyLoading: boolean
  imageOptimization: boolean
  cacheEnabled: boolean
  cacheExpiration: number
}

// 辅助功能设置
export interface AccessibilitySettings {
  highContrast: boolean
  reduceMotion: boolean
  screenReader: boolean
  keyboardNavigation: boolean
  focusIndicator: boolean
  colorBlindSupport: boolean
}

// 数据设置
export interface DataSettings {
  dataRetention: number
  exportFormat: 'csv' | 'excel' | 'json'
  importValidation: boolean
  backupFrequency: string
  syncEnabled: boolean
  syncInterval: number
}

// 完整设置对象
export interface AppSettings {
  language: LanguageSettings
  theme: ThemeSettings
  font: FontSettings
  layout: LayoutSettings
  notification: NotificationSettings
  performance: PerformanceSettings
  accessibility: AccessibilitySettings
  data: DataSettings
}

// 设置变更事件
export interface SettingsChangeEvent {
  category: keyof AppSettings
  key: string
  oldValue: any
  newValue: any
  timestamp: Date
}

// 预设主题
export interface PresetTheme {
  id: string
  name: string
  description: string
  colors: {
    primary: string
    accent: string
    background: string
    text: string
    border: string
  }
  preview: string
}

// 设置导入导出
export interface SettingsExport {
  version: string
  exportDate: string
  settings: AppSettings
  metadata: {
    appName: string
    appVersion: string
    userAgent: string
  }
}
