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