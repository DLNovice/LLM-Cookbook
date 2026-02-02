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
