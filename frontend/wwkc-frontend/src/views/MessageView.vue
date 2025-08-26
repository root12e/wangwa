<template>
  <div class="message-system">
    <h1>消息系统</h1>
    
    <div class="main-content">
      <div class="sidebar">
        <h3>聊天室</h3>
        <div class="chat-rooms">
          <div
            v-for="room in chatRooms"
            :key="room.id"
            :class="['room-item', { active: currentRoom?.id === room.id }]"
            @click="selectRoom(room)"
          >
            {{ room.name }}
          </div>
        </div>
        
        <h3>库存预警</h3>
        <div class="warnings">
          <div
            v-for="warning in warnings"
            :key="warning.id"
            class="warning-item"
            @click="showWarning(warning)"
          >
            {{ warning.store.name }} - {{ warning.product.name }}
          </div>
        </div>
      </div>
      
      <div class="chat-area">
        <div v-if="currentRoom">
          <h2>{{ currentRoom.name }}</h2>
          <div class="messages">
            <div v-for="msg in messages" :key="msg.id" class="message">
              <strong>{{ msg.sender.username }}:</strong> {{ msg.content }}
            </div>
          </div>
          <div class="input-area">
            <input v-model="newMessage" placeholder="输入消息..." />
            <button @click="sendMessage">发送</button>
          </div>
        </div>
        <div v-else>
          请选择聊天室
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()
const currentRoom = ref(null)
const newMessage = ref('')

const chatRooms = ref([])
const messages = ref([])
const warnings = ref([])

const selectRoom = async (room) => {
  currentRoom.value = room
  await messageStore.fetchMessages(room.id)
  messages.value = messageStore.messages
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentRoom.value) return
  
  await messageStore.sendMessage({
    room: currentRoom.value.id,
    message_type: 'text',
    content: newMessage.value.trim()
  })
  newMessage.value = ''
  messages.value = messageStore.messages
}

const showWarning = (warning) => {
  console.log('显示预警:', warning)
}

onMounted(async () => {
  await messageStore.fetchChatRooms()
  await messageStore.fetchInventoryWarnings()
  chatRooms.value = messageStore.chatRooms
  warnings.value = messageStore.inventoryWarnings
})
</script>

<style scoped>
.message-system {
  padding: 20px;
}

.main-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #ddd;
  padding-right: 20px;
}

.chat-rooms, .warnings {
  margin-bottom: 20px;
}

.room-item, .warning-item {
  padding: 10px;
  margin: 5px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.room-item:hover, .warning-item:hover {
  background: #f5f5f5;
}

.room-item.active {
  background: #e6f7ff;
  border-color: #1890ff;
}

.chat-area {
  flex: 1;
}

.messages {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 10px;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.input-area button {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
