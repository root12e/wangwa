<template>
  <div class="item" @click="handleClick">
    <div class="icon">
      <span class="icon-text">{{ icon }}</span>
    </div>
    <div class="details">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  description: string
}

defineProps<Props>()

const emit = defineEmits<{
  click: []
}>()

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.item {
  margin-top: 2rem;
  display: flex;
  position: relative;
  cursor: pointer;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.3s ease;
  background: var(--color-background);
}

.item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--color-primary);
}

.icon {
  display: flex;
  place-items: center;
  place-content: center;
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: var(--color-primary-light);
  margin-right: 1rem;
  flex-shrink: 0;
}

.icon-text {
  font-size: 2rem;
}

.details {
  flex: 1;
}

h3 {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-heading);
}

p {
  color: var(--color-text);
  line-height: 1.6;
  margin: 0;
}

@media (min-width: 1024px) {
  .item {
    margin-top: 0;
    padding: 1.5rem;
  }

  .icon {
    width: 60px;
    height: 60px;
    margin-right: 1rem;
  }
}
</style>
