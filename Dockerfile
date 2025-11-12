# Multi-stage build: First stage uses lightweight base image + uv manages Python
# Uses debian:bookworm-slim as base, uv automatically manages Python environment
FROM debian:bookworm-slim AS builder

# Configure apt proxy (if host has proxy)
# Note: Only replace localhost, other proxy addresses (like squid.corp.redhat.com) remain unchanged
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        if echo "$BUILD_PROXY" | grep -q "localhost"; then \
            BUILD_PROXY_CONVERTED=$(echo "$BUILD_PROXY" | sed 's|localhost|host.docker.internal|g'); \
        else \
            BUILD_PROXY_CONVERTED="$BUILD_PROXY"; \
        fi && \
        echo "Configuring apt proxy: $BUILD_PROXY_CONVERTED" && \
        echo "Acquire::http::Proxy \"$BUILD_PROXY_CONVERTED\";" > /etc/apt/apt.conf.d/01proxy && \
        echo "Acquire::https::Proxy \"$BUILD_PROXY_CONVERTED\";" >> /etc/apt/apt.conf.d/01proxy; \
    fi

# Configure apt retry and timeout (independent layer, cacheable)
RUN echo 'Acquire::Retries "10";' >> /etc/apt/apt.conf.d/99-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout

# Update package list (independent layer, cacheable)
RUN apt-get update

# Install base tools and build tools (independent layer, cacheable)
RUN apt-get install -y --no-install-recommends --fix-missing \
    ca-certificates \
    curl \
    build-essential \
    cmake

