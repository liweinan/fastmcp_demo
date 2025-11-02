#!/bin/bash

# FastMCP Demo 构建脚本
# 支持环境变量配置代理，与 Dockerfile 和 docker-compose.yml 配合使用
#
# 使用方法：
#   1. 设置代理环境变量（优先级：BUILD_PROXY > PROXY_URL > HTTP_PROXY > http_proxy）
#   2. 运行: ./build.sh
#
# 或者创建 .env 文件（参考 env.example）

set -e

echo "=== FastMCP Demo 构建脚本 ==="
echo ""

# 检查是否存在 .env 文件
if [ -f ".env" ]; then
    echo "✓ 加载 .env 文件..."
    # 使用 source 但避免覆盖已设置的环境变量
    set -a
    source .env
    set +a
elif [ -f "env.example" ]; then
    echo "⚠ 未找到 .env 文件，请参考 env.example 创建配置文件"
    echo "   或者直接设置环境变量："
    echo "     export BUILD_PROXY=http://your-proxy:port"
    echo "     export PROXY_URL=http://your-proxy:port"
    echo "     export HTTP_PROXY=http://your-proxy:port"
fi

echo ""

# 代理配置优先级：
# 1. BUILD_PROXY（直接传递给 Docker，Dockerfile 会自动处理 localhost -> host.docker.internal）
# 2. PROXY_URL
# 3. HTTP_PROXY
# 4. http_proxy

# 统一代理配置（兼容大小写环境变量）
if [ -z "$HTTP_PROXY" ] && [ -n "$http_proxy" ]; then
    export HTTP_PROXY="$http_proxy"
fi
if [ -z "$HTTPS_PROXY" ] && [ -n "$https_proxy" ]; then
    export HTTPS_PROXY="$https_proxy"
fi

# 如果用户已经设置了 BUILD_PROXY，直接使用（最高优先级）
if [ -n "$BUILD_PROXY" ]; then
    echo "✓ 检测到 BUILD_PROXY 环境变量: $BUILD_PROXY"
    FINAL_BUILD_PROXY="$BUILD_PROXY"
else
    # 从其他环境变量推导 BUILD_PROXY
    if [ -n "$PROXY_URL" ]; then
        echo "✓ 检测到 PROXY_URL 环境变量: $PROXY_URL"
        FINAL_BUILD_PROXY="$PROXY_URL"
    elif [ -n "$HTTP_PROXY" ]; then
        echo "✓ 检测到 HTTP_PROXY 环境变量: $HTTP_PROXY"
        FINAL_BUILD_PROXY="$HTTP_PROXY"
    elif [ -n "$http_proxy" ]; then
        echo "✓ 检测到 http_proxy 环境变量: $http_proxy"
        FINAL_BUILD_PROXY="$http_proxy"
    else
        echo "⚠ 未检测到任何代理配置"
        FINAL_BUILD_PROXY=""
    fi
fi

# 显示最终使用的代理配置
echo ""
if [ -n "$FINAL_BUILD_PROXY" ]; then
    # 检查是否包含 localhost，提示用户 Dockerfile 会自动转换
    if echo "$FINAL_BUILD_PROXY" | grep -q "localhost"; then
        EXPECTED_PROXY=$(echo "$FINAL_BUILD_PROXY" | sed 's|localhost|host.docker.internal|g')
        echo "=== 代理配置 ==="
        echo "原始代理地址: $FINAL_BUILD_PROXY"
        echo "容器内将使用: $EXPECTED_PROXY (Dockerfile 会自动转换 localhost -> host.docker.internal)"
        echo ""
        echo "代理将应用于："
        echo "  - apt-get 包管理器（Debian 仓库）"
        echo "  - uv 下载和安装"
        echo "  - Python 下载和安装"
        echo "  - pip/uv sync 依赖安装"
        echo ""
        echo "注意: Docker daemon 拉取基础镜像时不使用此代理"
        echo "      如果基础镜像拉取失败，请在 Docker Desktop 中配置代理"
        echo ""
    else
        echo "=== 代理配置 ==="
        echo "容器内将使用代理: $FINAL_BUILD_PROXY"
        echo ""
        echo "代理将应用于："
        echo "  - apt-get 包管理器（Debian 仓库）"
        echo "  - uv 下载和安装"
        echo "  - Python 下载和安装"
        echo "  - pip/uv sync 依赖安装"
        echo ""
    fi
else
    echo "=== 代理配置 ==="
    echo "⚠ 无代理配置，将直接连接（可能失败，取决于网络环境）"
    echo ""
fi

# 设置 BUILD_PROXY 环境变量，供 docker-compose.yml 使用
# docker-compose.yml 使用 ${BUILD_PROXY:-} 语法读取此变量
export BUILD_PROXY="$FINAL_BUILD_PROXY"

# 清除可能影响 Docker daemon 的其他代理环境变量
# 这些变量会影响 Docker daemon 本身，但我们只需要在容器内使用代理
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy PROXY_URL

# 构建 Docker 镜像
echo "开始构建 Docker 镜像..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 运行 docker-compose build
# docker-compose 会读取 BUILD_PROXY 环境变量并传递给 Dockerfile 的 ARG BUILD_PROXY
docker-compose build

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "=== 构建完成 ==="
echo ""
echo "提示："
echo "  - 运行服务: docker-compose up"
echo "  - 后台运行: docker-compose up -d"
echo "  - 查看日志: docker-compose logs -f"
echo ""
