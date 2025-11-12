#!/bin/bash

# Script to start FastMCP and Chat servers

echo "=== FastMCP Demo Startup Script ==="

# Check model file
if [ ! -f "./models/qwen2-1_5b-instruct-q4_k_m.gguf" ]; then
    echo "Warning: Model file does not exist, please download model file first"
    echo "Refer to README.md for instructions"
fi

# Start FastMCP server (background)
echo "Starting FastMCP server (port 8100)..."
python mcp_server.py &
MCP_PID=$!
echo "FastMCP server PID: $MCP_PID"

# Wait for MCP server to start
sleep 3

# Start Chat server (foreground)
echo "Starting Chat server (port 8000)..."
echo "Visit http://localhost:8000/docs to view API documentation"
echo "Press Ctrl+C to stop all services"
python chat_server.py

# Cleanup: If Chat server exits, stop MCP server
kill $MCP_PID 2>/dev/null
echo "All services stopped"

