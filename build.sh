#!/bin/bash

# FastMCP Demo 构建脚本
# 支持环境变量配置代理

set -e

echo "=== FastMCP Demo 构建脚本 ==="

# 检查是否存在 .env 文件
if [ -f ".env" ]; then
    echo "加载 .env 文件..."
    source .env
elif [ -f "env.example" ]; then
    echo "未找到 .env 文件，请参考 env.example 创建配置文件"
    echo "或者直接设置环境变量："
    echo "  export HTTP_PROXY=http://your-proxy:port"
    echo "  export HTTPS_PROXY=http://your-proxy:port"
    echo "  export PROXY_URL=http://your-proxy:port"
fi

# 统一代理配置（兼容大小写环境变量）
if [ -z "$HTTP_PROXY" ] && [ -n "$http_proxy" ]; then
    export HTTP_PROXY="$http_proxy"
fi
if [ -z "$HTTPS_PROXY" ] && [ -n "$https_proxy" ]; then
    export HTTPS_PROXY="$https_proxy"
fi
# 如果设置了HTTP_PROXY但没有设置PROXY_URL，使用HTTP_PROXY作为PROXY_URL
if [ -z "$PROXY_URL" ] && [ -n "$HTTP_PROXY" ]; then
    export PROXY_URL="$HTTP_PROXY"
fi

# 准备构建代理（容器内使用，不传递给Docker daemon）
BUILD_PROXY=""
if [ -n "$PROXY_URL" ]; then
    BUILD_PROXY="$PROXY_URL"
elif [ -n "$HTTP_PROXY" ]; then
    BUILD_PROXY="$HTTP_PROXY"
elif [ -n "$http_proxy" ]; then
    BUILD_PROXY="$http_proxy"
fi

# 构建 Docker 镜像
echo "构建 Docker 镜像..."
if [ -n "$BUILD_PROXY" ]; then
    echo "容器内将使用代理: $BUILD_PROXY"
    echo "注意: Docker daemon拉取基础镜像时不使用此代理"
    echo "      如果拉取失败，请在Docker Desktop中配置代理"
    echo ""
    # 清除可能影响Docker daemon的代理环境变量
    unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy PROXY_URL
    export BUILD_PROXY
    docker-compose build
else
    echo "无代理配置，直接构建..."
    # 清除可能影响Docker daemon的代理环境变量
    unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy PROXY_URL BUILD_PROXY
    docker-compose build
fi

echo "=== 构建完成 ==="
echo "运行服务: docker-compose up"
