FROM python:3.11-slim

# 安装系统依赖
# build-essential: 编译 llama-cpp-python 需要
# wget: 可选，用于下载模型文件
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
# fastmcp: MCP框架
# llama-cpp-python: 本地模型推理引擎
# flask: HTTP API服务器
RUN pip install --no-cache-dir -r requirements.txt

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
