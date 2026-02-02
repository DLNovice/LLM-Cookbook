#!/bin/bash
# MCP 集成测试脚本

echo "🧪 MCP Integration Test Suite"
echo "=============================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_api() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4

    echo -n "Testing: $name ... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\n%{http_code}")
    else
        response=$(curl -s "$url" -w "\n%{http_code}")
    fi

    http_code=$(echo "$response" | tail -n 1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
        ((FAILED++))
    fi
}

echo "Step 1: Testing MCP Server"
echo "----------------------------"
test_api "MCP Server Health" "http://localhost:8006/mcp_demo" "POST" '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}'

echo ""
echo "Step 2: Testing Agent Service"
echo "----------------------------"
test_api "Agent Health Check" "http://localhost:8000/health" "GET" ""
test_api "Agent Root Endpoint" "http://localhost:8000/" "GET" ""

echo ""
echo "Step 3: Testing MCP Tool Calls"
echo "----------------------------"

# 测试 add 工具
test_api "MCP Tool: add(5, 3)" "http://localhost:8000/agent/chat" "POST" '{
    "message": "请使用 add 工具帮我计算 5 + 3",
    "session_id": "test_add"
}'

# 测试 get_weather 工具
test_api "MCP Tool: get_weather" "http://localhost:8000/agent/chat" "POST" '{
    "message": "使用 get_weather 工具查询 New York 的天气",
    "session_id": "test_weather"
}'

echo ""
echo "Step 4: Testing Backend Service"
echo "----------------------------"
test_api "Backend Health Check" "http://localhost:8080/api/health" "GET" ""
test_api "Backend Root Endpoint" "http://localhost:8080/" "GET" ""

echo ""
echo "=============================="
echo "Test Results"
echo "=============================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the services.${NC}"
    exit 1
fi
