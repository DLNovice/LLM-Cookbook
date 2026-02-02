package middlewares

import (
	"gin_demo/utils"
	"net/http"

	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(ctx *gin.Context) {
		token := ctx.GetHeader("Authorization")
		if token == "" {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			ctx.Abort()
			return
		}

		username, err := utils.ParseJWT(token)
		if err != nil {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			ctx.Abort() // 中止当前请求的处理链
			return
		}

		// 结合Set和Get方法，实现从中间件中取值
		ctx.Set("username", username)
		ctx.Next() // 继续处理下一个中间件或路由处理函数
	}
}
