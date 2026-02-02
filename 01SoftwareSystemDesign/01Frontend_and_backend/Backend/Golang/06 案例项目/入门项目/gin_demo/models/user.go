package models

import "gorm.io/gorm"

type User struct {
	gorm.Model
	// gorm:"unique"：这是GORM框架的标签声明，表示这个字段在数据库中需要唯一约束
	Username string `gorm:"unique"`
	Password string
}
