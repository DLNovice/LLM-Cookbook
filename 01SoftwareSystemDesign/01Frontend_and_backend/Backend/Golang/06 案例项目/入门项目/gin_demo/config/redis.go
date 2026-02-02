package config

import (
	"gin_demo/global"

	"github.com/go-redis/redis"
)

var RedisClient *redis.Client

func initRedis() {
	RedisClient = redis.NewClient(&redis.Options{
		Addr:     "localhost:6389",
		DB:       0, // 默认数据库(use default DB)
		Password: "",
	})

	_, err := RedisClient.Ping().Result()
	if err != nil {
		panic("Failed to connect to Redis")
	}

	global.RedisDB = RedisClient
}
