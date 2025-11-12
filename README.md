# FastMCP Minimal Example

This is a minimal example based on FastMCP, demonstrating how to build a complete tool calling system:
- **FastMCP Server**: Exposes calculation tool interfaces (via MCP protocol and SSE transport)
- **FastAPI Chat Server**: Provides chat service, LLM calls FastMCP tools through MCP client

<img width="3840" height="2110" alt="b076f65573ef5b15190df9424cd20a12" src="https://github.com/user-attachments/assets/30232728-9b46-4393-8a54-8b09b26f685b" />

## Related Projects:

- https://github.com/fastapi/fastapi
- https://github.com/jlowin/fastmcp
- https://github.com/ggml-org/llama.cpp
- https://github.com/run-llama/llama_index

## Model Used

- https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF

## Reference Documentation

- https://developers.llamaindex.ai/python/examples/agent/react_agent/
- https://www.ibm.com/think/topics/react-agent
- https://modelcontextprotocol.io/docs/getting-started/intro
- https://hackteam.io/blog/your-llm-does-not-care-about-mcp/
- https://medium.com/@infin94/kickstart-your-research-instantly-generate-synthetic-text-data-with-llama-3-1-56eaee6fbf48
- https://levelup.gitconnected.com/how-i-built-a-tool-calling-llama-agent-with-a-custom-mcp-server-3bc057d27e85
- https://www.anthropic.com/news/model-context-protocol
- https://github.com/Kludex/starlette

## Features

- 🤖 **Real LLM Inference**: Uses Llama 3.1 8B language model (supports native tool_calls)
- 💬 **Friendly Conversation**: Supports natural language dialogue, can friendly reply to greetings and casual chat
- 🛠️ **Intelligent Tool Calling**: Uses LlamaIndex ReActAgent to automatically handle tool calls, LLM calls FastMCP server tools through MCP protocol
- 🔌 **FastMCP Integration**: Uses FastMCP framework to expose tools, provides tool interfaces through SSE protocol
- 🐳 Docker Containerized Deployment: Supports multi-service architecture (FastMCP server + Chat server)
- 🌐 HTTP API interface, supports curl interaction
- ⚡ CPU inference based on llama.cpp
- 🛡️ Comprehensive error handling and friendly error messages

## Quick Start

### 1. Download Model

The project uses **Llama 3.1 8B-Instruct** model (supports native tool_calls).

**Characteristics**:
- Model size: ~4.6GB
- Memory requirement: ~8GB RAM
- Tool calling: Native tool_calls support, automatically handled by LlamaIndex
- Inference speed: Medium
- **Advantage**: More accurate and reliable tool calling, better context understanding

**Download Methods**:

**Important**: Meta official version (`meta-llama/Llama-3.1-8B-Instruct`) requires login authentication.  
**Recommended**: Use community public quantized version (no authentication required, same functionality):

```bash
# Method 1: Direct download with wget (recommended, simplest)
mkdir -p models
# Download from bartowski (public version, no authentication, ~4.6GB)
wget -O models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# Note: Filename must be Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf, otherwise service cannot start

# Method 2: Use huggingface-cli (bartowski version, no login required)
pip install huggingface_hub
huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \
  --include "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" --local-dir ./models
```

**Alternative Public Sources** (all require no authentication, sorted by download count):
- `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF` (95k+ downloads, recommended)
- `MaziyarPanahi/Meta-Llama-3.1-8B-Instruct-GGUF` (76.2k downloads)
- `QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF` (55.5k downloads)

**Notes**:
- File size is ~4.6GB, ensure sufficient disk space
- Model filename is fixed as: `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
- File must be placed in `./models/` directory

### 2. Build and Start

#### Method 1: Use Build Script (Recommended)
```bash
# 1. Configure proxy (optional)
cp env.example .env
# Edit .env file, set your proxy configuration

# 2. Use build script
./build.sh

# 3. Start services
docker-compose up
```

#### Method 2: Manual Build
```bash
# No proxy environment
docker-compose build
docker-compose up

# Enterprise proxy environment
export PROXY_URL=http://your-proxy:port
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
export NO_PROXY=localhost,127.0.0.1

docker-compose build --build-arg proxy_url=$PROXY_URL --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY --build-arg no_proxy=$NO_PROXY
docker-compose up
```

#### Configuration Notes
- **PROXY_URL**: Proxy server address (e.g., `http://proxy.company.com:8080`)
- **HTTP_PROXY/HTTPS_PROXY**: Proxy settings during Docker build
- **NO_PROXY**: List of addresses that should not use proxy

**Note**: The project includes an automatic proxy configuration script `install.sh`, which automatically handles proxy settings inside containers based on environment variables.

Services will start at the following addresses:
- **FastMCP Server**: `http://localhost:8100` (provides tool interfaces)
- **Chat Server**: `http://localhost:8000` (provides chat service)

