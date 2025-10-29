FROM python:3.11-slim

# 设置代理（如果环境变量存在）
ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG proxy_url
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV no_proxy=$no_proxy
ENV HTTP_PROXY=$http_proxy
ENV HTTPS_PROXY=$https_proxy
ENV NO_PROXY=$no_proxy
ENV PROXY_URL=$proxy_url

# 配置 apt 代理（如果代理存在）
RUN if [ -n "$http_proxy" ]; then \
        echo "Acquire::http::Proxy \"$http_proxy\";" > /etc/apt/apt.conf.d/01proxy && \
        echo "Acquire::https::Proxy \"$https_proxy\";" >> /etc/apt/apt.conf.d/01proxy; \
    fi

# 安装编译工具
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件和安装脚本
COPY requirements.txt .
COPY install.sh .

# 运行安装脚本（配置代理并安装依赖）
RUN chmod +x install.sh && ./install.sh

# 创建模型目录
# 注意：模型文件通过Volume挂载，不会复制到镜像中
RUN mkdir -p models

# 复制应用代码
# 包含 server.py, tools.py 等应用文件
COPY . .

# 暴露端口
# 8000: Flask HTTP API服务端口
EXPOSE 8000

# 启动命令
# 直接运行MCP服务器，会自动加载模型和启动HTTP API
CMD ["python", "server.py"]
