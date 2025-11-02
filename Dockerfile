# 多阶段构建：第一阶段使用轻量级基础镜像 + uv 管理 Python
# 使用 debian:bookworm-slim 作为基础，uv 会自动管理 Python 环境
FROM debian:bookworm-slim AS builder

# 配置 apt 代理（如果宿主机有代理）
# 注意：只对 localhost 进行替换，其他代理地址（如 squid.corp.redhat.com）保持不变
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        if echo "$BUILD_PROXY" | grep -q "localhost"; then \
            BUILD_PROXY_CONVERTED=$(echo "$BUILD_PROXY" | sed 's|localhost|host.docker.internal|g'); \
        else \
            BUILD_PROXY_CONVERTED="$BUILD_PROXY"; \
        fi && \
        echo "配置 apt 代理: $BUILD_PROXY_CONVERTED" && \
        echo "Acquire::http::Proxy \"$BUILD_PROXY_CONVERTED\";" > /etc/apt/apt.conf.d/01proxy && \
        echo "Acquire::https::Proxy \"$BUILD_PROXY_CONVERTED\";" >> /etc/apt/apt.conf.d/01proxy; \
    fi

# 配置 apt 重试和超时（独立层，可缓存）
RUN echo 'Acquire::Retries "10";' >> /etc/apt/apt.conf.d/99-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout

# 更新包列表（独立层，可缓存）
RUN apt-get update

# 安装基础工具和编译工具（独立层，可缓存）
RUN apt-get install -y --no-install-recommends --fix-missing \
    ca-certificates \
    curl \
    build-essential \
    cmake

