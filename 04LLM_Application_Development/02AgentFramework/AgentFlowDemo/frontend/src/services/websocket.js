/**
 * WebSocket 服务
 * 处理与后端的 WebSocket 通信
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = '';
    this.sessionId = '';
    this.onMessageCallback = null;
    this.onErrorCallback = null;
    this.onCloseCallback = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  /**
   * 连接 WebSocket
   */
  connect(sessionId, onMessage, onError, onClose) {
    this.sessionId = sessionId || this.generateSessionId();
    this.onMessageCallback = onMessage;
    this.onErrorCallback = onError;
    this.onCloseCallback = onClose;

    // 构建 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = import.meta.env.VITE_BACKEND_PORT || '8080';
    this.url = `${protocol}//${host}:${port}/api/chat/ws?session_id=${this.sessionId}`;

    console.log('Connecting to WebSocket:', this.url);

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (this.onMessageCallback) {
            this.onMessageCallback(message);
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (this.onErrorCallback) {
          this.onErrorCallback(error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        if (this.onCloseCallback) {
          this.onCloseCallback();
        }
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
    }
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect(
          this.sessionId,
          this.onMessageCallback,
          this.onErrorCallback,
          this.onCloseCallback
        );
      }, 2000 * this.reconnectAttempts);
    } else {
      console.error('Max reconnect attempts reached');
    }
  }

  /**
   * 发送消息
   */
  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const payload = {
        message: message,
        session_id: this.sessionId
      };
      this.ws.send(JSON.stringify(payload));
      return true;
    } else {
      console.error('WebSocket is not connected');
      return false;
    }
  }

  /**
   * 关闭连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * 生成会话 ID
   */
  generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }

  /**
   * 检查连接状态
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export default new WebSocketService();
