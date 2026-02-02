package handler

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"

	"agent-flow-backend/internal/model"
	"agent-flow-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // 允许所有来源,生产环境需要配置
	},
}

// ChatHandler 聊天处理器
type ChatHandler struct {
	agentService *service.AgentService
	sessions     map[string]*Session
	sessionMutex sync.RWMutex
}

// Session WebSocket 会话
type Session struct {
	ID     string
	Conn   *websocket.Conn
	Send   chan model.StreamMessage
	mu     sync.Mutex
	closed bool
}

// NewChatHandler 创建聊天处理器
func NewChatHandler(agentService *service.AgentService) *ChatHandler {
	return &ChatHandler{
		agentService: agentService,
		sessions:     make(map[string]*Session),
	}
}

// HandleWebSocket 处理 WebSocket 连接
func (h *ChatHandler) HandleWebSocket(c *gin.Context) {
	sessionID := c.Query("session_id")
	if sessionID == "" {
		sessionID = uuid.New().String()
	}

	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}

	session := &Session{
		ID:   sessionID,
		Conn: conn,
		Send: make(chan model.StreamMessage, 256),
	}

	h.sessionMutex.Lock()
	h.sessions[sessionID] = session
	h.sessionMutex.Unlock()

	log.Printf("New WebSocket connection: session_id=%s", sessionID)

	// 启动读写协程
	go h.readPump(session)
	go h.writePump(session)
}

// readPump 读取客户端消息
func (h *ChatHandler) readPump(session *Session) {
	defer func() {
		h.closeSession(session)
	}()

	session.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	session.Conn.SetPongHandler(func(string) error {
		session.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		_, message, err := session.Conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket read error: %v", err)
			}
			break
		}

		// 解析消息
		var chatReq model.ChatRequest
		if err := json.Unmarshal(message, &chatReq); err != nil {
			log.Printf("Invalid message format: %v", err)
			continue
		}

		// 处理聊天请求
		go h.handleChatRequest(session, &chatReq)
	}
}

// writePump 向客户端发送消息
func (h *ChatHandler) writePump(session *Session) {
	ticker := time.NewTicker(54 * time.Second)
	defer func() {
		ticker.Stop()
		session.Conn.Close()
	}()

	for {
		select {
		case message, ok := <-session.Send:
			session.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				session.Conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			// 发送消息
			if err := session.Conn.WriteJSON(message); err != nil {
				log.Printf("WebSocket write error: %v", err)
				return
			}

		case <-ticker.C:
			// 发送心跳
			session.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := session.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// handleChatRequest 处理聊天请求
func (h *ChatHandler) handleChatRequest(session *Session, req *model.ChatRequest) {
	if req.SessionID == "" {
		req.SessionID = session.ID
	}

	log.Printf("Processing chat request: session_id=%s, message=%s", req.SessionID, req.Message)

	// 调用 Agent 服务流式接口
	err := h.agentService.StreamChat(req.Message, req.SessionID, func(chunk string) error {
		// 发送数据块到客户端
		msg := model.StreamMessage{
			Type:      "message",
			Content:   chunk,
			SessionID: req.SessionID,
			Timestamp: time.Now().Unix(),
		}

		select {
		case session.Send <- msg:
			return nil
		default:
			return nil // 通道满,跳过
		}
	})

	if err != nil {
		log.Printf("Agent service error: %v", err)
		errMsg := model.StreamMessage{
			Type:      "error",
			Content:   err.Error(),
			SessionID: req.SessionID,
			Timestamp: time.Now().Unix(),
		}
		session.Send <- errMsg
		return
	}

	// 发送完成标记
	doneMsg := model.StreamMessage{
		Type:      "done",
		Content:   "",
		SessionID: req.SessionID,
		Timestamp: time.Now().Unix(),
	}
	session.Send <- doneMsg
}

// closeSession 关闭会话
func (h *ChatHandler) closeSession(session *Session) {
	session.mu.Lock()
	defer session.mu.Unlock()

	if session.closed {
		return
	}

	session.closed = true
	close(session.Send)

	h.sessionMutex.Lock()
	delete(h.sessions, session.ID)
	h.sessionMutex.Unlock()

	log.Printf("Session closed: session_id=%s", session.ID)
}

// HandleSendMessage 处理同步消息发送 (REST API)
func (h *ChatHandler) HandleSendMessage(c *gin.Context) {
	var req model.ChatRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.SessionID == "" {
		req.SessionID = uuid.New().String()
	}

	// 调用 Agent 服务
	resp, err := h.agentService.Chat(req.Message, req.SessionID)
	if err != nil {
		log.Printf("Agent service error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, resp)
}

// HandleHealthCheck 健康检查
func (h *ChatHandler) HandleHealthCheck(c *gin.Context) {
	// 检查 Agent 服务
	err := h.agentService.HealthCheck()

	h.sessionMutex.RLock()
	sessionCount := len(h.sessions)
	h.sessionMutex.RUnlock()

	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status":        "unhealthy",
			"agent_service": err.Error(),
			"sessions":      sessionCount,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":   "healthy",
		"sessions": sessionCount,
	})
}
