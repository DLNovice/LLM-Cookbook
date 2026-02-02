package router

import (
	"gin_demo/controllers"
	"gin_demo/middlewares"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func InitRouter() *gin.Engine {
	r := gin.Default()

	// 使用通配符或自定义函数来处理各种IP和域名
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // 开发环境使用通配符
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization", "Accept", "X-Requested-With"},
		ExposeHeaders:    []string{"Content-Length", "Authorization"},
		AllowCredentials: true, // 注意：使用通配符时，某些浏览器可能不允许credentials
		MaxAge:           12 * time.Hour,
	}))

	auth := r.Group("/api/auth") // 不要写为 /api//auth
	{
		auth.POST("/login", controllers.Login)

		auth.POST("/register", controllers.Register)
	}

	// 公开API - 不需要认证
	api := r.Group("/api")
	api.GET("/exchangeRates", controllers.GetExchangeRate)

	// 需要认证的API
	protected := r.Group("/api")
	protected.Use(middlewares.AuthMiddleware())
	{
		protected.POST("/exchangeRates", controllers.CreateExchangeRate)

		protected.POST("/articles", controllers.CreateArticle)
		protected.GET("/articles", controllers.GetArticles)
		protected.GET("/articles/:id", controllers.GetArticleByID)

		protected.POST("/articles/:id/like", controllers.LikeArticle)
		protected.GET("/articles/:id/like", controllers.GetArticleLikes)
	}

	return r
}
