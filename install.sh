#!/bin/bash

# 安装脚本 - 配置代理并安装依赖

set -e

echo "=== FastMCP Demo 安装脚本 ==="

# 1. 清除可能的全局代理设置
echo "清除全局代理设置..."
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true

# 2. 设置正确的代理
PROXY_URL="http://squid.corp.redhat.com:3128"
echo "设置代理: $PROXY_URL"

export http_proxy=$PROXY_URL
export https_proxy=$PROXY_URL
export HTTP_PROXY=$PROXY_URL
export HTTPS_PROXY=$PROXY_URL
export no_proxy="localhost,127.0.0.1"
export NO_PROXY="localhost,127.0.0.1"

# 3. 配置 pip 代理
echo "配置 pip 代理..."
pip config set global.proxy "$PROXY_URL"
pip config set global.trusted-host "pypi.org files.pythonhosted.org"

# 4. 安装 uv
echo "安装 uv..."
pip install --no-cache-dir uv

# 5. 使用 uv 安装项目依赖
echo "安装项目依赖..."
uv pip install --system --no-cache -r requirements.txt

echo "=== 安装完成 ==="
