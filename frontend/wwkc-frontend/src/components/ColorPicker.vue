<template>
  <div class="color-picker">
    <div class="color-preview" @click="showPicker = !showPicker">
      <div 
        class="color-swatch" 
        :style="{ backgroundColor: modelValue }"
        :title="modelValue"
      ></div>
      <span class="color-value">{{ modelValue }}</span>
      <el-icon class="picker-icon">
        <ArrowDown v-if="!showPicker" />
        <ArrowUp v-else />
      </el-icon>
    </div>
    
    <div v-if="showPicker" class="color-panel">
      <div class="color-inputs">
        <div class="input-group">
          <label>HEX</label>
          <el-input 
            v-model="hexValue" 
            @input="updateFromHex"
            placeholder="#000000"
            size="small"
          />
        </div>
        
        <div class="input-group">
          <label>RGB</label>
          <div class="rgb-inputs">
            <el-input-number 
              v-model="rgbValues.r" 
              :min="0" 
              :max="255" 
              size="small"
              @change="updateFromRgb"
            />
            <el-input-number 
              v-model="rgbValues.g" 
              :min="0" 
              :max="255" 
              size="small"
              @change="updateFromRgb"
            />
            <el-input-number 
              v-model="rgbValues.b" 
              :min="0" 
              :max="255" 
              size="small"
              @change="updateFromRgb"
            />
          </div>
        </div>
        
        <div class="input-group">
          <label>HSL</label>
          <div class="hsl-inputs">
            <el-input-number 
              v-model="hslValues.h" 
              :min="0" 
              :max="360" 
              size="small"
              @change="updateFromHsl"
            />
            <el-input-number 
              v-model="hslValues.s" 
              :min="0" 
              :max="100" 
              size="small"
              @change="updateFromHsl"
            />
            <el-input-number 
              v-model="hslValues.l" 
              :min="0" 
              :max="100" 
              size="small"
              @change="updateFromHsl"
            />
          </div>
        </div>
      </div>
      
      <div class="color-sliders">
        <div class="slider-group">
          <label>色相 (H)</label>
          <el-slider 
            v-model="hslValues.h" 
            :min="0" 
            :max="360" 
            @change="updateFromHsl"
            :show-tooltip="false"
          />
        </div>
        
        <div class="slider-group">
          <label>饱和度 (S)</label>
          <el-slider 
            v-model="hslValues.s" 
            :min="0" 
            :max="100" 
            @change="updateFromHsl"
            :show-tooltip="false"
          />
        </div>
        
        <div class="slider-group">
          <label>亮度 (L)</label>
          <el-slider 
            v-model="hslValues.l" 
            :min="0" 
            :max="100" 
            @change="updateFromHsl"
            :show-tooltip="false"
          />
        </div>
      </div>
      
      <div class="preset-colors">
        <h4>预设颜色</h4>
        <div class="color-grid">
          <div 
            v-for="color in presetColors" 
            :key="color"
            class="preset-color"
            :style="{ backgroundColor: color }"
            @click="selectPresetColor(color)"
            :title="color"
          ></div>
        </div>
      </div>
      
      <div class="color-actions">
        <el-button size="small" @click="resetColor">重置</el-button>
        <el-button size="small" type="primary" @click="confirmColor">确定</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'

interface Props {
  modelValue: string
  showAlpha?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  showAlpha: false
})

const emit = defineEmits<Emits>()

// 响应式状态
const showPicker = ref(false)
const hexValue = ref('')
const rgbValues = ref({ r: 0, g: 0, b: 0 })
const hslValues = ref({ h: 0, s: 0, l: 0 })

// 预设颜色
const presetColors = [
  '#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00',
  '#00FF80', '#00FFFF', '#0080FF', '#0000FF', '#8000FF',
  '#FF00FF', '#FF0080', '#FF4040', '#FF8040', '#FFFF40',
  '#80FF40', '#40FF40', '#40FF80', '#40FFFF', '#4080FF',
  '#4040FF', '#8040FF', '#FF40FF', '#FF4080', '#FFFFFF',
  '#E0E0E0', '#C0C0C0', '#808080', '#404040', '#000000'
]

// HEX转RGB
const hexToRgb = (hex: string) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null
}

// RGB转HEX
const rgbToHex = (r: number, g: number, b: number) => {
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }).join('')
}

