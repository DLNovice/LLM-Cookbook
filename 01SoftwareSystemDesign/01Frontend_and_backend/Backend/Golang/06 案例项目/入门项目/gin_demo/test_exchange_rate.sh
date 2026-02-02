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