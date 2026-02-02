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
