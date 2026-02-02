package model

import "time"

// ChatMessage 聊天消息
type ChatMessage struct {
	ID        string    `json:"id"`
	SessionID string    `json:"session_id"`
	Role      string    `json:"role"` // "user" or "assistant"
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
}

// ChatRequest 聊天请求
type ChatRequest struct {
	Message   string `json:"message" binding:"required"`
	SessionID string `json:"session_id"`
}

// ChatResponse 聊天响应
type ChatResponse struct {
	Response  string `json:"response"`
	SessionID string `json:"session_id"`
}

// StreamMessage WebSocket 流式消息
type StreamMessage struct {
	Type      string `json:"type"` // "message", "done", "error"
	Content   string `json:"content"`
	SessionID string `json:"session_id"`
	Timestamp int64  `json:"timestamp"`
}

// AgentRequest Agent 服务请求
type AgentRequest struct {
	Message   string `json:"message"`
	SessionID string `json:"session_id"`
}

// AgentResponse Agent 服务响应
type AgentResponse struct {
	Response  string `json:"response"`
	SessionID string `json:"session_id"`
}
