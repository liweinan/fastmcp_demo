#!/bin/bash

# Installation script - Configure proxy and install dependencies

set -e

echo "=== FastMCP Demo Installation Script ==="

# 1. Clear possible global proxy settings
echo "Clearing global proxy settings..."
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true

# 2. Set proxy (read from environment variable, skip if not set)
if [ -n "$PROXY_URL" ]; then
    echo "Setting proxy: $PROXY_URL"
    export http_proxy=$PROXY_URL
    export https_proxy=$PROXY_URL
    export HTTP_PROXY=$PROXY_URL
    export HTTPS_PROXY=$PROXY_URL
    
    # Configure pip proxy
    echo "Configuring pip proxy..."
    pip config set global.proxy "$PROXY_URL"
    pip config set global.trusted-host "pypi.org files.pythonhosted.org"
else
    echo "PROXY_URL environment variable not set, skipping proxy configuration"
fi

# 3. Set no_proxy (optional)
if [ -n "$NO_PROXY" ]; then
    export no_proxy=$NO_PROXY
    export NO_PROXY=$NO_PROXY
else
    export no_proxy="localhost,127.0.0.1"
    export NO_PROXY="localhost,127.0.0.1"
fi

# 4. Install uv
echo "Installing uv..."
pip install --no-cache-dir uv

# 5. Use uv sync to install project dependencies (using pyproject.toml)
echo "Installing project dependencies..."
uv sync

echo "=== Installation Complete ==="