// RGB转HSL
const rgbToHsl = (r: number, g: number, b: number) => {
  r /= 255
  g /= 255
  b /= 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h = 0
  let s = 0
  const l = (max + min) / 2

  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0)
        break
      case g:
        h = (b - r) / d + 2
        break
      case b:
        h = (r - g) / d + 4
        break
    }
    h /= 6
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  }
}

// HSL转RGB
const hslToRgb = (h: number, s: number, l: number) => {
  h /= 360
  s /= 100
  l /= 100

  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1
    if (t > 1) t -= 1
    if (t < 1/6) return p + (q - p) * 6 * t
    if (t < 1/2) return q
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
    return p
  }

  let r, g, b

  if (s === 0) {
    r = g = b = l
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }

  return {
    r: Math.round(r * 255),
    g: Math.round(g * 255),
    b: Math.round(b * 255)
  }
}

// 更新颜色值
const updateColorValues = (color: string) => {
  try {
    // 解析HEX颜色
    if (color.startsWith('#')) {
      hexValue.value = color
      const rgb = hexToRgb(color)
      if (rgb) {
        rgbValues.value = rgb
        hslValues.value = rgbToHsl(rgb.r, rgb.g, rgb.b)
      }
    }
  } catch (error) {
    console.error('解析颜色失败:', error)
  }
}

// 计算属性
const currentColor = computed(() => props.modelValue)

// 监听颜色变化
watch(currentColor, (newColor) => {
  if (newColor) {
    updateColorValues(newColor)
  }
}, { immediate: true })

// 从HEX更新
const updateFromHex = () => {
  if (hexValue.value && /^#[0-9A-F]{6}$/i.test(hexValue.value)) {
    const rgb = hexToRgb(hexValue.value)
    if (rgb) {
      rgbValues.value = rgb
      hslValues.value = rgbToHsl(rgb.r, rgb.g, rgb.b)
      emit('update:modelValue', hexValue.value)
    }
  }
}

// 从RGB更新
const updateFromRgb = () => {
  const hex = rgbToHex(rgbValues.value.r, rgbValues.value.g, rgbValues.value.b)
  hexValue.value = hex
  hslValues.value = rgbToHsl(rgbValues.value.r, rgbValues.value.g, rgbValues.value.b)
  emit('update:modelValue', hex)
}

// 从HSL更新
const updateFromHsl = () => {
  const rgb = hslToRgb(hslValues.value.h, hslValues.value.s, hslValues.value.l)
  rgbValues.value = rgb
  const hex = rgbToHex(rgb.r, rgb.g, rgb.b)
  hexValue.value = hex
  emit('update:modelValue', hex)
}

// 选择预设颜色
const selectPresetColor = (color: string) => {
  emit('update:modelValue', color)
  showPicker.value = false
}

// 重置颜色
const resetColor = () => {
  updateColorValues(props.modelValue)
}

// 确认颜色
const confirmColor = () => {
  showPicker.value = false
}

// 点击外部关闭
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.color-picker')) {
    showPicker.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.color-picker {
  position: relative;
  display: inline-block;
}

.color-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: pointer;
  background: var(--el-bg-color);
  transition: all 0.2s;
}

.color-preview:hover {
  border-color: var(--el-color-primary);
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 2px solid var(--el-border-color);
  cursor: pointer;
}

.color-value {
  font-family: monospace;
  font-size: 14px;
  color: var(--el-text-color-primary);
  min-width: 70px;
}

.picker-icon {
  color: var(--el-text-color-secondary);
  transition: transform 0.2s;
}

.color-panel {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1000;
  width: 320px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  margin-top: 4px;
}

.color-inputs {
  margin-bottom: 16px;
}

.input-group {
  margin-bottom: 12px;
}

.input-group label {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.rgb-inputs,
.hsl-inputs {
  display: flex;
  gap: 8px;
}

.rgb-inputs .el-input-number,
.hsl-inputs .el-input-number {
  flex: 1;
}

.color-sliders {
  margin-bottom: 16px;
}

.slider-group {
  margin-bottom: 12px;
}

.slider-group label {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.preset-colors h4 {
  font-size: 14px;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
  margin-bottom: 16px;
}

.preset-color {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 2px solid var(--el-border-color);
  cursor: pointer;
  transition: transform 0.2s;
}

.preset-color:hover {
  transform: scale(1.1);
  border-color: var(--el-color-primary);
}

.color-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .color-panel {
    width: 280px;
    left: -20px;
  }
  
  .color-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}
</style>
