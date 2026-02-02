<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <h2>🤖 天气助手</h2>
      <div class="connection-status" :class="{ connected: isConnected }">
        {{ isConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages-container" ref="messagesContainer">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message"
        :class="msg.role"
      >
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
        </div>
      </div>

      <!-- 正在输入指示器 -->
      <div v-if="isTyping" class="message assistant">
        <div class="message-bubble">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-container">
      <input
        v-model="inputMessage"
        @keyup.enter="sendMessage"
        :disabled="!isConnected || isSending"
        placeholder="询问天气或随便聊聊..."
        class="message-input"
      />
      <button
        @click="sendMessage"
        :disabled="!isConnected || isSending || !inputMessage.trim()"
        class="send-button"
      >
        {{ isSending ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import websocketService from '../services/websocket';

export default {
  name: 'ChatView',
  setup() {
    const messages = ref([]);
    const inputMessage = ref('');
    const isConnected = ref(false);
    const isSending = ref(false);
    const isTyping = ref(false);
    const messagesContainer = ref(null);
    const currentAssistantMessage = ref('');

    // 连接 WebSocket
    const connectWebSocket = () => {
      websocketService.connect(
        null, // 自动生成 session_id
        handleMessage,
        handleError,
        handleClose
      );
    };

    // 处理接收到的消息
    const handleMessage = (message) => {
      console.log('Received message:', message);

      switch (message.type) {
        case 'message':
          // 流式消息块
          if (!isTyping.value) {
            isTyping.value = true;
            currentAssistantMessage.value = '';
          }
          currentAssistantMessage.value += message.content;
          break;

        case 'done':
          // 消息完成
          if (currentAssistantMessage.value) {
            messages.value.push({
              role: 'assistant',
              content: currentAssistantMessage.value,
              timestamp: new Date()
            });
            currentAssistantMessage.value = '';
          }
          isTyping.value = false;
          isSending.value = false;
          scrollToBottom();
          break;

        case 'error':
          // 错误消息
          messages.value.push({
            role: 'assistant',
            content: `❌ 错误: ${message.content}`,
            timestamp: new Date()
          });
          isTyping.value = false;
          isSending.value = false;
          scrollToBottom();
          break;
      }
    };

    // 处理错误
    const handleError = (error) => {
      console.error('WebSocket error:', error);
      isConnected.value = false;
    };

    // 处理连接关闭
    const handleClose = () => {
      isConnected.value = false;
    };

    // 发送消息
    const sendMessage = () => {
      if (!inputMessage.value.trim() || isSending.value || !isConnected.value) {
        return;
      }

      const message = inputMessage.value.trim();

      // 添加用户消息到界面
      messages.value.push({
        role: 'user',
        content: message,
        timestamp: new Date()
      });

      // 发送到后端
      websocketService.sendMessage(message);

      // 清空输入框
      inputMessage.value = '';
      isSending.value = true;
      scrollToBottom();
    };

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    // 生命周期钩子
    onMounted(() => {
      connectWebSocket();

      // 监听连接状态
      const checkConnection = setInterval(() => {
        isConnected.value = websocketService.isConnected();
      }, 1000);

      // 清理定时器
      onUnmounted(() => {
        clearInterval(checkConnection);
        websocketService.disconnect();
      });
    });

    return {
      messages,
      inputMessage,
      isConnected,
      isSending,
      isTyping,
      messagesContainer,
      sendMessage,
      formatTime
    };
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.connection-status {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.2);
  transition: background 0.3s;
}

.connection-status.connected {
  background: rgba(76, 175, 80, 0.8);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #ffffff;
}

.message {
  display: flex;
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.assistant .message-bubble {
  background: #f0f0f0;
  color: #333;
}

.message-content {
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: 0.7rem;
  margin-top: 0.3rem;
  opacity: 0.7;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-container {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 24px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.message-input:focus {
  border-color: #667eea;
}

.message-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}
</style>
