package main

import (
	"fmt"
	"log"

	"agent-flow-backend/internal/config"
	"agent-flow-backend/internal/handler"
	"agent-flow-backend/internal/service"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// 加载配置
	cfg := config.LoadConfig()

	log.Printf("Starting Agent Flow Backend Server...")
	log.Printf("Agent Service URL: %s", cfg.AgentServiceURL)
	log.Printf("Server Port: %s", cfg.ServerPort)

	// 设置 Gin 模式
	if !cfg.Debug {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建 Gin 引擎
	router := gin.Default()

	// 配置 CORS
	corsConfig := cors.DefaultConfig()
	corsConfig.AllowAllOrigins = true
	corsConfig.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	corsConfig.AllowHeaders = []string{"Origin", "Content-Type", "Accept", "Authorization"}
	corsConfig.AllowWebSockets = true
	router.Use(cors.New(corsConfig))

	// 初始化服务
	agentService := service.NewAgentService(cfg.AgentServiceURL)

	// 初始化处理器
	chatHandler := handler.NewChatHandler(agentService)

	// 路由配置
	api := router.Group("/api")
	{
		// 聊天接口
		chat := api.Group("/chat")
		{
			chat.POST("/send", chatHandler.HandleSendMessage)
			chat.GET("/ws", chatHandler.HandleWebSocket)
		}

		// 健康检查
		api.GET("/health", chatHandler.HandleHealthCheck)
	}

	// 根路径
	router.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"service": "Agent Flow Backend",
			"status":  "running",
			"version": "0.1.0",
		})
	})

	// 启动服务器
	addr := fmt.Sprintf(":%s", cfg.ServerPort)
	log.Printf("Server starting on %s", addr)

	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
