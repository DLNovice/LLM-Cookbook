package service

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"

	"agent-flow-backend/internal/model"
)

// AgentService Agent 服务客户端
type AgentService struct {
	baseURL string
	client  *http.Client
}

// NewAgentService 创建 Agent 服务客户端
func NewAgentService(baseURL string) *AgentService {
	return &AgentService{
		baseURL: baseURL,
		client:  &http.Client{},
	}
}

// Chat 同步调用 Agent
func (s *AgentService) Chat(message, sessionID string) (*model.AgentResponse, error) {
	url := fmt.Sprintf("%s/agent/chat", s.baseURL)

	reqBody := model.AgentRequest{
		Message:   message,
		SessionID: sessionID,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	resp, err := s.client.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("post request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("agent service error: %s", string(body))
	}

	var agentResp model.AgentResponse
	if err := json.NewDecoder(resp.Body).Decode(&agentResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return &agentResp, nil
}

// StreamChat 流式调用 Agent (SSE)
func (s *AgentService) StreamChat(message, sessionID string, callback func(string) error) error {
	url := fmt.Sprintf("%s/agent/stream", s.baseURL)

	reqBody := model.AgentRequest{
		Message:   message,
		SessionID: sessionID,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "text/event-stream")

	resp, err := s.client.Do(req)
	if err != nil {
		return fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("agent service error: %s", string(body))
	}

	// 解析 SSE 流
	reader := bufio.NewReader(resp.Body)
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				break
			}
			return fmt.Errorf("read stream: %w", err)
		}

		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// SSE 格式: "event: message" 或 "data: content"
		if strings.HasPrefix(line, "event:") {
			event := strings.TrimSpace(strings.TrimPrefix(line, "event:"))

			if event == "done" {
				log.Println("Stream completed")
				break
			} else if event == "error" {
				// 读取下一行获取错误信息
				dataLine, _ := reader.ReadString('\n')
				errMsg := strings.TrimSpace(strings.TrimPrefix(dataLine, "data:"))
				return fmt.Errorf("agent error: %s", errMsg)
			}
		} else if strings.HasPrefix(line, "data:") {
			data := strings.TrimSpace(strings.TrimPrefix(line, "data:"))

			if data == "[DONE]" {
				break
			}

			// 回调处理数据块
			if err := callback(data); err != nil {
				return fmt.Errorf("callback error: %w", err)
			}
		}
	}

	return nil
}

// HealthCheck 健康检查
func (s *AgentService) HealthCheck() error {
	url := fmt.Sprintf("%s/health", s.baseURL)

	resp, err := s.client.Get(url)
	if err != nil {
		return fmt.Errorf("health check failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("agent service unhealthy: status %d", resp.StatusCode)
	}

	return nil
}