**Startup Verification**:
After startup, check logs, you should see:
- `Loading model: ./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
- `Model loaded successfully`
- `MCP server connected successfully, found 3 tools`
- `Agent initialization complete, tool calls will be automatically handled by LlamaIndex`

**Runtime Logs**:
- LlamaIndex will automatically handle tool calls, logs will show tool call process
- Using `verbose=True` you can see detailed tool call and response information

**Notes**:
- Need to download Llama 3.1 8B model file first (~4.6GB)
- Tool calls are automatically handled by LlamaIndex ReActAgent, no manual parsing needed
- Supports native tool_calls, no text parsing needed
- Agent maximum iteration count set to 3, to avoid excessive response time
- Response contains raw complete output (`raw_response`)

### 3. Test API

#### Health Check
```bash
curl http://localhost:8000/health
```
**Expected Output**:
```json
{"status":"healthy","agent_loaded":true,"mcp_available":true,"tools_count":3}
```

**Note**: If `agent_loaded` is `false`, it means the model file was not found or Agent initialization failed, need to download model file first.

#### View Available Tools

**Note**: FastMCP server uses SSE protocol (`/sse` endpoint), cannot be accessed directly via curl. Tool list is obtained through HTTP API provided by Chat server.

**Get tool list from Chat server**:
```bash
curl http://localhost:8000/tools
```

#### Chat Test

**Notes**: 
1. If Chinese displays as Unicode escape characters (like `\u6211`), you can use `jq` or `python3 -m json.tool` to display correctly
2. Please ensure to use **English quotes**, not Chinese quotes ("")

```bash
# Greeting conversation (natural language reply)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}' | jq .
# Expected output:
# {
#   "raw_response": "你好！有什么我可以帮助你的吗？",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Simple addition (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | jq .
# Expected output:
# {
#   "raw_response": "Thought: ... Answer: 8 ...",  # Complete Agent output
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Multiplication (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 4 * 7"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 28", 
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Expression calculation (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 2+3*4"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 14",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Complex expression (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 3 * 7"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 21",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Non-calculation message (natural language reply)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "今天天气如何"}' | jq .
# Expected output:
# {
#   "raw_response": "今天的天气取决于你所在的地方，你可以告诉我你在哪里吗？",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }
```

**Feature Description**:
- 🧮 **Calculation Requests**: When users ask mathematical calculation questions, LLM will automatically call corresponding tools for calculation
- 💬 **Friendly Conversation**: When users greet or chat casually, LLM will reply friendly in natural language (will not call tools)
- 🔍 **Intelligent Recognition**: LLM will automatically recognize user intent, decide whether to use tools or reply directly
- ⚡ **Fast Response**: Maximum iteration count limited to 3, ensuring reasonable response time
- 📝 **Raw Response**: Returns complete raw output (`raw_response`)

**Alternative** (if system doesn't have `jq` installed):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | python3 -m json.tool
```

## Project Architecture

### 🔍 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  User Request (curl)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           FastAPI Chat Server (Port 8000)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LlamaIndex + llama-cpp-python → Llama 3.1 8B        │   │
│  │  - Analyze user request                              │   │
│  │  - Generate tool call declaration                    │   │
│  │  - Generate final response based on tool result      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                │
│                            │ SSE Connection                 │
│                            │ (via MCP Client)               │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MCP Client (BasicMCPClient)                         │   │
│  │  - Get tool list                                     │   │
│  │  - Call tool interface                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SSE Protocol (/sse)
                            │ MCP Protocol over SSE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         FastMCP Server (Port 8100)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastMCP Framework                                   │   │
│  │  - @mcp.tool() decorator registers tools             │   │
│  │  - SSE transport protocol (/sse)                     │   │
│  │  - Auto-exposes tools via MCP protocol               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tool Execution Layer                                │   │
│  │  - add_numbers()                                     │   │
│  │  - multiply_numbers()                                │   │
│  │  - calculate_expression()                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Points**:
- **FastMCP Server** (port 8100): Registers tools through `@mcp.tool()` decorator, provides SSE endpoint (`/sse`) to expose MCP protocol interface
- **FastAPI Chat Server** (port 8000): Uses llama-cpp-python for LLM inference, connects to FastMCP server's SSE endpoint through MCP client (BasicMCPClient)
- **Workflow**: User request → Chat server → LLM analysis → MCP protocol (SSE) calls FastMCP tools → Returns result → LLM generates final reply

### 🚀 Data Flow Example

**User Request: "Calculate 25 + 17"**

```
1. User → Chat Server (POST /chat)
   {"message": "Calculate 25 + 17"}

2. Chat Server → LLM (Round 1 inference)
   LLM analysis: "Need to call add_numbers tool"
   Generate tool call declaration: [add_numbers(a=25, b=17)]

3. Chat Server → FastMCP Server (via SSE /sse endpoint)
   MCP protocol call: add_numbers(a=25, b=17)

4. FastMCP Server → Tool Execution
   Execute: add(25, 17) → return 42

5. FastMCP Server → Chat Server
   Return: {"result": 42}

6. Chat Server → LLM (Round 2 inference)
   Feed tool result to LLM, LLM generates final response

7. Chat Server → User
   {"response": "Calculation result: 42", "tools_available": [...]}
```

## Project Structure

```
fastmcp_demo/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration (two services: mcp-server + chat-server)
├── pyproject.toml          # Python project configuration and dependencies (managed with uv)
├── install.sh             # Automatic installation script (handles proxy configuration)
├── build.sh               # Build script (supports environment variable configuration)
├── start_servers.sh       # Local startup script (starts both services simultaneously)
├── env.example            # Environment configuration example file
├── mcp_server.py          # FastMCP server (port 8100)
├── chat_server.py         # FastAPI Chat server (port 8000)
├── models/                # Model file directory (Volume mount)
└── README.md              # Usage instructions
```

## Technology Stack

- **FastMCP Framework**: FastMCP >= 0.1.0 (MCP protocol implementation)
- **MCP Protocol**: Model Context Protocol (tool calling protocol)
- **LlamaIndex**: >= 0.10.0 (Agent framework that automatically handles tool calls)
- **AI Model**: Llama 3.1 8B-Instruct-GGUF (supports native tool_calls)
- **Inference Engine**: llama-cpp-python (based on llama.cpp)
- **LLM Library**: llama-cpp-python >= 0.2.0
- **Web Framework**: FastAPI >= 0.104.0 (Chat server)
- **HTTP Client**: httpx >= 0.25.0 (MCP client)
- **ASGI Server**: uvicorn >= 0.24.0
- **Containerization**: Docker + Docker Compose
- **Proxy Handling**: Automatic proxy configuration script

## Model Information

### Llama 3.1 8B-Instruct (Default, Recommended)

- **Parameters**: 8B
- **Quantization**: Q4_K_M (~4.6GB)
- **Memory Requirement**: ~8GB RAM
- **Tool Calling**: **Stronger tool calling capability** (more accurate and reliable tool calling)
- **Inference**: CPU inference, no GPU required
- **Speed**: Medium (but tool calling is more reliable)
- **Advantage**: Better tool calling capability, more accurate and reliable


## Running Modes

The project **defaults to real LLM mode**, requires downloading model files to run. Model files will be automatically loaded at startup and perform real inference calculations.

### Real LLM Mode (Default)
The project uses real Llama 3.1 8B model for inference:
- ✅ **Real LLM Inference**: Uses llama-cpp-python to actually call the model
- ✅ **Intelligent Tool Calling**: Uses LlamaIndex ReActAgent to automatically handle tool calls
- ✅ **Native tool_calls Support**: Llama 3.1 8B supports native tool_calls, no text parsing needed
- ✅ **Friendly Conversation**: Supports natural language dialogue, can friendly reply to greetings and casual chat
- ✅ **Error Handling**: Comprehensive parameter validation and error messages
- ⚠️ **Requires Model File**: Must download model file to `./models/` directory to run

If model file does not exist, the service will fail to start and display error message.

## Important Notes

1. **Model File Required**: Must download Llama 3.1 8B model file (~4.6GB) to `./models/` directory, otherwise service cannot start
2. **Memory Requirement**: Recommend at least 8GB available memory (model requires ~8GB RAM)
3. **Network Connection**: First-time model download requires good network connection
4. **Proxy Environment**: Enterprise network environments need to configure proxy, see build instructions for details
5. **Request Format**: When using curl, ensure JSON uses English quotes, e.g., `'{"message": "你好"}'`
6. **Tool Calling**: Tool calls are automatically handled by LlamaIndex, no manual parsing or configuration needed

## LLM Usage Principles

### 1. Architecture Overview

The project adopts a **dual-server architecture**:
- **FastMCP Server** (`mcp_server.py`): Registers tools through `@mcp.tool()` decorator, exposes MCP protocol interface through SSE protocol (`/sse` endpoint)
- **Chat Server** (`chat_server.py`): Uses llama-cpp-python for LLM inference, connects to FastMCP server's SSE endpoint through MCP client (BasicMCPClient)

### 2. FastMCP Server

```python
# Create FastMCP instance
mcp = FastMCP("MathTools")

# Register tools
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers"""
    return add(a, b)

# Start server (via SSE transport protocol)
# After FastMCP tools are registered, MCP protocol interface is automatically exposed through SSE endpoint (/sse)
mcp.run(transport="sse")
```

**FastMCP Server Features**:
- Registers tools through `@mcp.tool()` decorator (`add_numbers`, `multiply_numbers`, `calculate_expression`)
- Provides MCP protocol interface using SSE transport protocol:
  - SSE endpoint: `http://0.0.0.0:8100/sse`
  - Tool list and calls are automatically exposed through MCP protocol
- FastMCP framework automatically handles tool registration and calls through SSE protocol

### 3. Chat Server and LLM Inference (Automatically Handled by LlamaIndex)

#### a) Model Loading and Agent Initialization
```python
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.tools.mcp import McpToolSpec, BasicMCPClient
from llama_index.core.agent import ReActAgent

# Load Llama model
llm = LlamaCPP(
    model_path=model_path,  # Llama 3.1 8B GGUF file
    temperature=0.1,
    max_new_tokens=256,
    context_window=4096,
    model_kwargs={"n_threads": 6},
)

# Connect to FastMCP server to get tools (via SSE endpoint)
mcp_sse_url = "http://localhost:8100/sse"
client = BasicMCPClient(command_or_url=mcp_sse_url, timeout=10)
tool_spec = McpToolSpec(client=client)
tools = await tool_spec.to_tool_list_async()  # Async get tool list

# Create ReActAgent (automatically handles tool calls)
agent = ReActAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True,
    system_prompt="You are a friendly math calculation assistant..."
)
```

#### b) Tool Call Flow (Automatically Handled)

**LlamaIndex ReActAgent automatically handles all tool calls**:

```python
# User request
handler = agent.run(
    user_msg="Calculate 25 + 17",
    memory=ChatMemoryBuffer(token_limit=3000),
    ctx=Context(agent),
    max_iterations=3  # Maximum iteration count, avoid excessive response time
)
result = await handler

# LlamaIndex will automatically:
# 1. Analyze user request
# 2. Decide if tool call is needed
# 3. If needed, generate tool_calls (native format)
# 4. Execute tool call
# 5. Feed result back to LLM
# 6. Generate final reply
```

**Advantages**:
- ✅ No manual parsing of tool calls needed
- ✅ Automatically handles native tool_calls format
- ✅ Supports multiple rounds of tool calls
- ✅ Comprehensive error handling and retry mechanism
- ✅ Raw response: Returns complete raw output
- ✅ Iteration count limit: Maximum 3 iterations, avoid long wait times

### 4. Complete Workflow Example

When user sends `"Calculate 25 + 17"`:

1. **User Request** → Chat Server (`POST /chat`)
2. **LlamaIndex Agent Analysis**: ReActAgent automatically decides tool call is needed
3. **Generate tool_calls**: Agent generates native format tool_calls (`add_numbers(a=25, b=17)`)
4. **Automatically Execute Tool**: LlamaIndex calls FastMCP tool through MCP protocol
5. **FastMCP Executes Tool**: Calls `add_numbers(25, 17)` → Returns `42`
6. **Generate Final Reply**: Agent feeds result back to LLM, generates friendly reply
7. **Return Final Result**: `"Calculation result: 42"`

### 5. Why Use LlamaIndex?

**Important Note**: Uses LlamaIndex framework to automatically handle tool calls, no manual parsing needed.

#### LlamaIndex Advantages

1. **Automatic Tool Call Handling**
   - ✅ Automatically recognizes when tool call is needed
   - ✅ Automatically handles native tool_calls format
   - ✅ No manual parsing of text or JSON needed

2. **Comprehensive Agent Architecture**
   - ✅ ReActAgent implements think-act-observe loop
   - ✅ Supports multiple rounds of tool calls
   - ✅ Automatically handles tool execution results

3. **Deep Integration with MCP Protocol**
   - ✅ `McpToolSpec` automatically gets tools from FastMCP server
   - ✅ Supports SSE protocol communication
   - ✅ Automatically converts tool formats

#### Key Features

- **MCP Protocol**: Uses FastMCP framework standardized tool calling method
- **LlamaIndex Integration**: Automatically handles all tool calling logic through LlamaIndex
- **Dual-Server Architecture**: Tool server and chat server separated, clear responsibilities
- **Native tool_calls Support**: Llama 3.1 8B supports native tool_calls, automatically handled by LlamaIndex
- **Local Inference**: Model runs completely locally, no network needed (except initial download)
- **CPU Optimized**: Uses llama.cpp for efficient CPU inference, no GPU needed

## Troubleshooting

### Proxy Related Issues
If you encounter connection issues in enterprise network environments:

1. **Use Configuration File** (Recommended):
   ```bash
   cp env.example .env
   # Edit .env file, set correct proxy address
   ./build.sh
   ```

2. **Manually Set Environment Variables**:
   ```bash
   export PROXY_URL=http://your-proxy:port
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ./build.sh
   ```

3. **Check Proxy Connectivity**:
   ```bash
   curl -I --proxy $PROXY_URL https://pypi.org
   ```

4. **Rebuild**:
   ```bash
   docker-compose build --no-cache --build-arg proxy_url=$PROXY_URL --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY
   ```

### Model File Not Found
If service startup fails, prompting model file not found:
1. Ensure model file is downloaded to `./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
2. Check if file path is correct (relative path is `./models/`)
3. Verify file permissions, ensure readable
4. Check server logs for detailed error information

### Insufficient Memory
If encountering insufficient memory, you can try:
- Reduce `n_ctx` parameter (in chat_server.py, default 4096)
- Reduce `n_threads` parameter (in chat_server.py, default 6)
- Use smaller quantized version model (like Q2_K or Q3_K_M)
- Close other memory-consuming programs

### Timeout and Performance Tuning
If encountering timeout errors ("Agent processing timeout"), you can adjust the following parameters based on hardware configuration:

#### 1. 调整 Token 生成参数（chat_server.py）

**位置**：`chat_server.py` 第 79-90 行

```python
llm = LlamaCPP(
    model_path=model_path,
    temperature=0.1,
    max_new_tokens=256,  # 可调整：128-512，数值越大生成内容越多，但耗时更长
    context_window=4096,
    verbose=False,
    model_kwargs={
        "n_threads": 6,      # 可调整：根据CPU核心数设置，建议为物理核心数
        "n_predict": 256,    # 应与 max_new_tokens 保持一致
    },
)
```

**调整建议**：
- **快速响应**（较低CPU）：`max_new_tokens=128`, `n_predict=128`
- **平衡**（中等CPU）：`max_new_tokens=256`, `n_predict=256`（默认）
- **完整回复**（高性能CPU）：`max_new_tokens=512`, `n_predict=512`

#### 2. 调整超时时间（chat_server.py）

**位置**：`chat_server.py` 第 299 行

```python
result = await asyncio.wait_for(handler, timeout=120.0)  # 可调整：60-300秒
```

**调整建议**：
- **快速硬件**（8核+CPU，高频率）：60-90秒
- **中等硬件**（4-6核CPU）：120秒（默认）
- **较慢硬件**（2-4核CPU，低频率）：180-300秒

**计算公式**（粗略估算）：
```
超时时间 ≈ (max_new_tokens / 10) + 工具调用时间（5-10秒）
```

例如：`max_new_tokens=256` → 超时时间 ≈ 25-35秒 + 5-10秒 ≈ 30-45秒（实际建议设置为 2-3 倍，即 60-120 秒）

#### 3. 调整 Agent 迭代次数（chat_server.py）

**位置**：`chat_server.py` 第 294 行

```python
max_iterations=3  # 可调整：1-5，简单计算通常只需要1次迭代
```

**调整建议**：
- **简单计算**：`max_iterations=1-2`（更快响应）
- **复杂问题**：`max_iterations=3-5`（允许多次工具调用）

#### 4. 性能优化建议

**根据硬件配置选择参数组合**：

| CPU 核心数 | 推荐 max_new_tokens | 推荐 timeout | 推荐 n_threads |
|-----------|-------------------|--------------|---------------|
| 2-4 核    | 128               | 180-240 秒   | 2-4           |
| 4-6 核    | 256               | 120-180 秒   | 4-6           |
| 6-8 核    | 256-512           | 90-120 秒    | 6-8           |
| 8+ 核     | 512               | 60-90 秒     | 8+            |

**注意**：
- 参数调整后需要重启服务才能生效
- 如果频繁超时，优先考虑减少 `max_new_tokens` 而不是增加 `timeout`
- CPU 推理速度较慢，这是正常现象，考虑使用 GPU 加速可以显著提升性能

### System Prompt 配置说明
如果遇到 Agent 行为不符合预期（如频繁调用工具、循环调用等），可以调整或移除 system_prompt：

#### System Prompt 的作用

**位置**：`chat_server.py` 第 138-166 行

当前 system_prompt 的主要作用：
1. **限制工具调用次数**：明确指示"每次请求最多只调用一次工具"，避免循环调用
2. **明确使用场景**：只在数学计算时使用工具，问候和闲聊不使用工具
3. **指导 Agent 行为**：提供清晰的工作流程和示例

#### 是否可以去掉 System Prompt？

**是的，技术上可以去掉。**

ReActAgent 可以在没有 `system_prompt` 的情况下正常工作：

```python
agent = ReActAgent(
    tools=tools if tools else None,
    llm=llm,
    verbose=True,
    # system_prompt=system_prompt  # 可以注释掉或删除
)
```

或者设置为 `None`：

```python
agent = ReActAgent(
    tools=tools if tools else None,
    llm=llm,
    verbose=True,
    system_prompt=None  # 明确设置为 None
)
```

#### 去掉 System Prompt 的影响

**仍然可以工作**：
- ✅ ReActAgent 会使用默认的 system prompt
- ✅ 工具调用功能正常
- ✅ 基本推理能力不受影响

**但会有行为差异**：
- ⚠️ 没有明确的工具调用限制，Agent 可能会多次调用工具（可能出现之前遇到的循环调用问题）
- ⚠️ 没有"只调用一次工具"的明确指导
- ⚠️ 没有针对数学计算的专门指导，可能对任何问题都尝试调用工具
- ⚠️ 对于问候和闲聊也可能尝试调用工具

#### 何时需要保留 System Prompt？

**建议保留**，如果遇到以下问题：
- Agent 循环调用工具
- Agent 在不该使用工具的场景下调用工具（如问候语）
- Agent 对同一个问题多次调用工具
- 希望严格控制 Agent 的行为

#### 何时可以去掉 System Prompt？

可以考虑去掉，如果：
- 希望 Agent 有更灵活的行为
- 允许多次工具调用（复杂任务需要多步骤）
- 使用默认的 Agent 行为已经满足需求

**结论**：
- ✅ **技术上可行**：去掉 `system_prompt` 也可以运行
- ⚠️ **功能可能受影响**：可能恢复循环调用工具等问题
- 💡 **建议保留**：当前的 `system_prompt` 解决了之前的工具调用问题

### JSON格式错误
如果遇到 `400 Bad Request` 或 JSON 格式错误：
- 确保使用**英文引号**，不要使用中文引号
- 检查JSON格式是否正确，例如：`'{"message": "你好"}'`
- 查看错误响应中的详细提示和示例
- 可以使用文件方式发送请求避免转义问题：
  ```bash
  echo '{"message": "你好"}' | curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d @- | jq .
  ```

### 端口冲突
如果端口被占用：
- **8000 端口（Chat 服务器）**：在 `docker-compose.yml` 中修改 `chat-server` 的端口映射
- **8100 端口（FastMCP 服务器）**：在 `docker-compose.yml` 中修改 `mcp-server` 的端口映射，并更新 `chat_server.py` 中的 `MCP_SERVER_URL` 环境变量

### FastMCP 服务器连接失败
如果 Chat 服务器无法连接到 FastMCP 服务器：
1. 确保 FastMCP 服务器已启动（`mcp-server` 服务）
2. 检查 `MCP_SERVER_URL` 环境变量是否正确（Docker 内部使用 `http://mcp-server:8100`，本地使用 `http://localhost:8100`）
3. 查看日志确认两个服务都在运行
4. Chat 服务器启动时会自动重试连接（最多15次，每次间隔2秒）

### Agent 迭代次数达到上限
如果遇到 `Max iterations of 10 reached!` 错误：
1. **正常现象**：表示 Agent 在10次迭代内无法完成任务
2. **解决方案**：
   - 将复杂问题拆分为更简单的步骤
   - 重新表述问题，使其更清晰明确
   - 检查输入是否有误（如输入不完整）
3. **响应格式**：即使达到迭代上限，也会返回友好的错误提示

### 构建失败
如果 Docker 构建失败：
1. 检查网络连接
2. 确认代理配置正确
3. 尝试清理 Docker 缓存：`docker system prune -a`
4. 使用 `--no-cache` 重新构建

## MCP 协议交互分析报告

本节基于实际的日志输出，详细分析一次完整的 MCP 协议交互流程，帮助理解 chat-server 和 mcp-server 之间的通信过程。

### 请求场景

用户向 chat-server 发送请求：`计算 10 + 20 * 2`

### 完整的交互流程

#### 1. SSE 连接建立

**chat-server → mcp-server**

```
chat-server-1  | 2025-11-03 04:18:30,522 - httpx - INFO - HTTP Request: GET http://mcp-server:8100/sse "HTTP/1.1 200 OK"
```

**mcp-server 日志：**

```
mcp-server-1   | 2025-11-03 04:18:30,520 - mcp.server.sse - DEBUG - Setting up SSE connection
mcp-server-1   | 2025-11-03 04:18:30,520 - mcp.server.sse - DEBUG - Created new session with ID: bdd2d4d9-feb5-4331-8891-f4a747248ee1
mcp-server-1   | 2025-11-03 04:18:30,521 - mcp.server.sse - DEBUG - Starting SSE response task
mcp-server-1   | INFO:     172.21.0.3:39074 - "GET /sse HTTP/1.1" 200 OK
```

**说明**：chat-server 通过 GET 请求建立 SSE 长连接，mcp-server 创建新的会话并返回会话 ID。

---

#### 2. 初始化阶段（initialize）

**chat-server → mcp-server**（POST /messages/）

```
chat-server-1  | 2025-11-03 04:18:30,524 - httpx - INFO - HTTP Request: POST http://mcp-server:8100/messages/?session_id=bdd2d4d9feb543318891f4a747248ee1 "HTTP/1.1 202 Accepted"
```

**mcp-server 日志 - 接收请求：**

```
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Handling POST message
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Parsed session ID: bdd2d4d9-feb5-4331-8891-f4a747248ee1
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"mcp","version":"0.1.0"}},"jsonrpc":"2.0","id":0}'
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='initialize', params={'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'mcp', 'version': '0.1.0'}}, jsonrpc='2.0', id=0)
```

**mcp-server → chat-server**（通过 SSE 流返回响应）

```
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=0, result={'protocolVersion': '2025-06-18', 'capabilities': {...}, 'serverInfo': {'name': 'MathTools', 'version': '1.20.0'}})), metadata=None)
```

**格式化后的响应（通过日志格式化器）：**

```
mcp-server-1   | 2025-11-03 04:18:30,524 - sse_starlette.sse - DEBUG - [SSE Chunk - 已格式化]
mcp-server-1   | {
mcp-server-1   |   "jsonrpc": "2.0",
mcp-server-1   |   "id": 0,
mcp-server-1   |   "result": {
mcp-server-1   |     "protocolVersion": "2025-06-18",
mcp-server-1   |     "capabilities": {
mcp-server-1   |       "experimental": {},
mcp-server-1   |       "prompts": {"listChanged": false},
mcp-server-1   |       "resources": {"subscribe": false, "listChanged": false},
mcp-server-1   |       "tools": {"listChanged": false}
mcp-server-1   |     },
mcp-server-1   |     "serverInfo": {
mcp-server-1   |       "name": "MathTools",
mcp-server-1   |       "version": "1.20.0"
mcp-server-1   |     }
mcp-server-1   |   }
mcp-server-1   | }
```

**说明**：
- chat-server 发送 `initialize` 请求，包含协议版本和客户端信息
- mcp-server 返回服务器能力信息和服务器信息（名称、版本）

---

#### 3. 初始化完成通知（notifications/initialized）

**chat-server → mcp-server**

```
mcp-server-1   | 2025-11-03 04:18:30,526 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"notifications/initialized","jsonrpc":"2.0"}'
mcp-server-1   | 2025-11-03 04:18:30,526 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCNotification(method='notifications/initialized', params=None, jsonrpc='2.0')
```

**说明**：chat-server 通知 mcp-server 初始化已完成（这是 MCP 协议的标准流程）。

---

#### 4. 工具列表查询（tools/list）

**chat-server → mcp-server**

```
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"tools/list","jsonrpc":"2.0","id":1}'
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='tools/list', params=None, jsonrpc='2.0', id=1)
```

**mcp-server 处理请求：**

```
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - DEBUG - Dispatching request of type ListToolsRequest
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - DEBUG - Response sent
```

**mcp-server → chat-server**（返回工具列表）

```
mcp-server-1   | 2025-11-03 04:18:30,531 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=1, result={'tools': [...]})))
```

**格式化后的工具列表响应：**

```
mcp-server-1   | {
mcp-server-1   |   "jsonrpc": "2.0",
mcp-server-1   |   "id": 1,
mcp-server-1   |   "result": {
mcp-server-1   |     "tools": [
mcp-server-1   |       {
mcp-server-1   |         "name": "add_numbers",
mcp-server-1   |         "description": "计算两个数字的加法。\n重要：仅在用户明确要求进行加法计算时使用此工具...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       },
mcp-server-1   |       {
mcp-server-1   |         "name": "multiply_numbers",
mcp-server-1   |         "description": "计算两个数字的乘法。\n重要：仅在用户明确要求进行乘法计算时使用此工具...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       },
mcp-server-1   |       {
mcp-server-1   |         "name": "calculate_expression",
mcp-server-1   |         "description": "计算数学表达式。表达式必须只包含数字和基本运算符...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       }
mcp-server-1   |     ]
mcp-server-1   |   }
mcp-server-1   | }
```

**说明**：
- chat-server 请求工具列表
- mcp-server 返回所有可用工具及其描述、输入输出模式
- 工具描述包含使用场景说明，帮助 Agent 决定何时使用哪个工具

---

#### 5. 工具调用（tools/call）

**chat-server → mcp-server**（请求调用 `calculate_expression` 工具）

```
mcp-server-1   | 2025-11-03 04:18:30,527 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"tools/call","params":{"name":"calculate_expression","arguments":{"expression":"10 + 20 * 2"}},"jsonrpc":"2.0","id":1}'
mcp-server-1   | 2025-11-03 04:18:30,527 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='tools/call', params={'name': 'calculate_expression', 'arguments': {'expression': '10 + 20 * 2'}}, jsonrpc='2.0', id=1)
```

**mcp-server 处理工具调用：**

```
mcp-server-1   | 2025-11-03 04:18:30,528 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
mcp-server-1   | 2025-11-03 04:18:30,528 - mcp.server.lowlevel.server - DEBUG - Dispatching request of type CallToolRequest
mcp-server-1   | 2025-11-03 04:18:30,528 - __main__ - INFO - [FastMCP Tool] calculate_expression(expression='10 + 20 * 2')
mcp-server-1   | 2025-11-03 04:18:30,528 - __main__ - INFO - [FastMCP Tool] calculate_expression 结果: 50.0
mcp-server-1   | 2025-11-03 04:18:30,529 - mcp.server.lowlevel.server - DEBUG - Response sent
```

**mcp-server → chat-server**（返回工具执行结果）

```
mcp-server-1   | 2025-11-03 04:18:30,529 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=1, result={'content': [{'type': 'text', 'text': '50.0'}], 'structuredContent': {'result': 50.0}, 'isError': False})), metadata=None)
```

**格式化后的工具调用响应：**

```
mcp-server-1   | {
mcp-server-1   |   "jsonrpc": "2.0",
mcp-server-1   |   "id": 1,
mcp-server-1   |   "result": {
mcp-server-1   |     "content": [
mcp-server-1   |       {
mcp-server-1   |         "type": "text",
mcp-server-1   |         "text": "50.0"
mcp-server-1   |       }
mcp-server-1   |     ],
mcp-server-1   |     "structuredContent": {
mcp-server-1   |       "result": 50.0
mcp-server-1   |     },
mcp-server-1   |     "isError": false
mcp-server-1   |   }
mcp-server-1   | }
```

**说明**：
- chat-server（Agent）根据用户请求决定调用 `calculate_expression` 工具，参数为 `"10 + 20 * 2"`
- mcp-server 执行工具函数，计算结果为 `50.0`
- mcp-server 返回格式化的结果，包含文本格式和结构化格式

---

#### 6. 最终响应

**chat-server 返回给用户：**

```json
{
  "raw_response": "50.0\n\n\n\n## Step 1: Determine the task\n...",
  "tools_available": [
    "add_numbers",
    "multiply_numbers",
    "calculate_expression"
  ]
}
```

---

### 关键发现

1. **双向通信**：
   - chat-server → mcp-server：通过 `POST /messages/` 发送 JSON-RPC 请求
   - mcp-server → chat-server：通过 SSE 流返回 JSON-RPC 响应

2. **会话管理**：
   - 每个 SSE 连接有唯一的 `session_id`
   - 所有请求都通过 `?session_id=xxx` 参数关联到同一个会话

3. **请求-响应匹配**：
   - JSON-RPC 协议通过 `id` 字段匹配请求和响应
   - 例如：初始化请求 `id=0`，对应的响应也是 `id=0`

4. **工具调用流程**：
   - Agent 先获取工具列表（了解可用工具）
   - Agent 分析用户请求，决定调用哪个工具
   - Agent 发送 `tools/call` 请求，包含工具名称和参数
   - mcp-server 执行工具并返回结果
   - Agent 将结果整合到最终回复中

5. **日志格式化器的作用**：
   - 自动格式化 JSON-RPC 消息，使其更易读
   - 将中文 Unicode 转义序列转换为可读中文
   - 格式化 SSE chunk 中的 JSON 数据
   - 帮助开发者理解 MCP 协议的详细交互过程

### 日志查看技巧

1. **查看完整的 MCP 交互**：在 mcp-server 日志中搜索 `Sending message via SSE` 或 `Received JSON`
2. **查看工具执行**：搜索 `[FastMCP Tool]` 查看工具的实际执行情况
3. **查看格式化后的 JSON**：搜索 `[SSE Chunk - 已格式化]` 查看格式化后的 JSON 响应
4. **跟踪会话**：通过 `session_id` 跟踪同一会话的所有请求和响应

### 协议流程图

```
用户请求: "计算 10 + 20 * 2"
    ↓
chat-server (Agent)
    ↓
1. GET /sse (建立 SSE 连接)
    ↓
2. POST /messages/ (initialize)
    ↓
3. POST /messages/ (notifications/initialized)
    ↓
4. POST /messages/ (tools/list) ← mcp-server 返回工具列表
    ↓
5. Agent 分析：需要调用 calculate_expression
    ↓
6. POST /messages/ (tools/call) ← mcp-server 执行工具并返回结果
    ↓
7. Agent 生成最终回复
    ↓
返回给用户: {"raw_response": "...", "tools_available": [...]}
```

---

**注意**：以上日志基于 DEBUG 级别的日志输出。默认情况下，MCP 相关日志已设置为 DEBUG 级别，并使用自定义格式化器进行格式化，确保 JSON 数据以易读格式输出，中文正确显示。

## 调试和容器命令

### 进入容器进行调试

当需要深入调试或排查问题时，可以进入容器执行命令。

#### 查看运行中的容器

```bash
docker ps
```

#### 进入 mcp-server 容器

```bash
docker exec -it fastmcp_demo-mcp-server-1 /bin/bash
```

#### 进入 chat-server 容器

```bash
docker exec -it fastmcp_demo-chat-server-1 /bin/bash
```

### 常用调试命令

#### 1. 检查 FastMCP 实例属性

在 mcp-server 容器中检查 FastMCP 实例的结构：

```bash
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp.server.fastmcp import FastMCP
mcp = FastMCP('Test')
print('app:', hasattr(mcp, 'app'))
print('_app:', hasattr(mcp, '_app'))
print('sse_app:', hasattr(mcp, 'sse_app'))
print('streamable_http_app:', hasattr(mcp, 'streamable_http_app'))
print('包含 app 的属性:', [x for x in dir(mcp) if 'app' in x.lower()])
"
```

**输出示例：**
```
app: False
_app: False
sse_app: True
streamable_http_app: True
包含 app 的属性: ['sse_app', 'streamable_http_app']
```

#### 2. 检查 Python 环境和依赖

```bash
# 检查 Python 版本
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python --version

# 检查已安装的包
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/pip list

# 检查特定包
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/pip show fastmcp
```

#### 3. 检查日志配置

```bash
# 在容器内测试日志格式化器
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
import logging
import json
from mcp_server import MCPProtocolFormatter

formatter = MCPProtocolFormatter('%(message)s')
record = logging.LogRecord(
    name='test',
    level=logging.DEBUG,
    pathname='',
    lineno=0,
    msg='Test JSON: %s',
    args=('{\"key\": \"value\"}',),
    exc_info=None
)
print(formatter.format(record))
"
```

#### 4. 检查 MCP 工具注册

```bash
# 检查工具是否正确注册
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import mcp
print('FastMCP 实例:', mcp)
print('工具数量:', len([x for x in dir(mcp) if not x.startswith('_')]))
"
```

#### 5. 测试工具函数

```bash
# 直接测试工具函数
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import calculate_expression
result = calculate_expression('10 + 20 * 2')
print('计算结果:', result)
"
```

#### 6. 检查网络连接

```bash
# 从 chat-server 容器测试连接到 mcp-server
docker exec fastmcp_demo-chat-server-1 /bin/bash -c "
curl -v http://mcp-server:8100/sse 2>&1 | head -20
"

# 从 mcp-server 容器测试自身
docker exec fastmcp_demo-mcp-server-1 /bin/bash -c "
curl -v http://localhost:8100/sse 2>&1 | head -20
"
```

#### 7. 查看实时日志

```bash
# 查看 mcp-server 日志
docker logs -f fastmcp_demo-mcp-server-1

# 查看 chat-server 日志
docker logs -f fastmcp_demo-chat-server-1

# 同时查看两个服务的日志
docker-compose logs -f
```

#### 8. 检查环境变量

```bash
# 查看 mcp-server 环境变量
docker exec fastmcp_demo-mcp-server-1 env

# 查看 chat-server 环境变量
docker exec fastmcp_demo-chat-server-1 env
```

#### 9. 检查文件系统

```bash
# 检查模型文件是否存在
docker exec fastmcp_demo-chat-server-1 ls -lh /app/models/

# 检查虚拟环境
docker exec fastmcp_demo-mcp-server-1 ls -la /app/.venv/bin/ | head -20

# 检查代码文件
docker exec fastmcp_demo-mcp-server-1 cat /app/mcp_server.py | head -50
```

### 调试技巧

1. **使用交互式 Python Shell**：
   ```bash
   docker exec -it fastmcp_demo-mcp-server-1 /app/.venv/bin/python
   ```
   然后在 Python shell 中导入模块进行交互式调试：
   ```python
   >>> from mcp_server import mcp
   >>> import inspect
   >>> print(inspect.getmembers(mcp))
   ```

2. **修改代码并重新加载**：
   - 如果使用 Docker volumes 挂载代码，修改后容器会自动检测变化（如果使用开发模式）
   - 或者需要重启容器：`docker-compose restart mcp-server`

3. **启用更详细的日志**：
   - 在容器内修改日志级别或添加临时日志语句
   - 查看格式化后的日志输出

4. **网络调试**：
   - 使用 `curl` 或 `wget` 测试 HTTP 端点
   - 检查端口是否开放：`netstat -tlnp`（如果可用）

### 常见问题排查

#### 问题：容器无法启动

```bash
# 查看容器启动日志
docker logs fastmcp_demo-mcp-server-1

# 检查容器状态
docker ps -a | grep fastmcp_demo
```

#### 问题：模块导入错误

```bash
# 检查 Python 路径
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "import sys; print(sys.path)"

# 检查模块是否可以导入
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "import mcp_server; print('导入成功')"
```

#### 问题：工具调用失败

```bash
# 直接测试工具函数
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import add_numbers, multiply_numbers, calculate_expression
print('add_numbers(2, 3):', add_numbers(2, 3))
print('multiply_numbers(4, 5):', multiply_numbers(4, 5))
print('calculate_expression(\"10+20*2\"):', calculate_expression('10+20*2'))
"
```

---

**提示**：以上命令可以帮助快速定位问题。如果遇到无法解决的问题，可以查看完整的容器日志或联系维护者。
