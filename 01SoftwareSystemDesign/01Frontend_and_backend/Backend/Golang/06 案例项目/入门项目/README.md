>Go+Gin+Gorm+Vue3+Redis+MySQL快速上手实战教程，在学习之前，简易快速了解上述框架的基础知识，方便跟着如下教程将各个框架串起来。

参考：[Github: Web003Gin-01_gingormtutorials](https://github.com/Slumhee/Web003Gin-01_gingormtutorials)

一个非常详细的golang基础入门项目，没想到是高中生写的，tql！原文照顾到0基础，讲解的非常详尽，下面是简述版。



## 01 基础概念

概述：

- RESTful API：Representational State Transfer (译: 表述性状态转移)，其是一种软件架构风格，而非标准。故 RESTful API 即为一种 REST 风格的接口，或者说是满足 REST 风格的接口。
- MVC：Model-View-Controller，一种常用的软件架构模式，旨在将应用程序的关注点分离，提高代码的可维护性。



正好试试ClaudeCode + GLM：当前在linux平台下，与windows的主要区别就是配置文件位置不同

- 安装ClaudeCode：

  ```bash
  npm install -g @anthropic-ai/claude-code
  ```

- 申请key并配置：编辑或新增 Claude Code 配置文件 `~/.claude/settings.json`（注意，官方一般是不推荐设置`"ANTHROPIC_DEFAULT_HAIKU_MODEL"`等参数的，但如果不配置，默认模型输出的不是glm系列，以防万一还是配了一下）

  ```json
  {
    "env": {
      "ANTHROPIC_AUTH_TOKEN": "yourkey here",
      "API_TIMEOUT_MS": "3000000",
      "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
      "MCP_TOOL_TIMEOUT": "30000",
      "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
      "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
      "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
    },
    "permissions": {
      "defaultMode": "bypassPermissions"
    },
    "alwaysThinkingEnabled": false
  }
  ```

- 新打开一个终端，输入`claude`进入ClaudeCode，输入`/model`选择`default`模型，输入`/status`验证：
  ![image-20251118104021139](./assets/image-20251118104021139.png)

- 可以终端直接使用ClaudeCode，也可以VSCode安装`Claude Code for VS Code`插件，交互体验更好



## 02 Viper 读取 MySQL配置文件

>Viper概述：其核心作用是简化 Go 应用程序的配置管理，提供一个统一、灵活且强大的接口来处理来自不同源的配置数据。
>
>官方文档: https://github.com/spf13/viper
>
>Viper currently supports:
>
>- JSON
>- TOML
>- YAML
>- INI
>- envfile
>- Java Propeties

docker部署mysql：

```bash
docker run -d \
  --name mysql-study-gin \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=gin_db \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=123456 \
  -p 3309:3306 \
  mysql:8.0
```

基础指令：

```bash
docker exec -it mysql-study-gin /bin/bash
mysql -u user -p

# 后续创建表后，用于检查的示例sql
USE gin_db;
# 查看有哪些表
SHOW TABLES;
# 检查表结构
DESCRIBE users;
# 检查数据内容
SELECT * FROM users;
# 删除所有users数据
DELETE FROM users;

# 退出mysql客户端
EXIT;
# 退出docker容器
exit
```



创建项目：

```bash
mkdir gin_demo
cd gin_demo
go mod init gin_demo
```

安装依赖：

```go
go get gorm.io/driver/mysql
go get -u github.com/gin-gonic/gin
go get github.com/spf13/viper
go get -u gorm.io/gorm
```



创建config目录：

- 创建config.yml：

  ```yml
  app:
    name: CurrencyExchangeApp
    port: :3000
  
  database:
    host: localhost
    port: :3309
    user: user
    password: 123456
    name: currency_exchange_db
  ```

- 创建config.go：

  ```go
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
  		Host     string
  		Port     string
  		User     string
  		Password string
  		Name     string
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
  
  	return AppConfig
  }
  
  ```

  

主目录下撰写main.go

```go
package main

import (
	"fmt"
	"gin_demo/config"
)

func main() {
	// 读取配置信息
	config.InitConfig()
	fmt.Println(config.AppConfig.App.Name)
}

```

示例结果：

```bash
$ go run main.go 
CurrencyExchangeApp
```

当前目录结构：

```bash
.
├── config
│   ├── config.go
│   └── config.yml
├── go.mod
├── go.sum
└── main.go

2 directories, 5 files
```



## 03 Gin 创建路由

创建router目录及router.go

```go
package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func InitRouter() *gin.Engine {
	r := gin.Default()

	auth := r.Group("/api/auth") // 不要写为 /api//auth
	{
		auth.POST("/login", func(ctx *gin.Context) {
			ctx.AbortWithStatusJSON(http.StatusOK, gin.H{
				"msg": "Login Success",
			})
		})
		auth.POST("/register", func(ctx *gin.Context) {
			ctx.AbortWithStatusJSON(http.StatusOK, gin.H{
				"msg": "Register Success",
			})
		})
	}

	return r
}

```

优化main.go：

```go
package main

import (
	"fmt"
	"gin_demo/config"
	"gin_demo/router"
)

func main() {
	// 读取配置信息
	config.InitConfig()
	fmt.Println(config.AppConfig.App.Name)

	router := router.InitRouter()

	port := config.AppConfig.App.Port
	if port == "" {
		port = "8080"
	}
	fmt.Println("Server running on port", port)

	// 启动服务
	router.Run(port)
}

```

测试：成功返回`Login Success`

```bash
$ go run main.go 
CurrencyExchangeApp
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] POST   /api/auth/login           --> gin_demo/router.InitRouter.func1 (3 handlers)
[GIN-debug] POST   /api/auth/register        --> gin_demo/router.InitRouter.func2 (3 handlers)
Server running on port :3000
[GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
Please check https://github.com/gin-gonic/gin/blob/master/docs/doc.md#dont-trust-all-proxies for details.
[GIN-debug] Listening and serving HTTP on :3000
[GIN] 2025/11/18 - 11:07:35 | 200 |     123.476µs |             ::1 | POST     "/api/auth/login"

$ curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{}'
{"msg":"Login Success"}
```

当前目录结构：

```bash
$ tree
.
├── config
│   ├── config.go
│   └── config.yml
├── go.mod
├── go.sum
├── main.go
└── router
    └── router.go

3 directories, 6 files
```



## 04 Gorm 登录注册功能

### 1、连接MySQL

简化config.yml中的Database设计：将原有变量融合为一个dsn即可，再加上最大连接数等配置信息

```yml
app:
  name: CurrencyExchangeApp
  port: :3000

database:
  dsn: user:123456@tcp(127.0.0.1:3309)/gin_db?charset=utf8mb4&parseTime=True&loc=Local
  MaxIdleConns: 11
  MaxOpenCons: 114
```

config.go中的结构体也要同步修改：

```go
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
```

在config目录下创建db.go：用于连接数据库等配置

```go
package config

import (
	"gin_demo/global"
	"log"
	"time"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

func initDB() {
	// dsn := "user:123456@tcp(127.0.0.1:3309)/gin_db?charset=utf8mb4&parseTime=True&loc=Local"
	dsn := AppConfig.Database.Dsn
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to initialize database, got error: %v", err)
	}

	sqlDB, err := db.DB()

	sqlDB.SetMaxIdleConns(AppConfig.Database.MaxIdleConns)
	sqlDB.SetMaxOpenConns(AppConfig.Database.MaxOpenConns)
	sqlDB.SetConnMaxLifetime(time.Hour)

	if err != nil {
		log.Fatalf("Failed to configure database, got error: %v", err)
	}

	global.Db = db
}

```



创建global目录及global.go，一般用于存一些全局变量：

```go
package global

import (
	"gorm.io/gorm"
)

var (
	Db *gorm.DB
)

```

接下来先在config.go最后加一句`initDB()`，之后我们再完善逻辑。



### 2、实现注册功能

接下来就要写数据库相关逻辑了，创建controllers目录及相关代码，不过在写这个逻辑之前，需要创建models目录及user.go：

```go
package models

import "gorm.io/gorm"

type User struct {
	gorm.Model
	// gorm:"unique"：这是GORM框架的标签声明，表示这个字段在数据库中需要唯一约束
	Username string `gorm:"unique"`
	Password string
}

```

接下来，创建controllers目录及auth_controllers.go：

```go
package controllers

import (
	"gin_demo/models"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Register(ctx *gin.Context) {
	var user models.User

	// 使用Gin的绑定方法
	if err := ctx.ShouldBindJSON(&user); err != nil {
		ctx.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
}

```

此时梳理一下逻辑：略



基于Bcrypt实现加密：

- 概述：Bcrypt 是一种用于密码哈希的加密算法，它是基于 Blowfish 算法的加强版, 被广泛应用于存储密码和进行身份验证。
- 目的：
- 安装：`go get golang.org/x/crypto/bcrypt`

创建utils目录及utils.go：

```go
package utils

import "golang.org/x/crypto/bcrypt"

func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}
```



完善auth_controllers.go：加入刚才在utils中写的加密逻辑

```go
package controllers

import (
	"gin_demo/models"
	"gin_demo/utils"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Register(ctx *gin.Context) {
	var user models.User

	// 使用Gin的绑定方法
	if err := ctx.ShouldBindJSON(&user); err != nil {
		ctx.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	hashedPwd, err := utils.HashPassword(user.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	user.Password = hashedPwd
}

```



基于JWT传输信息：

- 概述：JSON Web Token(JWT | json 网络令牌)是一种开放标准(RFC 7519)，用于在网络应用环境间安全地传递声明(claims)。JWT 是一种紧凑且自包含的方式, 用于作为 JSON 对象在各方之间安全地传输信息。由于其信息是经过数字签名的, 所以可以确保发送的数据在传输过程中未被篡改。
- 组成部分:
  - Header
  - Payload：包含所传递的声明(Claims)
  - Signature
- 安装：`go get github.com/golang-jwt/jwt/v5`
- 用法：请求头里加入 Authorization，并加上 Bearer 前缀。

在utils.go中加入JWT相关逻辑：

```go
package utils

import (
	"time"

	"github.com/golang-jwt/jwt"
	"golang.org/x/crypto/bcrypt"
)

func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func GenerateJWT(username string) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": username,
		"exp":      time.Now().Add(time.Hour * 72).Unix(),
	})

	signedToken, err := token.SignedString([]byte("secret"))
	return "Bearer " + signedToken, err
}

```

写完后会发现import处爆红，找不到jwt：终端执行`go mod tidy`确保依赖被正确下载。



完善auth_controllers.go：加入刚才在utils中写的JWT逻辑

```go
package controllers

import (
	"gin_demo/models"
	"gin_demo/utils"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Register(ctx *gin.Context) {
	var user models.User

	// 使用Gin的绑定方法
	if err := ctx.ShouldBindJSON(&user); err != nil {
		ctx.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	hashedPwd, err := utils.HashPassword(user.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	user.Password = hashedPwd

	token, err := utils.GenerateJWT(user.Username)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	
	ctx.JSON(http.StatusOK, gin.H{"token": token})
}

```



基于GORM实现CRUD的逻辑：这里是在auth_controllers.go中完善用户注册相关逻辑

```go
err = global.Db.AutoMigrate(&user)
if err != nil {
    ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
    return
}

err = global.Db.Create(&user).Error
if err != nil {
    ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
    return
}
```

完整代码：

```go
package controllers

import (
	"gin_demo/global"
	"gin_demo/models"
	"gin_demo/utils"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Register(ctx *gin.Context) {
	var user models.User

	// 使用Gin的绑定方法
	if err := ctx.ShouldBindJSON(&user); err != nil {
		ctx.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	hashedPwd, err := utils.HashPassword(user.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	user.Password = hashedPwd

	token, err := utils.GenerateJWT(user.Username)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	err = global.Db.AutoMigrate(&user)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	err = global.Db.Create(&user).Error
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"token": token})
}

```



### 3、实现登录功能

在auth_controllers.go中加入登录逻辑：

```go
func Login(ctx *gin.Context) {
	var input struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := ctx.ShouldBindJSON(&input); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var user models.User

	if err := global.Db.Where("username = ?", input.Username).First(&user).Error; err != nil {
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": "wrong credentials"})
		return
	}
}
```



此时需要在utils.go中加入验证密码的逻辑：

```go
func checkPassword(hashedPassword, password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
	return err == nil
}
```

完善auth_controllers.go中的Login逻辑：加入CheckPassword，再和Register中的逻辑一样，返回Json格式的StatusOK

```go
func Login(ctx *gin.Context) {
	var input struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := ctx.ShouldBindJSON(&input); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var user models.User

	if err := global.Db.Where("username = ?", input.Username).First(&user).Error; err != nil {
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": "wrong credentials"})
		return
	}

	// 注意1：此处返回值为bool，就不能用 err != nil 那套了
	// 注意2：(user.Password, input.Password)，不要把顺序搞反了
	if !utils.CheckPassword(user.Password, input.Password) {
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": "wrong credentials"})
		return
	}

	token, err := utils.GenerateJWT(user.Username)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"token": token})
}
```



接下来就可以完善Router，测试Web了：针对router.go的InitRouter，重整逻辑，实现真正的login和register

```go
{
    auth.POST("/login", func(ctx *gin.Context) {
        ctx.AbortWithStatusJSON(http.StatusOK, gin.H{
            "msg": "Login Success",
        })
    })
    auth.POST("/register", func(ctx *gin.Context) {
        ctx.AbortWithStatusJSON(http.StatusOK, gin.H{
            "msg": "Register Success",
        })
    })
}
```

改为：

```go
{
    auth.POST("/login", controllers.Login)

    auth.POST("/register", controllers.Register)
}
```



开始测试：我这里3000端口临时有事，改用3005了

```bash
$ go run main.go 
CurrencyExchangeApp
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] POST   /api/auth/login           --> gin_demo/controllers.Login (3 handlers)
[GIN-debug] POST   /api/auth/register        --> gin_demo/controllers.Register (3 handlers)
Server running on port :3005
[GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
Please check https://github.com/gin-gonic/gin/blob/master/docs/doc.md#dont-trust-all-proxies for details.
[GIN-debug] Listening and serving HTTP on :3005
```



测试注册：

```bash
curl -X POST http://localhost:3005/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

示例结果：

```bash
# curl指令返回：
{"token":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3MDUyMDQsInVzZXJuYW1lI

# main.go程序日志：
[GIN] 2025/11/18 - 14:06:44 | 200 |  1.552525307s |             ::1 | POST     "/api/auth/register"
```

进入mysql中检查一下：

```bash
docker exec -it mysql-study-gin /bin/bash
mysql -u user -p

# 后续创建表后，用于检查的示例sql
USE gin_db;
# 检查表结构
DESCRIBE users;
# 检查数据内容
SELECT * FROM users;
```

示例结果：

```bash
mysql> SELECT * FROM users;
+----+-------------------------+-------------------------+------------+----------+--------------------------------------------------------------+
| id | created_at              | updated_at              | deleted_at | username | password                                                     |
+----+-------------------------+-------------------------+------------+----------+--------------------------------------------------------------+
|  1 | 2025-11-18 14:06:44.867 | 2025-11-18 14:06:44.867 | NULL       | testuser | $2a$14$h/V2PZ8kOdM2pwmsHpBe6u1dT.TtK73EtHkTDE1z9AYdF8aFvb8fq |
+----+-------------------------+-------------------------+------------+----------+--------------------------------------------------------------+
1 row in set (0.01 sec)
```



测试登录：

```bash
curl -X POST http://localhost:3005/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

测试结果：

```bash
# curl指令返回：
{"token":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3MDU2ODAsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.4OdjMR7PsfjDHvEHH1QD10UKXKmhqNPf96H7xmKs-WA"}

# main.go程序日志：
[GIN] 2025/11/18 - 14:14:40 | 200 |  1.520707609s |             ::1 | POST     "/api/auth/login"
```

成功！



## 05 实现业务功能

本章将实现两个功能：

1）汇率兑换功能

2）文章点赞功能



### 1、汇率兑换功能

撰写汇率兑换相关逻辑：在controllers下创建exchange_rate_controller.go，两个功能，即创建汇率信息与获取汇率信息

```go
package controllers

// 创建汇率信息

// 获取汇率信息
```

写逻辑之前，先在Models下创建exchange_rate.go

```go
package models

import "time"

type ExchangeRate struct {
	ID           uint      `gorm:"primarykey" json:"_id"`
	FromCurrency string    `json:"fromCurrency" binding:"required"`
	ToCurrency   string    `json:"toCurrency" binding:"required"`
	Rate         float64   `json:"rate" binding:"required"`
	Date         time.Time `json:"date"`
}

```

接着就可以完善exchange_rate_controller.go：

```go
package controllers

import (
	"gin_demo/global"
	"gin_demo/models"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// 创建汇率信息
func CreateExchangeRate(ctx *gin.Context) {
	var exchangeRate models.ExchangeRate
	if err := ctx.ShouldBindJSON(&exchangeRate); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	exchangeRate.Date = time.Now()
	if err := global.Db.Create(&exchangeRate).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if err := global.Db.Create(&exchangeRate).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, exchangeRate)
}

// 获取汇率信息
func GetExchangeRate(ctx *gin.Context) {
	var exchangeRates []models.ExchangeRate
	if err := global.Db.First(&exchangeRates, ctx.Param("id")).Error; err != nil {
		ctx.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, exchangeRates)
}

```



### 2、中间件

>中间件是为了过滤路由而发明的一种机制, 也就是 http 请求来到时先经过中间件, 再到具体的处理函数。

用户必须要登录或者注册, 有了 jwt 才可以创建对应的汇率内容，此时就需要中间件做过滤。

自定义中间件, 请参考 Gin 的官方文档 - https://gin-gonic.com/zh-cn/docs/examples/custom-middleware/



在utils.go中，加入解析JWT的部分：

```go
func ParseJWT(tokenString string) (string, error) {
	// 去除开头的“Bearer”
	if len(tokenString) > 7 && tokenString[:7] == "Bearer " {
		tokenString = tokenString[7:]
	}

	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected Signing Method")
		}
		return []byte("secret"), nil
	})

	if err != nil {
		return "", err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		username, ok := claims["username"].(string)
		if !ok {
			return "", errors.New("username claim is not a string")
		}
		return username, nil
	}

	return "", err
}

```



创建middlewares目录及auth_middleware.go：本质就是写一个返回值为gin.HandlerFunc类型的函数即可

```go
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

```



中间件配置完毕，接下来在Router中配置入口：

```go
package router

import (
	"gin_demo/controllers"
	"gin_demo/middlewares"

	"github.com/gin-gonic/gin"
)

func InitRouter() *gin.Engine {
	r := gin.Default()

	auth := r.Group("/api/auth") // 不要写为 /api//auth
	{
		auth.POST("/login", controllers.Login)

		auth.POST("/register", controllers.Register)
	}

	api := r.Group("/api")
	api.GET("/exchangeRates", controllers.GetExchangeRate)
	api.Use(middlewares.AuthMiddleware())
	{
		api.POST("/exchageRates", controllers.CreateExchangeRate)
	}

	return r
}

```

测试：直接插入不行，返回`[GIN] 2025/11/18 - 15:19:00 | 404 |         993ns |             ::1 | POST     "/api/exchangeRates"`

```bash
curl -X POST http://localhost:3005/api/exchangeRates \
  -H "Content-Type: application/json" \
  -d '{
    "_id": 1,
    "fromCurrency": "EUR",
    "toCurrency": "USD",
    "rate": 1.1
  }'
```

奇怪，就算不行也不应该返回404这个状态码，修改Router：

```go
package router

import (
	"gin_demo/controllers"
	"gin_demo/middlewares"

	"github.com/gin-gonic/gin"
)

func InitRouter() *gin.Engine {
	r := gin.Default()

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
	}

	return r
}

```

且检查发现`CreateExchangeRate`与`GetExchangeRate`中数据库表处存在问题：

- 添加了数据库表自动迁移：`if err := global.Db.AutoMigrate(&exchangeRate); err != nil`
- 删除了重复的 `global.Db.Create(&exchangeRate).Error` 调用

这样GET和POST接口都会自动创建数据库表。

```go
package controllers

import (
	"gin_demo/global"
	"gin_demo/models"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// 创建汇率信息
func CreateExchangeRate(ctx *gin.Context) {
	var exchangeRate models.ExchangeRate
	if err := ctx.ShouldBindJSON(&exchangeRate); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 自动迁移数据库表
	if err := global.Db.AutoMigrate(&exchangeRate); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	exchangeRate.Date = time.Now()
	if err := global.Db.Create(&exchangeRate).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, exchangeRate)
}

// 获取汇率信息
func GetExchangeRate(ctx *gin.Context) {
	// 自动迁移数据库表
	var exchangeRate models.ExchangeRate
	if err := global.Db.AutoMigrate(&exchangeRate); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	var exchangeRates []models.ExchangeRate
	// 获取所有汇率数据
	if err := global.Db.Find(&exchangeRates).Error; err != nil {
		ctx.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, exchangeRates)
}

```



测试：

- 未登录，直接插入：返回`{"error":"Unauthorized"}`

  ```bash
  $ curl -X POST http://localhost:3005/api/exchangeRates \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \
    -d '{"_id": 1, "fromCurrency": "EUR", "toCurrency": "USD", "rate": 1.1}'
  
  {"error":"Unauthorized"}
  ```

- 先获取token，再插入：

  - 撰写一个shell脚本：

    ```shell
    #!/bin/bash
    
    echo "=== 货币汇率API测试 ==="
    echo
    
    # 1. 登录获取token
    echo "1. 登录获取token..."
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:3005/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "password": "password123"}')
    
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo "Token: $TOKEN"
    echo
    
    # 2. 创建汇率数据
    echo "2. 创建汇率数据..."
    curl -X POST http://localhost:3005/api/exchangeRates \
      -H "Content-Type: application/json" \
      -H "Authorization: $TOKEN" \
      -d '{"_id": 10, "fromCurrency": "EUR", "toCurrency": "USD", "rate": 1.1}'
    echo
    echo
    
    # 3. 获取汇率数据
    echo "3. 获取汇率数据..."
    curl -X GET http://localhost:3005/api/exchangeRates
    echo
    echo
    
    echo "=== 测试完成 ==="
    ```

  - 测试：

    ```bash
    $ bash test_api.sh 
    === 货币汇率API测试 ===
    
    1. 登录获取token...
    Token: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3MTI0NzgsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.JZwoc9dVdTL0qrDD6TyaMgDNCfZLWamjxI2uDk4WwtE
    
    2. 创建汇率数据...
    {"_id":10,"fromCurrency":"EUR","toCurrency":"USD","rate":1.1,"date":"2025-11-18T16:07:58.698699065+08:00"}
    
    3. 获取汇率数据...
    [{"_id":10,"fromCurrency":"EUR","toCurrency":"USD","rate":1.1,"date":"2025-11-18T16:07:58.699+08:00"}]
    
    === 测试完成 ===
    ```

  - 主程序那里也正常返回了200：

    ```bash
    [GIN] 2025/11/18 - 16:07:58 | 200 |  1.527980129s |             ::1 | POST     "/api/auth/login"
    [GIN] 2025/11/18 - 16:07:58 | 200 |   32.795723ms |             ::1 | POST     "/api/exchangeRates"
    [GIN] 2025/11/18 - 16:07:58 | 200 |   19.115562ms |             ::1 | GET      "/api/exchangeRates"
    ```

  - 检查数据库：正常创建了数据表，并成功插入了数据

    ```mysql
    mysql> SHOW TABLES;
    +------------------+
    | Tables_in_gin_db |
    +------------------+
    | exchange_rates   |
    | users            |
    +------------------+
    2 rows in set (0.00 sec)
    
    mysql> SELECT * FROM exchange_rates;
    +----+---------------+-------------+------+-------------------------+
    | id | from_currency | to_currency | rate | date                    |
    +----+---------------+-------------+------+-------------------------+
    | 10 | EUR           | USD         |  1.1 | 2025-11-18 16:07:58.699 |
    +----+---------------+-------------+------+-------------------------+
    1 row in set (0.00 sec)
    ```

    

### 3、文章功能

在models目录下创建article.go：

```go
package models

import "gorm.io/gorm"

type Article struct {
	gorm.Model
	Title string `binding:"required"`
	Content string `binding:"required"`
	Preview string `binding:"required"`
}
```

在controller目录下创建article_controller.go：撰写“文章”相关业务逻辑，类似于刚才汇率兑换功能中的Create与Get逻辑

```go
package controllers

import (
	"errors"
	"gin_demo/global"
	"gin_demo/models"
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func CreateArticle(ctx *gin.Context) {
	var article models.Article

	if err := ctx.ShouldBindJSON(&article); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 保存到数据库
	if err := global.Db.AutoMigrate(&article); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Article created successfully"})

	if err := global.Db.Create(&article).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusCreated, article)
}

func GetArticles(ctx *gin.Context) {
	var articles []models.Article

	if err := global.Db.Find(&articles).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, articles)
}

func GetArticleByID(ctx *gin.Context) {
	id := ctx.Param("id")

	var article models.Article

	if err := global.Db.Where("id = ?", id).First(&article).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			ctx.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	ctx.JSON(http.StatusOK, article)
}

```

后续完善点赞功能后，再一块测试。



## 06 Redis部分

> 为了实现点赞功能，这里加入Redis模块，redis基础可参考：[Redis/README.md](Redis/README.md)

点赞功能很适合Redis，实时性、并发性要求高，一致性要求不高。



### 1、配置Redis

docker安装redis：

```bash
docker run -d \
  --name redis-gin-demo \
  -p 6389:6379 \
  -v redis-data:/data \
  redis redis-server --appendonly yes
```

测试：

```bash
# 进入 Redis 容器内部使用 redis-cli
docker exec -it redis-gin-demo redis-cli

# 进入容器 Bash（可查看配置等）
docker exec -it myredis bash

# 执行 Redis 命令
127.0.0.1:6379> set name "hello"
OK
127.0.0.1:6379> get name
"hello"
```



golang安装redis依赖：

```bash
go get -u github.com/go-redis/redis
```

修改global，加入Redis全局变量：

```go
package global

import (
	"github.com/go-redis/redis"
	"gorm.io/gorm"
)

var (
	Db      *gorm.DB
	RedisDB *redis.Client
)

```

在config目录下创建redis.go：

```go
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

```

在config.go中加一行：`initRedis()`



### 2、实现点赞功能

在controllers目录下新建like_controller.go：

```go
package controllers

import (
	"gin_demo/global"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis"
)

// 实现点赞功能
func LikeArticle(ctx *gin.Context) {
	articleID := ctx.Param("id")

	likeKey := "article:" + articleID + ":likes"

	if err := global.RedisDB.Incr(likeKey).Err(); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Successfully liked the article"})
}

// 获取点赞数
func GetArticleLikes(ctx *gin.Context) {
	articleID := ctx.Param("id")

	likeKey := "article:" + articleID + ":likes"

	likes, err := global.RedisDB.Get(likeKey).Result()

	if err == redis.Nil {
		likes = "0"
	} else if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"likes": likes})
}

```



补充重要概念: 原子性

- 原子性确保一个操作在执行过程中是不可被打断的。对于原子操作, 要么所有的步骤都成功完成并对外可见, 要么这些步骤都不执行, 系统的状态保持不变。
- `INCR`和`DECR`操作在 Redis 中就是原子操作(原子性的)。



修改router.go：补充几行路由即可

```go
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
```



### 3、增加缓存

文章预览页面,，若有非常多的文章内容(几千条内容)，且此项目用户量较大，若无缓存，所有的请求都需要直接访问数据库，可能带来的风险。

修改controllers/artical_controller.go：

- 思路概述：
  - 当新增文章时, 除了更新数据库, 还要同步更新或删除缓存中的对应数据。这样, 下一次读取时, 缓存中的数据就是最新的。
  - 备注：或者新增文章时, 不直接更新缓存, 而是删除缓存中的旧数据。下次读取时, 由于缓存没有命中, 从数据库中读取最新数据并重新写入缓存。

- 具体操作：原教程中这里代码存在些许冗余，这里稍微优化了下
  - 声明变量 var cacheKey = "articles"
  - 优化GetArticles：处理面向缓存的几种情况


```go
func GetArticles(ctx *gin.Context) {
	// 检查缓存
	cachedData, err := global.RedisDB.Get(cacheKey).Result()
	if err == nil {
		// 缓存命中，解析JSON数据并返回
		var articles []models.Article
		if err := json.Unmarshal([]byte(cachedData), &articles); err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse cached data"})
			return
		}
		ctx.JSON(http.StatusOK, articles)
		return
	}

	// 缓存不存在，从数据库中获取数据
	var articles []models.Article
	if err := global.Db.Find(&articles).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 将数据转换为JSON格式
	articleJSON, err := json.Marshal(articles)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 存入缓存，设置10分钟过期时间
	if err := global.RedisDB.Set(cacheKey, articleJSON, 10*time.Minute).Err(); err != nil {
		// 缓存失败不影响主要功能，可以选择记录日志
		// 这里不返回错误，因为数据已经成功获取
	}

	ctx.JSON(http.StatusOK, articles)
}
```



但是，若在缓存有效期内, 用户又新增了一些文章, 此时用户通过缓存得到文章, 将看不到变化。

- 解决方法案例: 常见的缓存失效策略
  1. 设置过期时间(我们已经做过了)
  2. 主动更新缓存
- 修改`controllers/artical_controller.go`：在`CreateArticle`最终`ctx.JSON(http.StatusCreated, article)`前加入一行`Redis Del`命令即可

```go
func CreateArticle(ctx *gin.Context) {
	var article models.Article

	if err := ctx.ShouldBindJSON(&article); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 保存到数据库
	if err := global.Db.AutoMigrate(&article); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Article created successfully"})

	if err := global.Db.Create(&article).Error; err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 删除缓存
	if err := global.RedisDB.Del(cacheKey).Err(); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 返回创建的文章
	ctx.JSON(http.StatusCreated, article)
}
```



### 4、开始测试

记录一下清理mysql、redis数据相关sql：后续会用到

```bash
docker exec -it mysql-study-gin /bin/bash
mysql -u user -p

USE gin_db;
SHOW TABLES;
DELETE FROM articles;
ALTER TABLE articles AUTO_INCREMENT = 1;
```

```bash
docker exec -it redis-gin-demo /bin/bash
redis-cli --raw

KEYS *
redis-cli DEL articles
```



#### 1）测试基础功能

准备一个shell脚本：mysql与redis均启动后，启动`go run main.go`，之后运行此脚本

```shell
#!/bin/bash

echo "=== 文章相关API测试 ==="
echo

BASE_URL="http://localhost:3005"

# 0. 登录获取token
echo "0. 登录获取token..."
echo "请求URL: $BASE_URL/api/auth/login"
LOGIN_RESPONSE=$(curl -v -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}' 2>&1)

echo "登录响应: $LOGIN_RESPONSE"

# 尝试多种方式提取token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# 如果上面的方式失败，尝试jq解析
if [ -z "$TOKEN" ]; then
    TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token' 2>/dev/null)
fi

# 如果还是为空，尝试其他可能的字段名
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "错误：无法获取token，登录响应: $LOGIN_RESPONSE"
    exit 1
fi

# 移除可能存在的Bearer前缀
if [[ $TOKEN == Bearer* ]]; then
    TOKEN="${TOKEN#Bearer }"
fi

echo "获取到的Token: $TOKEN"
echo "Token长度: ${#TOKEN}"
echo

echo "=== Article API 测试开始 ==="

# 验证token不为空
if [ -z "$TOKEN" ]; then
    echo "错误：Token为空，无法继续测试"
    exit 1
fi

echo "1. 创建文章..."
echo "使用的Authorization Header: Bearer $TOKEN"

# 创建文章1
echo "创建文章1..."
RESP1=$(curl -v -X POST $BASE_URL/api/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"测试文章1","content":"这是测试文章1的内容","preview":"文章1预览"}' 2>&1)
echo "文章1创建结果: $RESP1"
echo

# 创建文章2
echo "创建文章2..."
RESP2=$(curl -v -X POST $BASE_URL/api/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"测试文章2","content":"这是测试文章2的内容","preview":"文章2预览"}' 2>&1)
echo "文章2创建结果: $RESP2"
echo

echo "2. 获取文章列表..."
ARTICLES=$(curl -v -X GET $BASE_URL/api/articles \
  -H "Authorization: Bearer $TOKEN" 2>&1)
echo "文章列表: $ARTICLES"
echo

echo "3. 获取单个文章（假设ID为1）..."
ARTICLE=$(curl -v -X GET $BASE_URL/api/articles/1 \
  -H "Authorization: Bearer $TOKEN" 2>&1)
echo "单个文章: $ARTICLE"
echo

echo "4. 测试错误情况..."

# 测试无效的token
echo "测试无效token..."
INVALID_TOKEN_RESPONSE=$(curl -v -X GET $BASE_URL/api/articles \
  -H "Authorization: Bearer invalid_token_123" 2>&1)
echo "无效token响应: $INVALID_TOKEN_RESPONSE"
echo

# 测试无token的请求
echo "测试无token请求..."
NO_TOKEN_RESPONSE=$(curl -v -X GET $BASE_URL/api/articles 2>&1)
echo "无token响应: $NO_TOKEN_RESPONSE"
echo

echo "=== Article API 测试完成 ==="
echo

echo "=== 数据清理选项 ==="
echo "如需清理测试数据，请在MySQL中执行以下SQL语句："
echo "USE your_database_name;"
echo "DELETE FROM articles;"
echo "ALTER TABLE articles AUTO_INCREMENT = 1;"
echo
echo "或在Redis中执行："
echo "redis-cli DEL articles"
echo

```

测试结果：测试成功，先获取token → 之后创建文章1和文章2 → 接着获取全部文章的内容 → 接着根据ID1获取文章1的内容 → 最后测试一些错误内容

- `main.go`日志

  ```bash
  [GIN] 2025/11/19 - 13:04:06 | 200 |  1.531724472s |             ::1 | POST     "/api/auth/login"
  [GIN-debug] [WARNING] Headers were already written. Wanted to override status code 200 with 201
  [GIN] 2025/11/19 - 13:04:06 | 200 |   43.738244ms |             ::1 | POST     "/api/articles"
  [GIN-debug] [WARNING] Headers were already written. Wanted to override status code 200 with 201
  [GIN] 2025/11/19 - 13:04:06 | 200 |   23.268526ms |             ::1 | POST     "/api/articles"
  [GIN] 2025/11/19 - 13:04:06 | 200 |    4.788921ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:04:06 | 200 |    2.167906ms |             ::1 | GET      "/api/articles/1"
  [GIN] 2025/11/19 - 13:04:06 | 401 |     119.368µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:04:06 | 401 |      28.842µs |             ::1 | GET      "/api/articles"
  ```

- shell脚本日志：

  ```bash
  === 文章相关API测试 ===
  
  0. 登录获取token...
  请求URL: http://localhost:3005/api/auth/login
  登录响应: Note: Unnecessary use of -X or --request, POST is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > POST /api/auth/login HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Content-Type: application/json
  > Content-Length: 51
  > 
  } [51 bytes data]
  * upload completely sent off: 51 bytes
  100    51    0     0  100    51      0     42  0:00:01  0:00:01 --:--:--    42< HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 154
  < 
  { [154 bytes data]
  100   205  100   154  100    51    100     33  0:00:01  0:00:01 --:--:--   133
  * Connection #0 to host localhost left intact
  {"token":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY"}
  获取到的Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  Token长度: 135
  
  === Article API 测试开始 ===
  1. 创建文章...
  使用的Authorization Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  创建文章1...
  文章1创建结果: Note: Unnecessary use of -X or --request, POST is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > POST /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Content-Type: application/json
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  > Content-Length: 92
  > 
  } [92 bytes data]
  * upload completely sent off: 92 bytes
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 246
  < 
  { [246 bytes data]
  100   338  100   246  100    92   5433   2032 --:--:-- --:--:-- --:--:--  7511
  * Connection #0 to host localhost left intact
  {"message":"Article created successfully"}{"ID":1,"CreatedAt":"2025-11-19T13:04:06.326+08:00","UpdatedAt":"2025-11-19T13:04:06.326+08:00","DeletedAt":null,"Title":"测试文章1","Content":"这是测试文章1的内容","Preview":"文章1预览"}
  
  创建文章2...
  文章2创建结果: Note: Unnecessary use of -X or --request, POST is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > POST /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Content-Type: application/json
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  > Content-Length: 92
  > 
  } [92 bytes data]
  * upload completely sent off: 92 bytes
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 246
  < 
  { [246 bytes data]
  100   338  100   246  100    92  10223   3823 --:--:-- --:--:-- --:--:-- 14083
  * Connection #0 to host localhost left intact
  {"message":"Article created successfully"}{"ID":2,"CreatedAt":"2025-11-19T13:04:06.365+08:00","UpdatedAt":"2025-11-19T13:04:06.365+08:00","DeletedAt":null,"Title":"测试文章2","Content":"这是测试文章2的内容","Preview":"文章2预览"}
  
  2. 获取文章列表...
  文章列表: Note: Unnecessary use of -X or --request, GET is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > GET /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  > 
  * Request completely sent off
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 411
  < 
  { [411 bytes data]
  100   411  100   411    0     0  72155      0 --:--:-- --:--:-- --:--:-- 82200
  * Connection #0 to host localhost left intact
  [{"ID":1,"CreatedAt":"2025-11-19T13:04:06.326+08:00","UpdatedAt":"2025-11-19T13:04:06.326+08:00","DeletedAt":null,"Title":"测试文章1","Content":"这是测试文章1的内容","Preview":"文章1预览"},{"ID":2,"CreatedAt":"2025-11-19T13:04:06.365+08:00","UpdatedAt":"2025-11-19T13:04:06.365+08:00","DeletedAt":null,"Title":"测试文章2","Content":"这是测试文章2的内容","Preview":"文章2预览"}]
  
  3. 获取单个文章（假设ID为1）...
  单个文章: Note: Unnecessary use of -X or --request, GET is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > GET /api/articles/1 HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODc4NDYsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.C-zMcUK_rz9L28nRhYDl14ngmEdak79ECVqPoGS0qKY
  > 
  * Request completely sent off
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 204
  < 
  { [204 bytes data]
  100   204  100   204    0     0  66885      0 --:--:-- --:--:-- --:--:-- 68000
  * Connection #0 to host localhost left intact
  {"ID":1,"CreatedAt":"2025-11-19T13:04:06.326+08:00","UpdatedAt":"2025-11-19T13:04:06.326+08:00","DeletedAt":null,"Title":"测试文章1","Content":"这是测试文章1的内容","Preview":"文章1预览"}
  
  4. 测试错误情况...
  测试无效token...
  无效token响应: Note: Unnecessary use of -X or --request, GET is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > GET /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Authorization: Bearer invalid_token_123
  > 
  * Request completely sent off
  < HTTP/1.1 401 Unauthorized
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 24
  < 
  { [24 bytes data]
  100    24  100    24    0     0  23529      0 --:--:-- --:--:-- --:--:-- 24000
  * Connection #0 to host localhost left intact
  {"error":"Unauthorized"}
  
  测试无token请求...
  无token响应: Note: Unnecessary use of -X or --request, GET is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > GET /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > 
  * Request completely sent off
  < HTTP/1.1 401 Unauthorized
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:04:06 GMT
  < Content-Length: 24
  < 
  { [24 bytes data]
  100    24  100    24    0     0  39538      0 --:--:-- --:--:-- --:--:-- 24000
  * Connection #0 to host localhost left intact
  {"error":"Unauthorized"}
  
  === Article API 测试完成 ===
  
  === 数据清理选项 ===
  如需清理测试数据，请在MySQL中执行以下SQL语句：
  USE your_database_name;
  DELETE FROM articles;
  ALTER TABLE articles AUTO_INCREMENT = 1;
  
  或在Redis中执行：
  redis-cli DEL articles
  ```

- 查看数据库验证：已正确创建数据库并插入数据

  ```bash
  mysql> SHOW TABLES;
  +------------------+
  | Tables_in_gin_db |
  +------------------+
  | exchange_rates   |
  | users            |
  +------------------+
  2 rows in set (0.00 sec)
  
  mysql> SHOW TABLES;
  +------------------+
  | Tables_in_gin_db |
  +------------------+
  | articles         |
  | exchange_rates   |
  | users            |
  +------------------+
  3 rows in set (0.01 sec)
  
  mysql> SELECT * FROM articles;
  +----+-------------------------+-------------------------+------------+-------+------------+---------+
  | id | created_at              | updated_at              | deleted_at | title | content    | preview |
  +----+-------------------------+-------------------------+------------+-------+------------+---------+
  |  1 | 2025-11-19 13:04:06.326 | 2025-11-19 13:04:06.326 | NULL       | ????1 | ??????1??? | ??1??   |
  |  2 | 2025-11-19 13:04:06.365 | 2025-11-19 13:04:06.365 | NULL       | ????2 | ??????2??? | ??2??   |
  +----+-------------------------+-------------------------+------------+-------+------------+---------+
  2 rows in set (0.00 sec)
  ```

  

#### 2）测试Redis效果

先到数据库中删除之前的测试数据：

```bash
mysql> DELETE FROM articles;
Query OK, 2 rows affected (0.01 sec)

mysql> ALTER TABLE articles AUTO_INCREMENT = 1;
Query OK, 0 rows affected (0.01 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

撰写新的测试脚本：主要测试内容如下

1. Redis连接检查 - 验证Redis服务是否正常运行
2. 缓存状态监控 - 实时检查缓存键的存在、大小和TTL
3. 首次查询测试 - 验证从数据库读取数据并建立缓存
4. 缓存命中测试 - 验证后续请求从缓存读取
5. 缓存失效测试 - 验证创建文章时缓存被正确删除
6. 缓存重建测试 - 验证缓存失效后重新建立
7. 性能对比测试 - 对比数据库查询和缓存查询的性能差异
8. Redis信息展示 - 显示Redis服务器状态和内存使用情况

```shell
#!/bin/bash

echo "=== Redis缓存效果专项测试 ==="
echo

BASE_URL="http://localhost:3005"
CACHE_KEY="articles"

# Redis容器配置
REDIS_CONTAINER_NAME="redis-gin-demo"  # 默认容器名
REDIS_CLI="docker exec $REDIS_CONTAINER_NAME redis-cli"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 辅助函数
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 自动检测Redis容器名称
detect_redis_container() {
    print_step "检测Redis容器"

    # 查找运行在6389端口的Redis容器
    REDIS_CONTAINER=$(docker ps --filter "publish=6389" --format "{{.Names}}" | head -1)

    if [ -n "$REDIS_CONTAINER" ]; then
        REDIS_CONTAINER_NAME="$REDIS_CONTAINER"
        REDIS_CLI="docker exec $REDIS_CONTAINER_NAME redis-cli"
        print_success "找到Redis容器: $REDIS_CONTAINER_NAME"
        echo "  CLI命令: $REDIS_CLI"
    else
        # 尝试查找名称包含redis的容器
        REDIS_CONTAINER=$(docker ps --filter "name=redis" --format "{{.Names}}" | head -1)
        if [ -n "$REDIS_CONTAINER" ]; then
            REDIS_CONTAINER_NAME="$REDIS_CONTAINER"
            REDIS_CLI="docker exec $REDIS_CONTAINER_NAME redis-cli"
            print_success "找到Redis容器: $REDIS_CONTAINER_NAME"
            echo "  CLI命令: $REDIS_CLI"
        else
            print_error "未找到运行中的Redis容器"
            echo "请确保Redis容器正在运行并映射了端口"
            exit 1
        fi
    fi
    echo
}

# 检查Redis连接
check_redis() {
    print_step "检查Redis连接"

    echo "测试Redis连接配置:"
    echo "  容器名称: $REDIS_CONTAINER_NAME"
    echo "  CLI命令: $REDIS_CLI"
    echo

    # 测试连接
    PING_RESULT=$($REDIS_CLI ping 2>&1)
    PING_EXIT_CODE=$?

    echo "Redis PING响应: $PING_RESULT"
    echo "退出代码: $PING_EXIT_CODE"
    echo

    if [ $PING_EXIT_CODE -eq 0 ] && [ "$PING_RESULT" = "PONG" ]; then
        print_success "Redis连接正常"

        # 额外测试：基本操作
        echo "测试基本Redis操作..."

        # 测试SET操作
        TEST_KEY="test_connection_$(date +%s)"
        TEST_VALUE="test_value"

        if $REDIS_CLI SET $TEST_KEY "$TEST_VALUE" > /dev/null 2>&1; then
            RETRIEVED_VALUE=$($REDIS_CLI GET $TEST_KEY 2>/dev/null)

            if [ "$RETRIEVED_VALUE" = "$TEST_VALUE" ]; then
                print_success "Redis读写测试通过"
                $REDIS_CLI DEL $TEST_KEY > /dev/null 2>&1  # 清理测试数据
            else
                print_warning "Redis读写测试失败 - 值不匹配"
            fi
        else
            print_warning "Redis写入测试失败"
        fi
    else
        print_error "Redis连接失败"
        echo "可能的原因:"
        echo "1. Redis容器未运行"
        echo "2. Redis服务未启动"
        echo "3. Docker权限问题"
        echo "4. 容器名称不正确"
        echo

        # 尝试手动连接测试
        echo "尝试手动连接测试:"
        echo "  命令: $REDIS_CLI ping"
        echo "  原始输出:"
        $REDIS_CLI ping 2>&1
        echo

        # 提供解决方案
        echo "建议解决方案:"
        echo "1. 检查Redis容器: docker ps | grep redis"
        echo "2. 启动容器: ./start_docker_redis.sh"
        echo "3. 验证容器名: docker ps --format 'table {{.Names}}\t{{.Ports}}'"
        echo

        # 询问是否继续
        read -p "Redis连接失败，是否继续测试其他部分? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    echo
}

# 0. 登录获取token
get_token() {
    print_step "登录获取Token"

    LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "password": "password123"}')

    echo "登录响应: $LOGIN_RESPONSE"

    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$TOKEN" ]; then
        print_error "无法获取Token"
        echo "登录响应: $LOGIN_RESPONSE"
        exit 1
    fi

    print_success "Token获取成功"
    echo "原始Token: ${TOKEN:0:50}..."

    # 移除Bearer前缀（因为GenerateJWT已经添加了Bearer，但我们需要纯token用于Authorization header）
    if [[ $TOKEN == Bearer* ]]; then
        TOKEN="${TOKEN#Bearer }"
        echo "已移除Bearer前缀"
    fi

    echo "最终Token: ${TOKEN:0:50}..."
    echo "Token长度: ${#TOKEN}"
    echo
}

# 1. 清理环境和缓存
clean_environment() {
    print_step "清理测试环境"

    # 清理Redis缓存
    REDIS_RESULT=$($REDIS_CLI DEL $CACHE_KEY 2>/dev/null)
    if [ "$REDIS_RESULT" -gt 0 ]; then
        print_success "已清理Redis缓存 ($CACHE_KEY)"
    else
        print_warning "Redis缓存中无数据 ($CACHE_KEY)"
    fi

    # 清理数据库文章数据
    echo "请手动执行以下SQL清理数据库："
    echo "USE your_database_name;"
    echo "DELETE FROM articles;"
    echo "ALTER TABLE articles AUTO_INCREMENT = 1;"
    echo

    read -p "数据库清理完成后按回车继续..." -r
    echo
}

# 2. 检查缓存状态
check_cache_status() {
    print_step "检查Redis缓存状态"

    CACHE_EXISTS=$($REDIS_CLI EXISTS $CACHE_KEY 2>/dev/null)
    if [ "$CACHE_EXISTS" -eq 1 ]; then
        print_warning "缓存中存在数据 ($CACHE_KEY)"
        CACHE_SIZE=$($REDIS_CLI STRLEN $CACHE_KEY 2>/dev/null)
        echo "缓存数据大小: $CACHE_SIZE 字节"

        TTL=$($REDIS_CLI TTL $CACHE_KEY 2>/dev/null)
        echo "缓存TTL: $TTL 秒"
    else
        print_success "缓存为空 ($CACHE_KEY)"
    fi
    echo
}

# 3. 创建测试数据
create_test_data() {
    print_step "创建测试数据"

    echo "Token验证: ${TOKEN:0:20}..."
    echo "Authorization Header将是: Bearer ${TOKEN:0:20}..."

    # 创建第一篇文章
    echo "创建文章1..."
    RESP1=$(curl -v -X POST $BASE_URL/api/articles \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"Redis测试文章1","content":"这是专门用于Redis缓存测试的文章1","preview":"缓存测试文章1预览"}' 2>&1)
    echo "文章1创建结果: $RESP1"

    # 创建第二篇文章
    echo "创建文章2..."
    RESP2=$(curl -v -X POST $BASE_URL/api/articles \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"Redis测试文章2","content":"这是专门用于Redis缓存测试的文章2","preview":"缓存测试文章2预览"}' 2>&1)
    echo "文章2创建结果: $RESP2"
    echo
}

# 4. 测试首次获取（应该从数据库读取）
test_first_request() {
    print_step "首次获取文章列表（应从数据库读取）"

    # 记录开始时间
    START_TIME=$(date +%s%N)

    # 发送请求
    ARTICLES_RESPONSE=$(curl -s -X GET $BASE_URL/api/articles \
      -H "Authorization: Bearer $TOKEN" \
      -w "HTTP_CODE:%{http_code};TIME_TOTAL:%{time_total};SIZE_DOWNLOAD:%{size_download}")

    # 记录结束时间
    END_TIME=$(date +%s%N)
    DURATION=$((($END_TIME - $START_TIME) / 1000000))

    # 解析响应信息
    HTTP_CODE=$(echo $ARTICLES_RESPONSE | grep -o "HTTP_CODE:[^;]*" | cut -d: -f2)
    TIME_TOTAL=$(echo $ARTICLES_RESPONSE | grep -o "TIME_TOTAL:[^;]*" | cut -d: -f2)
    SIZE_DOWNLOAD=$(echo $ARTICLES_RESPONSE | grep -o "SIZE_DOWNLOAD:[^;]*" | cut -d: -f2)
    BODY=$(echo $ARTICLES_RESPONSE | sed 's/HTTP_CODE:[^;]*;TIME_TOTAL:[^;]*;SIZE_DOWNLOAD:[^;]*//')

    echo "HTTP状态码: $HTTP_CODE"
    echo "请求总时间: ${TIME_TOTAL}秒"
    echo "实际测量时间: ${DURATION}毫秒"
    echo "响应大小: ${SIZE_DOWNLOAD}字节"
    echo "响应数据: $BODY"
    echo
}

# 5. 检查缓存是否生成
check_cache_created() {
    print_step "检查缓存是否生成"

    CACHE_EXISTS=$($REDIS_CLI EXISTS $CACHE_KEY 2>/dev/null)
    if [ "$CACHE_EXISTS" -eq 1 ]; then
        print_success "缓存已创建 ($CACHE_KEY)"

        CACHE_SIZE=$($REDIS_CLI STRLEN $CACHE_KEY 2>/dev/null)
        echo "缓存数据大小: $CACHE_SIZE 字节"

        TTL=$($REDIS_CLI TTL $CACHE_KEY 2>/dev/null)
        echo "缓存TTL: $TTL 秒"

        # 获取缓存数据（截取前100字符）
        CACHE_PREVIEW=$($REDIS_CLI GET $CACHE_KEY 2>/dev/null | head -c 100)
        echo "缓存数据预览: $CACHE_PREVIEW..."
    else
        print_error "缓存未创建"
    fi
    echo
}

# 6. 测试缓存命中
test_cache_hit() {
    print_step "第二次获取文章列表（应从缓存读取）"

    # 连续发送多次请求测试缓存一致性
    for i in {1..3}; do
        echo "第 $i 次请求:"

        # 记录开始时间
        START_TIME=$(date +%s%N)

        # 发送请求
        ARTICLES_RESPONSE=$(curl -s -X GET $BASE_URL/api/articles \
          -H "Authorization: Bearer $TOKEN" \
          -w "HTTP_CODE:%{http_code};TIME_TOTAL:%{time_total};SIZE_DOWNLOAD:%{size_download}")

        # 记录结束时间
        END_TIME=$(date +%s%N)
        DURATION=$((($END_TIME - $START_TIME) / 1000000))

        # 解析响应信息
        HTTP_CODE=$(echo $ARTICLES_RESPONSE | grep -o "HTTP_CODE:[^;]*" | cut -d: -f2)
        TIME_TOTAL=$(echo $ARTICLES_RESPONSE | grep -o "TIME_TOTAL:[^;]*" | cut -d: -f2)

        echo "  HTTP状态码: $HTTP_CODE"
        echo "  请求总时间: ${TIME_TOTAL}秒"
        echo "  实际测量时间: ${DURATION}毫秒"
        echo "  响应状态: $([ "$HTTP_CODE" = "200" ] && echo "✓ 成功" || echo "✗ 失败")"
        echo
    done
}

# 7. 测试缓存失效
test_cache_invalidation() {
    print_step "测试缓存失效（创建新文章）"

    echo "创建新文章以触发缓存失效..."
    RESP_NEW=$(curl -s -X POST $BASE_URL/api/articles \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"触发失效的新文章","content":"这篇文章应该触发缓存失效","preview":"缓存失效测试"}')
    echo "新文章创建结果: $RESP_NEW"

    # 检查缓存是否被删除
    CACHE_EXISTS_AFTER=$($REDIS_CLI EXISTS $CACHE_KEY 2>/dev/null)
    if [ "$CACHE_EXISTS_AFTER" -eq 0 ]; then
        print_success "缓存已被正确删除"
    else
        print_warning "缓存仍然存在"
    fi
    echo
}

# 8. 测试缓存重建
test_cache_rebuild() {
    print_step "测试缓存重建（再次获取数据）"

    # 再次请求数据，应该从数据库读取并重建缓存
    REBUILD_RESPONSE=$(curl -s -X GET $BASE_URL/api/articles \
      -H "Authorization: Bearer $TOKEN" \
      -w "HTTP_CODE:%{http_code};TIME_TOTAL:%{time_total}")

    HTTP_CODE=$(echo $REBUILD_RESPONSE | grep -o "HTTP_CODE:[^;]*" | cut -d: -f2)
    TIME_TOTAL=$(echo $REBUILD_RESPONSE | grep -o "TIME_TOTAL:[^;]*" | cut -d: -f2)

    echo "重建缓存请求状态码: $HTTP_CODE"
    echo "重建缓存请求时间: ${TIME_TOTAL}秒"

    # 检查缓存是否重建
    sleep 1  # 等待一下确保缓存操作完成
    CACHE_EXISTS_REBUILD=$($REDIS_CLI EXISTS $CACHE_KEY 2>/dev/null)
    if [ "$CACHE_EXISTS_REBUILD" -eq 1 ]; then
        print_success "缓存已重建"
    else
        print_error "缓存重建失败"
    fi
    echo
}

# 9. 性能对比测试
performance_comparison() {
    print_step "性能对比测试"

    echo "清空缓存..."
    $REDIS_CLI DEL $CACHE_KEY > /dev/null 2>&1

    echo "数据库查询测试（无缓存）:"
    DB_TIMES=()
    for i in {1..5}; do
        START_TIME=$(date +%s%N)
        curl -s -X GET $BASE_URL/api/articles -H "Authorization: Bearer $TOKEN" > /dev/null
        END_TIME=$(date +%s%N)
        DURATION=$((($END_TIME - $START_TIME) / 1000000))
        DB_TIMES+=($DURATION)
        echo "  第 $i 次: ${DURATION}ms"
    done

    echo "缓存查询测试（有缓存）:"
    CACHE_TIMES=()
    for i in {1..5}; do
        START_TIME=$(date +%s%N)
        curl -s -X GET $BASE_URL/api/articles -H "Authorization: Bearer $TOKEN" > /dev/null
        END_TIME=$(date +%s%N)
        DURATION=$((($END_TIME - $START_TIME) / 1000000))
        CACHE_TIMES+=($DURATION)
        echo "  第 $i 次: ${DURATION}ms"
    done

    # 计算平均值
    DB_AVG=0
    for time in "${DB_TIMES[@]}"; do
        DB_AVG=$((DB_AVG + time))
    done
    DB_AVG=$((DB_AVG / ${#DB_TIMES[@]}))

    CACHE_AVG=0
    for time in "${CACHE_TIMES[@]}"; do
        CACHE_AVG=$((CACHE_AVG + time))
    done
    CACHE_AVG=$((CACHE_AVG / ${#CACHE_TIMES[@]}))

    echo -e "${GREEN}性能统计:${NC}"
    echo "数据库查询平均时间: ${DB_AVG}ms"
    echo "缓存查询平均时间: ${CACHE_AVG}ms"

    if [ $CACHE_AVG -lt $DB_AVG ]; then
        IMPROVEMENT=$((($DB_AVG - $CACHE_AVG) * 100 / $DB_AVG))
        echo -e "${GREEN}缓存性能提升: ${IMPROVATION}%${NC}"
    else
        print_warning "缓存未显示性能提升"
    fi
    echo
}

# 10. 显示Redis信息
show_redis_info() {
    print_step "Redis服务器信息"

    echo "Redis版本:"
    $REDIS_CLI INFO server | grep redis_version

    echo
    echo "内存使用情况:"
    $REDIS_CLI INFO memory | grep used_memory_human

    echo
    echo "连接信息:"
    $REDIS_CLI INFO clients | grep connected_clients

    echo
    echo "缓存键信息:"
    $REDIS_CLI INFO keyspace | grep db
    echo
}

# 检查Docker Redis状态
check_docker_redis() {
    print_step "检查Docker Redis容器状态"

    # 检查Redis容器是否运行
    REDIS_CONTAINER=$(docker ps --filter "publish=6389" --format "table {{.Names}}" | grep -v NAMES)

    if [ -n "$REDIS_CONTAINER" ]; then
        print_success "Redis容器正在运行: $REDIS_CONTAINER"

        # 显示容器信息
        echo "容器详细信息:"
        docker ps --filter "publish=6389" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_warning "未找到运行在6389端口的Redis容器"

        # 查看所有Redis相关的容器（包括停止的）
        echo "所有Redis相关容器:"
        docker ps -a --filter "name=redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

        # 尝试启动Redis容器（如果有停止的）
        STOPPED_CONTAINER=$(docker ps -a --filter "name=redis" --filter "status=exited" --format "{{.Names}}" | head -1)
        if [ -n "$STOPPED_CONTAINER" ]; then
            echo "发现停止的Redis容器: $STOPPED_CONTAINER"
            read -p "是否启动该容器? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker start $STOPPED_CONTAINER
                print_success "Redis容器已启动"
                sleep 3  # 等待容器完全启动
            fi
        fi
    fi
    echo
}

# 主测试流程
main() {
    echo "开始Redis缓存效果专项测试..."
    echo "测试服务器: $BASE_URL"
    echo "缓存键名: $CACHE_KEY"
    echo

    check_docker_redis
    detect_redis_container
    check_redis
    get_token
    clean_environment
    check_cache_status
    create_test_data
    test_first_request
    check_cache_created
    test_cache_hit
    test_cache_invalidation
    test_cache_rebuild
    performance_comparison
    show_redis_info

    print_step "测试完成"
    echo -e "${GREEN}Redis缓存效果测试已完成！${NC}"
    echo
    echo "如需清理测试数据，请执行："
    echo "1. MySQL: DELETE FROM articles; ALTER TABLE articles AUTO_INCREMENT = 1;"
    echo "2. Redis: redis-cli DEL $CACHE_KEY"
}

# 运行主函数
main
```

测试结果：

- main.go日志：请求成功

  ```bash
  $ go run main.go 
  CurrencyExchangeApp
  [GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.
  
  [GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
   - using env:   export GIN_MODE=release
   - using code:  gin.SetMode(gin.ReleaseMode)
  
  [GIN-debug] POST   /api/auth/login           --> gin_demo/controllers.Login (3 handlers)
  [GIN-debug] POST   /api/auth/register        --> gin_demo/controllers.Register (3 handlers)
  [GIN-debug] GET    /api/exchangeRates        --> gin_demo/controllers.GetExchangeRate (3 handlers)
  [GIN-debug] POST   /api/exchangeRates        --> gin_demo/controllers.CreateExchangeRate (4 handlers)
  [GIN-debug] POST   /api/articles             --> gin_demo/controllers.CreateArticle (4 handlers)
  [GIN-debug] GET    /api/articles             --> gin_demo/controllers.GetArticles (4 handlers)
  [GIN-debug] GET    /api/articles/:id         --> gin_demo/controllers.GetArticleByID (4 handlers)
  [GIN-debug] POST   /api/articles/:id/like    --> gin_demo/controllers.LikeArticle (4 handlers)
  [GIN-debug] GET    /api/articles/:id/like    --> gin_demo/controllers.GetArticleLikes (4 handlers)
  Server running on port :3005
  [GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
  Please check https://github.com/gin-gonic/gin/blob/master/docs/doc.md#dont-trust-all-proxies for details.
  [GIN-debug] Listening and serving HTTP on :3005
  [GIN] 2025/11/19 - 13:35:35 | 200 |  1.487311736s |             ::1 | POST     "/api/auth/login"
  [GIN-debug] [WARNING] Headers were already written. Wanted to override status code 200 with 201
  [GIN] 2025/11/19 - 13:35:38 | 200 |   25.719192ms |             ::1 | POST     "/api/articles"
  [GIN-debug] [WARNING] Headers were already written. Wanted to override status code 200 with 201
  [GIN] 2025/11/19 - 13:35:38 | 200 |   21.924054ms |             ::1 | POST     "/api/articles"
  [GIN] 2025/11/19 - 13:35:38 | 200 |    3.576995ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:39 | 200 |     653.251µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:39 | 200 |     757.334µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:39 | 200 |    1.159929ms |             ::1 | GET      "/api/articles"
  [GIN-debug] [WARNING] Headers were already written. Wanted to override status code 200 with 201
  [GIN] 2025/11/19 - 13:35:39 | 200 |    21.07923ms |             ::1 | POST     "/api/articles"
  [GIN] 2025/11/19 - 13:35:39 | 200 |    3.124772ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |    2.731678ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |    1.230361ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |    1.001526ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |     782.183µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |     988.669µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |     921.781µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |    1.095059ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |      948.35µs |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |    1.008747ms |             ::1 | GET      "/api/articles"
  [GIN] 2025/11/19 - 13:35:40 | 200 |     782.758µs |             ::1 | GET      "/api/articles
  ```

- shell脚本运行日志：成功，不过可能因为数据量实在过少，优化效果甚微

  ```bash
  === Redis缓存效果专项测试 ===
  
  开始Redis缓存效果专项测试...
  测试服务器: http://localhost:3005
  缓存键名: articles
  
  === 检查Docker Redis容器状态 ===
  ✓ Redis容器正在运行: redis-gin-demo
  容器详细信息:
  NAMES            STATUS       PORTS
  redis-gin-demo   Up 2 hours   0.0.0.0:6389->6379/tcp, [::]:6389->6379/tcp
  
  === 检测Redis容器 ===
  ✓ 找到Redis容器: redis-gin-demo
    CLI命令: docker exec redis-gin-demo redis-cli
  
  === 检查Redis连接 ===
  测试Redis连接配置:
    容器名称: redis-gin-demo
    CLI命令: docker exec redis-gin-demo redis-cli
  
  Redis PING响应: PONG
  退出代码: 0
  
  ✓ Redis连接正常
  测试基本Redis操作...
  ✓ Redis读写测试通过
  
  === 登录获取Token ===
  登录响应: {"token":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODk3MzUsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.NU2NkWCVqPYyEaVO3Z4KuttwRGIFA01DevVYAlCIacY"}
  ✓ Token获取成功
  原始Token: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleH...
  已移除Bearer前缀
  最终Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3N...
  Token长度: 135
  
  === 清理测试环境 ===
  ⚠ Redis缓存中无数据 (articles)
  请手动执行以下SQL清理数据库：
  USE your_database_name;
  DELETE FROM articles;
  ALTER TABLE articles AUTO_INCREMENT = 1;
  
  数据库清理完成后按回车继续...
  
  === 检查Redis缓存状态 ===
  ✓ 缓存为空 (articles)
  
  === 创建测试数据 ===
  Token验证: eyJhbGciOiJIUzI1NiIs...
  Authorization Header将是: Bearer eyJhbGciOiJIUzI1NiIs...
  创建文章1...
  文章1创建结果: Note: Unnecessary use of -X or --request, POST is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > POST /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Content-Type: application/json
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODk3MzUsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.NU2NkWCVqPYyEaVO3Z4KuttwRGIFA01DevVYAlCIacY
  > Content-Length: 126
  > 
  } [126 bytes data]
  * upload completely sent off: 126 bytes
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:35:38 GMT
  < Content-Length: 280
  < 
  { [280 bytes data]
  100   406  100   280  100   126  10282   4626 --:--:-- --:--:-- --:--:-- 15037
  * Connection #0 to host localhost left intact
  {"message":"Article created successfully"}{"ID":1,"CreatedAt":"2025-11-19T13:35:38.886+08:00","UpdatedAt":"2025-11-19T13:35:38.886+08:00","DeletedAt":null,"Title":"Redis测试文章1","Content":"这是专门用于Redis缓存测试的文章1","Preview":"缓存测试文章1预览"}
  创建文章2...
  文章2创建结果: Note: Unnecessary use of -X or --request, POST is already inferred.
  * Host localhost:3005 was resolved.
  * IPv6: ::1
  * IPv4: 127.0.0.1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
    0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying [::1]:3005...
  * Connected to localhost (::1) port 3005
  > POST /api/articles HTTP/1.1
  > Host: localhost:3005
  > User-Agent: curl/8.9.1
  > Accept: */*
  > Content-Type: application/json
  > Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjM3ODk3MzUsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.NU2NkWCVqPYyEaVO3Z4KuttwRGIFA01DevVYAlCIacY
  > Content-Length: 126
  > 
  } [126 bytes data]
  * upload completely sent off: 126 bytes
  < HTTP/1.1 200 OK
  < Content-Type: application/json; charset=utf-8
  < Date: Wed, 19 Nov 2025 05:35:38 GMT
  < Content-Length: 280
  < 
  { [280 bytes data]
  100   406  100   280  100   126  12187   5484 --:--:-- --:--:-- --:--:-- 18454
  * Connection #0 to host localhost left intact
  {"message":"Article created successfully"}{"ID":2,"CreatedAt":"2025-11-19T13:35:38.917+08:00","UpdatedAt":"2025-11-19T13:35:38.917+08:00","DeletedAt":null,"Title":"Redis测试文章2","Content":"这是专门用于Redis缓存测试的文章2","Preview":"缓存测试文章2预览"}
  
  === 首次获取文章列表（应从数据库读取） ===
  HTTP状态码: 200
  请求总时间: 0.004434秒
  实际测量时间: 15毫秒
  响应大小: 479字节
  响应数据: [{"ID":1,"CreatedAt":"2025-11-19T13:35:38.886+08:00","UpdatedAt":"2025-11-19T13:35:38.886+08:00","DeletedAt":null,"Title":"Redis测试文章1","Content":"这是专门用于Redis缓存测试的文章1","Preview":"缓存测试文章1预览"},{"ID":2,"CreatedAt":"2025-11-19T13:35:38.917+08:00","UpdatedAt":"2025-11-19T13:35:38.917+08:00","DeletedAt":null,"Title":"Redis测试文章2","Content":"这是专门用于Redis缓存测试的文章2","Preview":"缓存测试文章2预览"}]
  
  === 检查缓存是否生成 ===
  ✓ 缓存已创建 (articles)
  缓存数据大小: 479 字节
  缓存TTL: 600 秒
  缓存数据预览: [{"ID":1,"CreatedAt":"2025-11-19T13:35:38.886+08:00","UpdatedAt":"2025-11-19T13:35:38.886+08:00","De...
  
  === 第二次获取文章列表（应从缓存读取） ===
  第 1 次请求:
    HTTP状态码: 200
    请求总时间: 0.001231秒
    实际测量时间: 8毫秒
    响应状态: ✓ 成功
  
  第 2 次请求:
    HTTP状态码: 200
    请求总时间: 0.001134秒
    实际测量时间: 7毫秒
    响应状态: ✓ 成功
  
  第 3 次请求:
    HTTP状态码: 200
    请求总时间: 0.001999秒
    实际测量时间: 10毫秒
    响应状态: ✓ 成功
  
  === 测试缓存失效（创建新文章） ===
  创建新文章以触发缓存失效...
  新文章创建结果: {"message":"Article created successfully"}{"ID":3,"CreatedAt":"2025-11-19T13:35:39.411+08:00","UpdatedAt":"2025-11-19T13:35:39.411+08:00","DeletedAt":null,"Title":"触发失效的新文章","Content":"这篇文章应该触发缓存失效","Preview":"缓存失效测试"}
  ✓ 缓存已被正确删除
  
  === 测试缓存重建（再次获取数据） ===
  重建缓存请求状态码: 200
  重建缓存请求时间: 0.003900秒
  ✓ 缓存已重建
  
  === 性能对比测试 ===
  清空缓存...
  数据库查询测试（无缓存）:
    第 1 次: 10ms
    第 2 次: 8ms
    第 3 次: 8ms
    第 4 次: 8ms
    第 5 次: 7ms
  缓存查询测试（有缓存）:
    第 1 次: 7ms
    第 2 次: 7ms
    第 3 次: 8ms
    第 4 次: 7ms
    第 5 次: 7ms
  性能统计:
  数据库查询平均时间: 8ms
  缓存查询平均时间: 7ms
  缓存性能提升: %
  
  === Redis服务器信息 ===
  Redis版本:
  redis_version:8.2.3
  
  内存使用情况:
  used_memory_human:1.18M
  
  连接信息:
  connected_clients:3
  
  缓存键信息:
  db0:keys=2,expires=1,avg_ttl=599858,subexpiry=0
  
  === 测试完成 ===
  Redis缓存效果测试已完成！
  
  如需清理测试数据，请执行：
  1. MySQL: DELETE FROM articles; ALTER TABLE articles AUTO_INCREMENT = 1;
  2. Redis: redis-cli DEL articles
  ```

- 查看数据库验证效果，并清理数据：注意`redis-cli`后加入`--raw`，应对输出乱码问题

  ```bash
  mysql> SELECT * FROM articles;
  +----+-------------------------+-------------------------+------------+------------+---------------------+-----------+
  | id | created_at              | updated_at              | deleted_at | title      | content             | preview   |
  +----+-------------------------+-------------------------+------------+------------+---------------------+-----------+
  |  1 | 2025-11-19 13:35:38.886 | 2025-11-19 13:35:38.886 | NULL       | Redis????1 | ??????Redis???????1 | ??????1?? |
  |  2 | 2025-11-19 13:35:38.917 | 2025-11-19 13:35:38.917 | NULL       | Redis????2 | ??????Redis???????2 | ??????2?? |
  |  3 | 2025-11-19 13:35:39.411 | 2025-11-19 13:35:39.411 | NULL       | ????????   | ????????????        | ??????    |
  +----+-------------------------+-------------------------+------------+------------+---------------------+-----------+
  3 rows in set (0.00 sec)
  
  mysql> DELETE FROM articles;
  Query OK, 3 rows affected (0.00 sec)
  
  mysql> ALTER TABLE articles AUTO_INCREMENT = 1;
  Query OK, 0 rows affected (0.02 sec)
  Records: 0  Duplicates: 0  Warnings: 0
  ```

  ```bash
  root@dbe982e0f447:/data# redis-cli --raw
  127.0.0.1:6379> KEYS *
  name
  articles
  127.0.0.1:6379> TYPE articles
  string
  127.0.0.1:6379> GET articles
  [{"ID":1,"CreatedAt":"2025-11-19T13:35:38.886+08:00","UpdatedAt":"2025-11-19T13:35:38.886+08:00","DeletedAt":null,"Title":"Redis测试文章1","Content":"这是专门用于Redis缓存测试的文章1","Preview":"缓存测试文章1预览"},{"ID":2,"CreatedAt":"2025-11-19T13:35:38.917+08:00","UpdatedAt":"2025-11-19T13:35:38.917+08:00","DeletedAt":null,"Title":"Redis测试文章2","Content":"这是专门用于Redis缓存测试的文章2","Preview":"缓存测试文章2预览"},{"ID":3,"CreatedAt":"2025-11-19T13:35:39.411+08:00","UpdatedAt":"2025-11-19T13:35:39.411+08:00","DeletedAt":null,"Title":"触发失效的新文章","Content":"这篇文章应该触发缓存失效","Preview":"缓存失效测试"}]
  127.0.0.1:6379> DEL articles
  1
  127.0.0.1:6379> KEYS *
  name
  ```



当前目录结构：

```bash
.
├── config
│   ├── config.go
│   ├── config.yml
│   ├── db.go
│   └── redis.go
├── controllers
│   ├── article_controller.go
│   ├── auth_controllers.go
│   ├── exchange_rate_controller.go
│   └── like_controller.go
├── global
│   └── global.go
├── go.mod
├── go.sum
├── main.go
├── middlewares
│   └── auth_middleware.go
├── models
│   ├── article.go
│   ├── exchange_rate.go
│   └── user.go
├── router
│   └── router.go
├── test_article.sh
├── test_exchange_rate.sh
├── test_redis.sh
└── utils
    └── utils.go

8 directories, 21 files
```

至此，后端部分结束，且测试结束🌹🌹🌹



## 07 前端部分

配置前端：

- 先拉取[原项目github前端基础代码](https://github.com/Slumhee/Web003Gin-01_gingormtutorials/tree/main/Exchangeapp_frontend)，由于这是个前后端分离项目，所以如果不考究规范，前端代码的位置没那么多要求
- 安装依赖（虽然出现了些 弃用警告`npm warn deprecated `和 安全漏洞`vulnerabilities` ，好在安装陈工了）：`npm i`
- 启动前端：`npm run dev -- --host`，如下图所示
  <img src="./assets/image-20251119140756740.png" alt="image-20251119140756740" style="zoom: 25%;" />

之后再结合后端，逐步解决问题。



### 1、查看汇率时，出现了CORS问题

> 注意：前端程序中默认使用3000端口对接后端，如果修改了后端服务的端口，注意更正

按道理，无需登录即可查看有哪些货币，但是实际上出现了如下问题：

![image-20251119141934774](./assets/image-20251119141934774.png)

前端代码是没有问题的，核心在于需要后端去允许CORS：设置 Gin CORS 中间件

- 安装依赖：`go get github.com/gin-contrib/cors`

- 修改router.go：需要将相关设置写在路由之前，也就是在`r := gin.Default()`之后加上`r.Use(cors.New(cors.Config`相关内容即可

  ```go
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
  ```

- 备注：

  - 由于当前项目运行在服务器上，我是通过ssh启动项目并访问该服务的，所以`AllowOrigins`中即便加入了`"http://localhost:5173"`等信息，在ssh中使用curl是可以的，但是在宿主机上浏览器访问该前端依旧会会存在CORS问题，这里图省事，直接使用通配符，即`[]string{"*"}`即可
  - 这里`AllowOriginFunc`没必要设置

测试：CORS问题已解决

![image-20251119145019337](./assets/image-20251119145019337.png)



### 2、优雅的退出我们的应用

在ctrl + c关闭后端时，出现`^Csignal: interrupt`（或者类似`exit status 0xc000013a`），不够优雅。

在解决这个问题前，需要先了解Go语言的Channel与Deadlock相关知识：

- Channel：略
- Deadlock：略
- （补充）WaitGroup Context：略



Gin官方文档关闭案例：[优雅地重启或停止](https://gin-gonic.com/zh-cn/docs/examples/graceful-restart-or-stop/)

在main.go中：

- 原代码：

  ```go
  package main
  
  import (
  	"fmt"
  	"gin_demo/config"
  	"gin_demo/router"
  )
  
  func main() {
  	// 读取配置信息
  	config.InitConfig()
  	fmt.Println(config.AppConfig.App.Name)
  
  	router := router.InitRouter()
  
  	port := config.AppConfig.App.Port
  	if port == "" {
  		port = "8080"
  	}
  	fmt.Println("Server running on port", port)
  
  	// 启动服务
  	router.Run(port)
  }
  
  ```

- 修改后：

  ```go
  package main
  
  import (
  	"context"
  	"log"
  	"net/http"
  	"os"
  	"os/signal"
  	"time"
  
  	"gin_demo/config"
  	"gin_demo/router"
  )
  
  func main() {
  	config.InitConfig()
  
  	r := router.InitRouter()
  
  	port := config.AppConfig.App.Port
  
  	if port == "" {
  		port = ":8080"
  	}
  
  	srv := &http.Server{
  		Addr:    port,
  		Handler: r,
  	}
  
  	go func() {
  		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
  			log.Fatalf("listen: %s\n", err)
  		}
  	}()
  
  	quit := make(chan os.Signal, 1)
  	signal.Notify(quit, os.Interrupt)
  	<-quit
  	log.Println("Shutdown Server ...")
  
  	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
  	defer cancel()
  	if err := srv.Shutdown(ctx); err != nil {
  		log.Fatal("Server Shutdown:", err)
  	}
  	log.Println("Server exiting")
  
  }
  
  ```

  

测试：ctrl + c 时就可以优雅的退出了

```bash
[GIN] 2025/11/19 - 14:57:19 | 200 |   15.039326ms |       127.0.0.1 | GET      "/api/exchangeRates"
^C2025/11/19 14:57:22 Shutdown Server ...
2025/11/19 14:57:22 Server exiting
```



### 3、应用最终效果

1）测试兑换货币功能：

![image-20251119150045008](./assets/image-20251119150045008.png)

符合我们之前在数据库中设置的汇率：

```bash
mysql> SELECT * FROM exchange_rates;
+----+---------------+-------------+------+-------------------------+
| id | from_currency | to_currency | rate | date                    |
+----+---------------+-------------+------+-------------------------+
| 10 | EUR           | USD         |  1.1 | 2025-11-18 16:07:58.699 |
+----+---------------+-------------+------+-------------------------+
1 row in set (0.00 sec)
```

备注：由于数据库里只写了`EUR→USD`   的汇率，且没有加入更多的逻辑，所以如果前端反着写的话（`USD→EUR` ），是没有结果的。



2）登录前部分功能是无法使用的：

![image-20251119140934289](./assets/image-20251119140934289.png)



3）用错误账号登录：

![image-20251119150226775](./assets/image-20251119150226775.png)



4）注册账号：正常注册并跳转

![image-20251119150306228](./assets/image-20251119150306228.png)

检查数据库：已正常注册

```bash
mysql> SELECT * FROM users;
+----+-------------------------+-------------------------+------------+------------+--------------------------------------------------------------+
| id | created_at              | updated_at              | deleted_at | username   | password                                                     |
+----+-------------------------+-------------------------+------------+------------+--------------------------------------------------------------+
|  1 | 2025-11-18 14:06:44.867 | 2025-11-18 14:06:44.867 | NULL       | testuser   | $2a$14$h/V2PZ8kOdM2pwmsHpBe6u1dT.TtK73EtHkTDE1z9AYdF8aFvb8fq |
|  2 | 2025-11-19 15:03:05.083 | 2025-11-19 15:03:05.083 | NULL       | test_user2 | $2a$14$Y9IU.vFdDXsEKakgeGJJQOQelScpHproOIURA6kn9hBUONwEUnq6W |
+----+-------------------------+-------------------------+------------+------------+--------------------------------------------------------------+
2 rows in set (0.00 sec)
```



5）查看新闻：记得提前插入些新闻

![image-20251119150650719](./assets/image-20251119150650719.png)

🌹🌹🌹完结撒花🌹🌹🌹
