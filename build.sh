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
    echo "  export PROXY_URL=http://your-proxy:port"
    echo "  export HTTP_PROXY=http://your-proxy:port"
    echo "  export HTTPS_PROXY=http://your-proxy:port"
fi

# 构建参数
BUILD_ARGS=""

# 添加代理参数（如果设置了）
if [ -n "$PROXY_URL" ]; then
    echo "使用代理: $PROXY_URL"
    BUILD_ARGS="$BUILD_ARGS --build-arg proxy_url=$PROXY_URL"
fi

if [ -n "$HTTP_PROXY" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg http_proxy=$HTTP_PROXY"
fi

if [ -n "$HTTPS_PROXY" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg https_proxy=$HTTPS_PROXY"
fi

if [ -n "$NO_PROXY" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg no_proxy=$NO_PROXY"
fi

# 构建 Docker 镜像
echo "构建 Docker 镜像..."
if [ -n "$BUILD_ARGS" ]; then
    echo "构建参数: $BUILD_ARGS"
    docker-compose build $BUILD_ARGS
else
    echo "无代理配置，直接构建..."
    docker-compose build
fi

echo "=== 构建完成 ==="
echo "运行服务: docker-compose up"
