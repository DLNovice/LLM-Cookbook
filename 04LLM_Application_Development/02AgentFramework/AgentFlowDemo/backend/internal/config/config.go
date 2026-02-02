package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

// Config 应用配置
type Config struct {
	ServerPort       string
	AgentServiceURL  string
	CorsAllowOrigins string
	Debug            bool
}

// LoadConfig 加载配置
func LoadConfig() *Config {
	// 加载 .env 文件
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	return &Config{
		ServerPort:       getEnv("SERVER_PORT", "8080"),
		AgentServiceURL:  getEnv("AGENT_SERVICE_URL", "http://localhost:8000"),
		CorsAllowOrigins: getEnv("CORS_ALLOW_ORIGINS", "*"),
		Debug:            getEnv("DEBUG", "true") == "true",
	}
}

// getEnv 获取环境变量,如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