# 清理 apt 缓存（独立层，可缓存）
RUN rm -rf /var/lib/apt/lists/*

# 复制代理设置辅助脚本
COPY docker-set-proxy.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-set-proxy.sh

# 安装 uv（独立层，可缓存）
# uv 安装到 /root/.local/bin，只有代理配置或 uv 版本改变时才重新下载
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        echo "使用代理下载 uv: $BUILD_PROXY_CONVERTED" && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED" && \
        curl --proxy "$BUILD_PROXY_CONVERTED" -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && \
        sh /tmp/uv-install.sh && \
        rm -f /tmp/uv-install.sh; \
    else \
        echo "不使用代理下载 uv"; \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && \
        sh /tmp/uv-install.sh && \
        rm -f /tmp/uv-install.sh; \
    fi

# 验证 uv 安装（独立层，可缓存）
RUN export PATH="/root/.local/bin:$PATH" && \
    /root/.local/bin/uv --version

# 复制项目文件（先复制配置文件，便于 uv sync）
WORKDIR /app
COPY pyproject.toml ./

# 安装 Python（独立层，可缓存）
# uv 会自动下载并管理 Python 3.11，Python 会缓存在 /root/.local/share/uv/python/
ARG BUILD_PROXY
RUN export PATH="/root/.local/bin:$PATH" && \
    if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED"; \
    fi && \
    echo "使用 uv 安装 Python 3.11..." && \
    uv python install 3.11 && \
    uv python list

# 使用 uv sync 创建虚拟环境并安装依赖（独立层，只有依赖改变时才重新执行）
ARG BUILD_PROXY
RUN export PATH="/root/.local/bin:$PATH" && \
    if [ -n "$BUILD_PROXY" ]; then \
        BUILD_PROXY_CONVERTED=$(/usr/local/bin/docker-set-proxy.sh "$BUILD_PROXY") && \
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true && \
        export http_proxy="$BUILD_PROXY_CONVERTED" https_proxy="$BUILD_PROXY_CONVERTED" HTTP_PROXY="$BUILD_PROXY_CONVERTED" HTTPS_PROXY="$BUILD_PROXY_CONVERTED" && \
        echo "已配置 uv 代理: $BUILD_PROXY_CONVERTED"; \
    fi && \
    echo "=== 使用 uv sync 安装依赖（构建阶段，需要编译工具）===" && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        echo "检测到 ARM 架构，设置编译选项..." && \
        export CMAKE_ARGS="-DGGML_NATIVE=OFF -DCMAKE_C_FLAGS='-march=armv8-a' -DCMAKE_CXX_FLAGS='-march=armv8-a'" && \
        export GGML_NATIVE=OFF; \
    else \
        echo "检测到架构: $ARCH，使用默认编译选项"; \
    fi && \
    uv sync --verbose && \
    echo "=== uv sync 完成 ===" && \
    # 验证虚拟环境和依赖
    ls -la /app/.venv/bin/ | head -10 && \
    /app/.venv/bin/python --version && \
    /app/.venv/bin/pip list | head -20

# 最终阶段：只复制 uv、Python 和虚拟环境，不包含编译工具
FROM debian:bookworm-slim

# 配置 apt 代理（如果宿主机有代理）
# 注意：只对 localhost 进行替换，其他代理地址（如 squid.corp.redhat.com）保持不变
ARG BUILD_PROXY
RUN if [ -n "$BUILD_PROXY" ]; then \
        if echo "$BUILD_PROXY" | grep -q "localhost"; then \
            BUILD_PROXY_CONVERTED=$(echo "$BUILD_PROXY" | sed 's|localhost|host.docker.internal|g'); \
        else \
            BUILD_PROXY_CONVERTED="$BUILD_PROXY"; \
        fi && \
        echo "配置 apt 代理: $BUILD_PROXY_CONVERTED" && \
        echo "Acquire::http::Proxy \"$BUILD_PROXY_CONVERTED\";" > /etc/apt/apt.conf.d/01proxy && \
        echo "Acquire::https::Proxy \"$BUILD_PROXY_CONVERTED\";" >> /etc/apt/apt.conf.d/01proxy; \
    fi

# 配置 apt 重试和超时（与 builder 阶段一致）
RUN echo 'Acquire::Retries "10";' >> /etc/apt/apt.conf.d/99-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/99-timeout

# 更新 apt 包列表（独立层，可缓存）
# 注意：将 apt-get update 独立出来，只有代理配置改变时才重新执行
RUN apt-get update

# 从builder阶段复制 uv、Python 和虚拟环境
# uv 安装在 /root/.local/bin/uv
# uv 管理的 Python 在 /root/.local/share/uv/python/
# 虚拟环境在 /app/.venv/（包含所有已安装的依赖）
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/.venv /app/.venv

# 安装运行时依赖（独立层，可缓存）
# 注意：编译工具（build-essential, cmake）仅在 builder 阶段需要
# 最终阶段只需要运行时库：
#   - libgcc-s1（C++运行时）
#   - libstdc++6（标准C++库）
#   - libgomp1（OpenMP运行时，llama-cpp-python需要）
# 使用重试机制处理网络问题
RUN (apt-get install -y --no-install-recommends \
        ca-certificates \
        libgcc-s1 \
        libstdc++6 \
        libgomp1 || \
     (echo "第一次安装失败，重试..." && \
      apt-get update && \
      apt-get install -y --no-install-recommends --fix-missing \
          ca-certificates \
          libgcc-s1 \
          libstdc++6 \
          libgomp1)) && \
    rm -rf /var/lib/apt/lists/* && \
    echo "运行时依赖安装完成（仅运行时库，无编译工具）"

# 设置 PATH：确保 uv 和虚拟环境中的 Python 可用
ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"

# 验证 uv、Python 和虚拟环境已正确复制，并修复 Python 链接
RUN /root/.local/bin/uv --version && \
    /root/.local/bin/uv python list && \
    if [ -d "/app/.venv" ]; then \
        echo "检查虚拟环境..." && \
        # 查找 uv 管理的 Python 解释器路径
        PYTHON_PATH=$(/root/.local/bin/uv python list | grep "3.11" | head -1 | awk '{print $NF}' || echo "") && \
        if [ -n "$PYTHON_PATH" ] && [ -f "$PYTHON_PATH/bin/python3" ]; then \
            echo "找到 Python 解释器: $PYTHON_PATH/bin/python3" && \
            # 修复虚拟环境中的 Python 链接
            if [ -f "/app/.venv/bin/python3" ]; then \
                rm -f /app/.venv/bin/python3 && \
                ln -sf "$PYTHON_PATH/bin/python3" /app/.venv/bin/python3 && \
                rm -f /app/.venv/bin/python && \
                ln -sf python3 /app/.venv/bin/python && \
                echo "已修复 Python 链接"; \
            fi && \
            # 验证修复后的 Python
            /app/.venv/bin/python --version && \
            echo "虚拟环境验证完成"; \
        else \
            echo "警告: 无法找到 Python 解释器，虚拟环境可能需要重新创建"; \
        fi; \
    else \
        echo "错误: 虚拟环境目录不存在"; \
    fi

# 设置工作目录
WORKDIR /app

# 创建模型目录
# 注意：模型文件通过Volume挂载，不会复制到镜像中
RUN mkdir -p models

# 复制应用代码和配置文件
# 先复制 pyproject.toml（虚拟环境已在构建时安装好依赖）
COPY pyproject.toml ./
# 然后复制其他应用文件
COPY *.py ./

# 暴露端口
# 8100: FastMCP服务器（SSE端点）
# 8000: Chat服务器（HTTP API）
EXPOSE 8100 8000

# 启动命令由docker-compose.yml指定