# Clean apt cache (independent layer, cacheable)
RUN rm -rf /var/lib/apt/lists/*

# Copy proxy setup helper script
COPY docker-set-proxy.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-set-proxy.sh

# Install uv (independent layer, cacheable)
# uv installed to /root/.local/bin, only re-download when proxy config or uv version changes
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        echo "Downloading uv with proxy: $BUILD_PROXY_CONVERTED" && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED" && \
        curl --proxy "$BUILD_PROXY_CONVERTED" -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && \
        sh /tmp/uv-install.sh && \
        rm -f /tmp/uv-install.sh; \
    else \
        echo "Downloading uv without proxy"; \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && \
        sh /tmp/uv-install.sh && \
        rm -f /tmp/uv-install.sh; \
    fi

# Verify uv installation (independent layer, cacheable)
RUN export PATH="/root/.local/bin:$PATH" && \
    /root/.local/bin/uv --version

# Copy project files (copy config file first, convenient for uv sync)
WORKDIR /app
COPY pyproject.toml ./

# Install Python (independent layer, cacheable)
# uv automatically downloads and manages Python 3.11, Python cached in /root/.local/share/uv/python/
ARG BUILD_PROXY
RUN export PATH="/root/.local/bin:$PATH" && \
    if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED"; \
    fi && \
    echo "Installing Python 3.11 with uv..." && \
    uv python install 3.11 && \
    uv python list

# Use uv sync to create virtual environment and install dependencies (independent layer, only re-execute when dependencies change)
ARG BUILD_PROXY
RUN export PATH="/root/.local/bin:$PATH" && \
    if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED" && \
        echo "Configured uv proxy: $BUILD_PROXY_CONVERTED"; \
    fi && \
    echo "=== Installing dependencies with uv sync (build stage, requires build tools) ===" && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        echo "Detected ARM architecture, setting compilation options..." && \
        export CMAKE_ARGS="-DGGML_NATIVE=OFF -DCMAKE_C_FLAGS='-march=armv8-a' -DCMAKE_CXX_FLAGS='-march=armv8-a'" && \
        export GGML_NATIVE=OFF; \
    else \
        echo "Detected architecture: $ARCH, using default compilation options"; \
    fi && \
    uv sync --verbose && \
    echo "=== uv sync completed ===" && \
    # Verify virtual environment and dependencies
    ls -la /app/.venv/bin/ | head -10 && \
    /app/.venv/bin/python --version && \
    /app/.venv/bin/pip list | head -20

# Final stage: Only copy uv, Python and virtual environment, exclude build tools
FROM debian:bookworm-slim

# Configure apt proxy (if host has proxy)
# Note: Only replace localhost, other proxy addresses (like squid.corp.redhat.com) remain unchanged
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        if echo "$BUILD_PROXY" | grep -q "localhost"; then \
            BUILD_PROXY_CONVERTED=$(echo "$BUILD_PROXY" | sed 's|localhost|host.docker.internal|g'); \
        else \
            BUILD_PROXY_CONVERTED="$BUILD_PROXY"; \
        fi && \
        echo "Configuring apt proxy: $BUILD_PROXY_CONVERTED" && \
        echo "Acquire::http::Proxy \"$BUILD_PROXY_CONVERTED\";" > /etc/apt/apt.conf.d/01proxy && \
        echo "Acquire::https::Proxy \"$BUILD_PROXY_CONVERTED\";" >> /etc/apt/apt.conf.d/01proxy; \
    fi

# Configure apt retry and timeout (consistent with builder stage)
RUN echo 'Acquire::Retries "10";' >> /etc/apt/apt.conf.d/99-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout

# Update apt package list (independent layer, cacheable)
# Note: Separate apt-get update, only re-execute when proxy config changes
RUN apt-get update

# Copy uv, Python and virtual environment from builder stage
# uv installed at /root/.local/bin/uv
# uv-managed Python at /root/.local/share/uv/python/
# Virtual environment at /app/.venv/ (contains all installed dependencies)
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/.venv /app/.venv

# Install runtime dependencies (independent layer, cacheable)
# Note: Build tools (build-essential, cmake) only needed in builder stage
# Final stage only needs runtime libraries:
#   - libgcc-s1 (C++ runtime)
#   - libstdc++6 (standard C++ library)
#   - libgomp1 (OpenMP runtime, required by llama-cpp-python)
# Use retry mechanism to handle network issues
RUN (apt-get install -y --no-install-recommends \
        ca-certificates \
        libgcc-s1 \
        libstdc++6 \
        libgomp1 || \
     (echo "First installation failed, retrying..." && \
      apt-get update && \
      apt-get install -y --no-install-recommends --fix-missing \
          ca-certificates \
          libgcc-s1 \
          libstdc++6 \
          libgomp1)) && \
    rm -rf /var/lib/apt/lists/* && \
    echo "Runtime dependencies installed (runtime libraries only, no build tools)"

# Set PATH: Ensure uv and Python in virtual environment are available
ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"

# Verify uv, Python and virtual environment are correctly copied, and fix Python links
RUN /root/.local/bin/uv --version && \
    /root/.local/bin/uv python list && \
    if [ -d "/app/.venv" ]; then \
        echo "Checking virtual environment..." && \
        # Find uv-managed Python interpreter path
        PYTHON_PATH=$(/root/.local/bin/uv python list | grep "3.11" | head -1 | awk '{print $NF}' || echo "") && \
        if [ -n "$PYTHON_PATH" ] && [ -f "$PYTHON_PATH/bin/python3" ]; then \
            echo "Found Python interpreter: $PYTHON_PATH/bin/python3" && \
            # Fix Python links in virtual environment
            if [ -f "/app/.venv/bin/python3" ]; then \
                rm -f /app/.venv/bin/python3 && \
                ln -sf "$PYTHON_PATH/bin/python3" /app/.venv/bin/python3 && \
                rm -f /app/.venv/bin/python && \
                ln -sf python3 /app/.venv/bin/python && \
                echo "Fixed Python links"; \
            fi && \
            # Verify fixed Python
            /app/.venv/bin/python --version && \
            echo "Virtual environment verification completed"; \
        else \
            echo "Warning: Cannot find Python interpreter, virtual environment may need to be recreated"; \
        fi; \
    else \
        echo "Error: Virtual environment directory does not exist"; \
    fi

# Set working directory
WORKDIR /app

# Create models directory
# Note: Model files are mounted via Volume, not copied into image
RUN mkdir -p models

# Copy application code and config files
# Copy pyproject.toml first (virtual environment already has dependencies installed at build time)
COPY pyproject.toml ./
# Then copy other application files
COPY *.py ./

# Expose ports
# 8100: FastMCP server (SSE endpoint)
# 8000: Chat server (HTTP API)
EXPOSE 8100 8000

# Startup command specified by docker-compose.yml
