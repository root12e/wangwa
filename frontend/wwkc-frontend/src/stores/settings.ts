import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { 
  AppSettings, 
  LanguageSettings, 
  ThemeSettings, 
  FontSettings,
  LayoutSettings,
  NotificationSettings,
  PerformanceSettings,
  AccessibilitySettings,
  DataSettings,
  PresetTheme,
  SettingsExport
} from '@/types/settings'

export const useSettingsStore = defineStore('settings', () => {
  // 默认设置
  const defaultSettings: AppSettings = {
    language: {
      currentLanguage: 'zh-CN',
      availableLanguages: [
        { code: 'zh-CN', name: '简体中文', nativeName: '简体中文', flag: '🇨🇳' },
        { code: 'en-US', name: 'English', nativeName: 'English', flag: '🇺🇸' },
        { code: 'ja-JP', name: '日本語', nativeName: '日本語', flag: '🇯🇵' },
        { code: 'ko-KR', name: '한국어', nativeName: '한국어', flag: '🇰🇷' }
      ]
    },
    theme: {
      currentTheme: 'light',
      primaryColor: '#409EFF',
      accentColor: '#67C23A',
      backgroundColor: '#FFFFFF',
      textColor: '#303133',
      borderColor: '#DCDFE6',
      customColors: []
    },
    font: {
      fontSize: 'medium',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      lineHeight: 1.5,
      letterSpacing: 0,
      fontWeight: 'normal'
    },
    layout: {
      sidebarCollapsed: false,
      sidebarWidth: 240,
      headerHeight: 60,
      contentPadding: 24,
      showBreadcrumb: true,
      showPageTitle: true,
      compactMode: false
    },
    notification: {
      soundEnabled: true,
      desktopNotifications: true,
      emailNotifications: false,
      notificationTypes: ['system', 'inventory', 'order'],
      quietHours: {
        enabled: false,
        startTime: '22:00',
        endTime: '08:00'
      }
    },
    performance: {
      autoRefresh: true,
      refreshInterval: 30,
      lazyLoading: true,
      imageOptimization: true,
      cacheEnabled: true,
      cacheExpiration: 3600
    },
    accessibility: {
      highContrast: false,
      reduceMotion: false,
      screenReader: false,
      keyboardNavigation: true,
      focusIndicator: true,
      colorBlindSupport: false
    },
    data: {
      dataRetention: 365,
      exportFormat: 'excel',
      importValidation: true,
      backupFrequency: 'weekly',
      syncEnabled: false,
      syncInterval: 60
    }
  }

  // 预设主题
  const presetThemes: PresetTheme[] = [
    {
      id: 'default',
      name: '默认主题',
      description: '经典的蓝色主题',
      colors: {
        primary: '#409EFF',
        accent: '#67C23A',
        background: '#FFFFFF',
        text: '#303133',
        border: '#DCDFE6'
      },
      preview: 'linear-gradient(135deg, #409EFF 0%, #67C23A 100%)'
    },
    {
      id: 'ocean',
      name: '海洋主题',
      description: '清新的海洋蓝调',
      colors: {
        primary: '#1E88E5',
        accent: '#00BCD4',
        background: '#F5F9FF',
        text: '#1A237E',
        border: '#BBDEFB'
      },
      preview: 'linear-gradient(135deg, #1E88E5 0%, #00BCD4 100%)'
    },
    {
      id: 'forest',
      name: '森林主题',
      description: '自然的绿色主题',
      colors: {
        primary: '#4CAF50',
        accent: '#8BC34A',
        background: '#F1F8E9',
        text: '#2E7D32',
        border: '#C8E6C9'
      },
      preview: 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)'
    },
    {
      id: 'sunset',
      name: '日落主题',
      description: '温暖的橙红色调',
      colors: {
        primary: '#FF9800',
        accent: '#FF5722',
        background: '#FFF3E0',
        text: '#E65100',
        border: '#FFCC02'
      },
      preview: 'linear-gradient(135deg, #FF9800 0%, #FF5722 100%)'
    },
    {
      id: 'midnight',
      name: '午夜主题',
      description: '深色主题，护眼舒适',
      colors: {
        primary: '#9C27B0',
        accent: '#673AB7',
        background: '#121212',
        text: '#FFFFFF',
        border: '#333333'
      },
      preview: 'linear-gradient(135deg, #9C27B0 0%, #673AB7 100%)'
    }
  ]

  // 响应式状态
  const settings = ref<AppSettings>({ ...defaultSettings })
  const isInitialized = ref(false)

  // 计算属性
  const currentLanguage = computed(() => settings.value.language.currentLanguage)
  const currentTheme = computed(() => settings.value.theme.currentTheme)
  const currentFontSize = computed(() => settings.value.font.fontSize)
  const isDarkMode = computed(() => settings.value.theme.currentTheme === 'dark')

  // 初始化设置
  const initializeSettings = () => {
    try {
      const savedSettings = localStorage.getItem('wwkc-settings')
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings)
        // 合并保存的设置和默认设置
        settings.value = { ...defaultSettings, ...parsed }
      }
      
      // 应用设置到DOM
      applySettings()
      isInitialized.value = true
    } catch (error) {
      console.error('初始化设置失败:', error)
      // 使用默认设置
      settings.value = { ...defaultSettings }
    }
  }

  // 保存设置到本地存储
  const saveSettings = () => {
    try {
      localStorage.setItem('wwkc-settings', JSON.stringify(settings.value))
      applySettings()
    } catch (error) {
      console.error('保存设置失败:', error)
    }
  }

  // 应用设置到DOM
  const applySettings = () => {
    const root = document.documentElement
    
    // 应用主题颜色
    root.style.setProperty('--primary-color', settings.value.theme.primaryColor)
    root.style.setProperty('--accent-color', settings.value.theme.accentColor)
    root.style.setProperty('--background-color', settings.value.theme.backgroundColor)
    root.style.setProperty('--text-color', settings.value.theme.textColor)
    root.style.setProperty('--border-color', settings.value.theme.borderColor)
    
    // 应用字体设置
    const fontSizeMap = {
      'small': '14px',
      'medium': '16px',
      'large': '18px',
      'extra-large': '20px'
    }
    root.style.setProperty('--font-size-base', fontSizeMap[settings.value.font.fontSize])
    root.style.setProperty('--font-family', settings.value.font.fontFamily)
    root.style.setProperty('--line-height', settings.value.font.lineHeight.toString())
    root.style.setProperty('--letter-spacing', `${settings.value.font.letterSpacing}px`)
    root.style.setProperty('--font-weight', settings.value.font.fontWeight)
    
    // 应用布局设置
    root.style.setProperty('--sidebar-width', `${settings.value.layout.sidebarWidth}px`)
    root.style.setProperty('--header-height', `${settings.value.layout.headerHeight}px`)
    root.style.setProperty('--content-padding', `${settings.value.layout.contentPadding}px`)
    
    // 应用主题模式
    if (settings.value.theme.currentTheme === 'dark') {
      document.body.classList.add('dark-theme')
    } else {
      document.body.classList.remove('dark-theme')
    }
    
    // 应用字体大小类
    document.body.className = document.body.className.replace(/font-size-\w+/, '')
    document.body.classList.add(`font-size-${settings.value.font.fontSize}`)
  }

  // 更新设置
  const updateSetting = <K extends keyof AppSettings, SK extends keyof AppSettings[K]>(
    category: K,
    key: SK,
    value: AppSettings[K][SK]
  ) => {
    const oldValue = settings.value[category][key]
    settings.value[category][key] = value
    
    // 立即应用某些设置
    if (category === 'theme' || category === 'font') {
      applySettings()
    }
    
    // 保存设置
    saveSettings()
    
    return { oldValue, newValue: value }
  }

  // 重置设置
  const resetSettings = (category?: keyof AppSettings) => {
    if (category) {
      settings.value[category] = { ...defaultSettings[category] }
    } else {
      settings.value = { ...defaultSettings }
    }
    applySettings()
    saveSettings()
  }

  // 应用预设主题
  const applyPresetTheme = (themeId: string) => {
    const theme = presetThemes.find(t => t.id === themeId)
    if (theme) {
      settings.value.theme.primaryColor = theme.colors.primary
      settings.value.theme.accentColor = theme.colors.accent
      settings.value.theme.backgroundColor = theme.colors.background
      settings.value.theme.textColor = theme.colors.text
      settings.value.theme.borderColor = theme.colors.border
      applySettings()
      saveSettings()
    }
  }

  // 切换主题模式
  const toggleTheme = () => {
    const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto']
    const currentIndex = themes.indexOf(settings.value.theme.currentTheme)
    const nextIndex = (currentIndex + 1) % themes.length
    settings.value.theme.currentTheme = themes[nextIndex]
    applySettings()
    saveSettings()
  }

  // 切换字体大小
  const toggleFontSize = () => {
    const sizes: Array<'small' | 'medium' | 'large' | 'extra-large'> = ['small', 'medium', 'large', 'extra-large']
    const currentIndex = sizes.indexOf(settings.value.font.fontSize)
    const nextIndex = (currentIndex + 1) % sizes.length
    settings.value.font.fontSize = sizes[nextIndex]
    applySettings()
    saveSettings()
  }

  // 切换语言
  const changeLanguage = (languageCode: string) => {
    settings.value.language.currentLanguage = languageCode
    saveSettings()
    // 这里可以触发语言切换事件
    window.dispatchEvent(new CustomEvent('language-changed', { detail: languageCode }))
  }

  // 导出设置
  const exportSettings = (): SettingsExport => {
    return {
      version: '1.0.0',
      exportDate: new Date().toISOString(),
      settings: settings.value,
      metadata: {
        appName: 'WWKC库存管理系统',
        appVersion: '1.0.0',
        userAgent: navigator.userAgent
      }
    }
  }

  // 导入设置
  const importSettings = (importData: SettingsExport) => {
    try {
      if (importData.version && importData.settings) {
        settings.value = { ...defaultSettings, ...importData.settings }
        applySettings()
        saveSettings()
        return true
      }
      return false
    } catch (error) {
      console.error('导入设置失败:', error)
      return false
    }
  }

  // 监听设置变化
  watch(settings, () => {
    if (isInitialized.value) {
      saveSettings()
    }
  }, { deep: true })

  return {
    // 状态
    settings,
    isInitialized,
    presetThemes,
    
    // 计算属性
    currentLanguage,
    currentTheme,
    currentFontSize,
    isDarkMode,
    
    // 方法
    initializeSettings,
    updateSetting,
    resetSettings,
    applyPresetTheme,
    toggleTheme,
    toggleFontSize,
    changeLanguage,
    exportSettings,
    importSettings,
    saveSettings
  }
})
