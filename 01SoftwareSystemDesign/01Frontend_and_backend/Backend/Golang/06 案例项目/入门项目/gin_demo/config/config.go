package config

import (
	"fmt"

	"github.com/spf13/viper"
)

// 定义一个Config结构体，其内部嵌套了两个匿名结构体：App和Database
type Config struct {
	App struct {
		Name string
		Port string
	}
	Database struct {
		Dsn          string
		MaxIdleConns int
		MaxOpenConns int
	}
}

var AppConfig *Config

func InitConfig() *Config {
	viper.SetConfigName("config")   // 配置文件名称（不需要带后缀）
	viper.SetConfigType("yml")      // 配置文件类型
	viper.AddConfigPath("./config") // 配置文件路径

	err := viper.ReadInConfig() // 读取配置文件
	if err != nil {
		panic(fmt.Errorf("fatal error config file: %w", err))
	}

	AppConfig = &Config{}
	viper.Unmarshal(AppConfig)

	initDB()
	initRedis()
	return AppConfig
}
