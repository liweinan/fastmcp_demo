#!/bin/bash

# 启动FastMCP和Chat服务器的脚本

echo "=== FastMCP Demo 启动脚本 ==="

# 检查模型文件
if [ ! -f "./models/qwen2-1_5b-instruct-q4_k_m.gguf" ]; then
    echo "警告: 模型文件不存在，请先下载模型文件"
    echo "参考README.md中的说明"
fi

# 启动FastMCP服务器（后台）
echo "启动FastMCP服务器（端口8100）..."
python mcp_server.py &
MCP_PID=$!
echo "FastMCP服务器PID: $MCP_PID"

# 等待MCP服务器启动
sleep 3

# 启动Chat服务器（前台）
echo "启动Chat服务器（端口8000）..."
echo "访问 http://localhost:8000/docs 查看API文档"
echo "按 Ctrl+C 停止所有服务"
python chat_server.py

# 清理：如果Chat服务器退出，停止MCP服务器
kill $MCP_PID 2>/dev/null
echo "所有服务已停止"

