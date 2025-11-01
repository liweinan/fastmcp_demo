#!/bin/bash

# 安装脚本 - 配置代理并安装依赖

set -e

echo "=== FastMCP Demo 安装脚本 ==="

# 1. 清除可能的全局代理设置
echo "清除全局代理设置..."
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true

# 2. 设置代理（从环境变量读取，如果没有则跳过）
if [ -n "$PROXY_URL" ]; then
    echo "设置代理: $PROXY_URL"
    export http_proxy=$PROXY_URL
    export https_proxy=$PROXY_URL
    export HTTP_PROXY=$PROXY_URL
    export HTTPS_PROXY=$PROXY_URL
    
    # 配置 pip 代理
    echo "配置 pip 代理..."
    pip config set global.proxy "$PROXY_URL"
    pip config set global.trusted-host "pypi.org files.pythonhosted.org"
else
    echo "未设置 PROXY_URL 环境变量，跳过代理配置"
fi

# 3. 设置 no_proxy（可选）
if [ -n "$NO_PROXY" ]; then
    export no_proxy=$NO_PROXY
    export NO_PROXY=$NO_PROXY
else
    export no_proxy="localhost,127.0.0.1"
    export NO_PROXY="localhost,127.0.0.1"
fi

# 4. 安装 uv
echo "安装 uv..."
pip install --no-cache-dir uv

# 5. 使用 uv sync 安装项目依赖（使用 pyproject.toml）
echo "安装项目依赖..."
uv sync

echo "=== 安装完成 ==="
