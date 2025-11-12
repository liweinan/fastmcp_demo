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
  -d '{"message": "Hello"}' | jq .
# Expected output:
# {
#   "raw_response": "Hello! How can I help you?",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Simple addition (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 5 + 3"}' | jq .
# Expected output:
# {
#   "raw_response": "Thought: ... Answer: 8 ...",  # Complete Agent output
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Multiplication (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 4 * 7"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 28", 
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Expression calculation (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 2+3*4"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 14",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Complex expression (tool call)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 3 * 7"}' | jq .
# Expected output:
# {
#   "raw_response": "Calculation result: 21",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# Non-calculation message (natural language reply)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather today?"}' | jq .
# Expected output:
# {
#   "raw_response": "The weather today depends on your location. Can you tell me where you are?",
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
  -d '{"message": "Calculate 5 + 3"}' | python3 -m json.tool
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
5. **Request Format**: When using curl, ensure JSON uses English quotes, e.g., `'{"message": "Hello"}'`
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

#### 1. Adjust Token Generation Parameters (chat_server.py)

**Location**: `chat_server.py` lines 79-90

```python
llm = LlamaCPP(
    model_path=model_path,
    temperature=0.1,
    max_new_tokens=256,  # Adjustable: 128-512, larger value generates more content but takes longer
    context_window=4096,
    verbose=False,
    model_kwargs={
        "n_threads": 6,      # Adjustable: Set based on CPU cores, recommend physical core count
        "n_predict": 256,    # Should match max_new_tokens
    },
)
```

**Adjustment Recommendations**:
- **Fast Response** (Lower CPU): `max_new_tokens=128`, `n_predict=128`
- **Balanced** (Medium CPU): `max_new_tokens=256`, `n_predict=256` (default)
- **Complete Response** (High Performance CPU): `max_new_tokens=512`, `n_predict=512`

#### 2. Adjust Timeout (chat_server.py)

**Location**: `chat_server.py` line 299

```python
result = await asyncio.wait_for(handler, timeout=120.0)  # Adjustable: 60-300 seconds
```

**Adjustment Recommendations**:
- **Fast Hardware** (8+ cores CPU, high frequency): 60-90 seconds
- **Medium Hardware** (4-6 cores CPU): 120 seconds (default)
- **Slower Hardware** (2-4 cores CPU, low frequency): 180-300 seconds

**Calculation Formula** (rough estimate):
```
Timeout ≈ (max_new_tokens / 10) + Tool call time (5-10 seconds)
```

Example: `max_new_tokens=256` → Timeout ≈ 25-35 seconds + 5-10 seconds ≈ 30-45 seconds (actually recommend setting to 2-3 times, i.e., 60-120 seconds)

#### 3. Adjust Agent Iteration Count (chat_server.py)

**Location**: `chat_server.py` line 294

```python
max_iterations=3  # Adjustable: 1-5, simple calculations usually only need 1 iteration
```

**Adjustment Recommendations**:
- **Simple Calculations**: `max_iterations=1-2` (faster response)
- **Complex Problems**: `max_iterations=3-5` (allows multiple tool calls)

#### 4. Performance Optimization Recommendations

**Choose Parameter Combinations Based on Hardware Configuration**:

| CPU Cores | Recommended max_new_tokens | Recommended timeout | Recommended n_threads |
|-----------|---------------------------|---------------------|----------------------|
| 2-4 cores | 128                       | 180-240 seconds     | 2-4                  |
| 4-6 cores | 256                       | 120-180 seconds     | 4-6                  |
| 6-8 cores | 256-512                   | 90-120 seconds      | 6-8                  |
| 8+ cores  | 512                       | 60-90 seconds       | 8+                   |

**Notes**:
- Parameters take effect after service restart
- If frequent timeouts, prioritize reducing `max_new_tokens` rather than increasing `timeout`
- CPU inference is slow, this is normal, consider using GPU acceleration to significantly improve performance

### System Prompt Configuration

If encountering Agent behavior that doesn't meet expectations (such as frequent tool calls, loop calls, etc.), you can adjust or remove system_prompt:

#### Role of System Prompt

**Location**: `chat_server.py` lines 138-166

Main roles of current system_prompt:
1. **Limit Tool Call Count**: Clearly instructs "call at most one tool per request" to avoid loop calls
2. **Clarify Usage Scenarios**: Only use tools for mathematical calculations, greetings and casual chat do not use tools
3. **Guide Agent Behavior**: Provides clear workflow and examples

#### Can System Prompt Be Removed?

**Yes, technically it can be removed.**

ReActAgent can work normally without `system_prompt`:

```python
agent = ReActAgent(
    tools=tools if tools else None,
    llm=llm,
    verbose=True,
    # system_prompt=system_prompt  # Can be commented out or deleted
)
```

Or set to `None`:

```python
agent = ReActAgent(
    tools=tools if tools else None,
    llm=llm,
    verbose=True,
    system_prompt=None  # Explicitly set to None
)
```

#### Impact of Removing System Prompt

**Still Works**:
- ✅ ReActAgent will use default system prompt
- ✅ Tool calling functionality works normally
- ✅ Basic reasoning ability not affected

**But There Will Be Behavioral Differences**:
- ⚠️ No clear tool call limits, Agent may call tools multiple times (may encounter loop call issues as before)
- ⚠️ No clear guidance on "call tool only once"
- ⚠️ No specific guidance for mathematical calculations, may try to call tools for any question
- ⚠️ May also try to call tools for greetings and casual chat

#### When Should System Prompt Be Kept?

**Recommend keeping** if encountering the following issues:
- Agent loops calling tools
- Agent calls tools in scenarios where it shouldn't (like greetings)
- Agent calls tools multiple times for the same question
- Want to strictly control Agent behavior

#### When Can System Prompt Be Removed?

Can consider removing if:
- Want Agent to have more flexible behavior
- Allow multiple tool calls (complex tasks require multiple steps)
- Default Agent behavior already meets requirements

**Conclusion**:
- ✅ **Technically Feasible**: Can run without `system_prompt`
- ⚠️ **Functionality May Be Affected**: May restore loop tool calling issues
- 💡 **Recommend Keeping**: Current `system_prompt` solved previous tool calling issues

### JSON Format Error
If encountering `400 Bad Request` or JSON format errors:
- Ensure to use **English quotes**, do not use Chinese quotes
- Check if JSON format is correct, e.g., `'{"message": "Hello"}'`
- Check detailed prompts and examples in error response
- Can use file method to send requests to avoid escape issues:
  ```bash
  echo '{"message": "Hello"}' | curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d @- | jq .
  ```

### Port Conflict
If port is occupied:
- **Port 8000 (Chat Server)**: Modify `chat-server` port mapping in `docker-compose.yml`
- **Port 8100 (FastMCP Server)**: Modify `mcp-server` port mapping in `docker-compose.yml`, and update `MCP_SERVER_URL` environment variable in `chat_server.py`

### FastMCP Server Connection Failed
If Chat server cannot connect to FastMCP server:
1. Ensure FastMCP server is started (`mcp-server` service)
2. Check if `MCP_SERVER_URL` environment variable is correct (use `http://mcp-server:8100` inside Docker, `http://localhost:8100` locally)
3. Check logs to confirm both services are running
4. Chat server will automatically retry connection on startup (up to 15 times, 2 seconds interval)

### Agent Reached Maximum Iteration Count
If encountering `Max iterations of 3 reached!` error:
1. **Normal Phenomenon**: Indicates Agent cannot complete task within 3 iterations
2. **Solutions**:
   - Break complex problems into simpler steps
   - Rephrase question to make it clearer and more explicit
   - Check if input has errors (like incomplete input)
3. **Response Format**: Even when reaching iteration limit, will return friendly error message

### Build Failed
If Docker build fails:
1. Check network connection
2. Confirm proxy configuration is correct
3. Try cleaning Docker cache: `docker system prune -a`
4. Rebuild with `--no-cache`

## MCP Protocol Interaction Analysis Report

This section is based on actual log output, providing detailed analysis of a complete MCP protocol interaction flow to help understand the communication process between chat-server and mcp-server.

### Request Scenario

User sends request to chat-server: `Calculate 10 + 20 * 2`

### Complete Interaction Flow

#### 1. SSE Connection Establishment

**chat-server → mcp-server**

```
chat-server-1  | 2025-11-03 04:18:30,522 - httpx - INFO - HTTP Request: GET http://mcp-server:8100/sse "HTTP/1.1 200 OK"
```

**mcp-server logs:**

```
mcp-server-1   | 2025-11-03 04:18:30,520 - mcp.server.sse - DEBUG - Setting up SSE connection
mcp-server-1   | 2025-11-03 04:18:30,520 - mcp.server.sse - DEBUG - Created new session with ID: bdd2d4d9-feb5-4331-8891-f4a747248ee1
mcp-server-1   | 2025-11-03 04:18:30,521 - mcp.server.sse - DEBUG - Starting SSE response task
mcp-server-1   | INFO:     172.21.0.3:39074 - "GET /sse HTTP/1.1" 200 OK
```

**Explanation**: chat-server establishes SSE long connection through GET request, mcp-server creates new session and returns session ID.

---

#### 2. Initialization Phase (initialize)

**chat-server → mcp-server** (POST /messages/)

```
chat-server-1  | 2025-11-03 04:18:30,524 - httpx - INFO - HTTP Request: POST http://mcp-server:8100/messages/?session_id=bdd2d4d9feb543318891f4a747248ee1 "HTTP/1.1 202 Accepted"
```

**mcp-server logs - receiving request:**

```
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Handling POST message
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Parsed session ID: bdd2d4d9-feb5-4331-8891-f4a747248ee1
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"mcp","version":"0.1.0"}},"jsonrpc":"2.0","id":0}'
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='initialize', params={'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'mcp', 'version': '0.1.0'}}, jsonrpc='2.0', id=0)
```

**mcp-server → chat-server** (returns response via SSE stream)

```
mcp-server-1   | 2025-11-03 04:18:30,524 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=0, result={'protocolVersion': '2025-06-18', 'capabilities': {...}, 'serverInfo': {'name': 'MathTools', 'version': '1.20.0'}})), metadata=None)
```

**Formatted response (via log formatter):**

```
mcp-server-1   | 2025-11-03 04:18:30,524 - sse_starlette.sse - DEBUG - [SSE Chunk - Formatted]
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

**Explanation**:
- chat-server sends `initialize` request, containing protocol version and client information
- mcp-server returns server capability information and server information (name, version)

---

#### 3. Initialization Complete Notification (notifications/initialized)

**chat-server → mcp-server**

```
mcp-server-1   | 2025-11-03 04:18:30,526 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"notifications/initialized","jsonrpc":"2.0"}'
mcp-server-1   | 2025-11-03 04:18:30,526 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCNotification(method='notifications/initialized', params=None, jsonrpc='2.0')
```

**Explanation**: chat-server notifies mcp-server that initialization is complete (this is the standard MCP protocol flow).

---

#### 4. Tool List Query (tools/list)

**chat-server → mcp-server**

```
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"tools/list","jsonrpc":"2.0","id":1}'
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='tools/list', params=None, jsonrpc='2.0', id=1)
```

**mcp-server processing request:**

```
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - DEBUG - Dispatching request of type ListToolsRequest
mcp-server-1   | 2025-11-03 04:18:30,530 - mcp.server.lowlevel.server - DEBUG - Response sent
```

**mcp-server → chat-server** (returns tool list)

```
mcp-server-1   | 2025-11-03 04:18:30,531 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=1, result={'tools': [...]})))
```

**Formatted tool list response:**

```
mcp-server-1   | {
mcp-server-1   |   "jsonrpc": "2.0",
mcp-server-1   |   "id": 1,
mcp-server-1   |   "result": {
mcp-server-1   |     "tools": [
mcp-server-1   |       {
mcp-server-1   |         "name": "add_numbers",
mcp-server-1   |         "description": "Calculate the sum of two numbers.\nImportant: Only use this tool when the user explicitly requests addition calculation...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       },
mcp-server-1   |       {
mcp-server-1   |         "name": "multiply_numbers",
mcp-server-1   |         "description": "Calculate the product of two numbers.\nImportant: Only use this tool when the user explicitly requests multiplication calculation...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       },
mcp-server-1   |       {
mcp-server-1   |         "name": "calculate_expression",
mcp-server-1   |         "description": "Calculate a mathematical expression. The expression must only contain numbers and basic operators...",
mcp-server-1   |         "inputSchema": {...},
mcp-server-1   |         "outputSchema": {...}
mcp-server-1   |       }
mcp-server-1   |     ]
mcp-server-1   |   }
mcp-server-1   | }
```

**Explanation**:
- chat-server requests tool list
- mcp-server returns all available tools with their descriptions, input/output schemas
- Tool descriptions contain usage scenario explanations to help Agent decide when to use which tool

---

#### 5. Tool Call (tools/call)

**chat-server → mcp-server** (request to call `calculate_expression` tool)

```
mcp-server-1   | 2025-11-03 04:18:30,527 - mcp.server.sse - DEBUG - Received JSON: b'{"method":"tools/call","params":{"name":"calculate_expression","arguments":{"expression":"10 + 20 * 2"}},"jsonrpc":"2.0","id":1}'
mcp-server-1   | 2025-11-03 04:18:30,527 - mcp.server.sse - DEBUG - Validated client message: root=JSONRPCRequest(method='tools/call', params={'name': 'calculate_expression', 'arguments': {'expression': '10 + 20 * 2'}}, jsonrpc='2.0', id=1)
```

**mcp-server processing tool call:**

```
mcp-server-1   | 2025-11-03 04:18:30,528 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
mcp-server-1   | 2025-11-03 04:18:30,528 - mcp.server.lowlevel.server - DEBUG - Dispatching request of type CallToolRequest
mcp-server-1   | 2025-11-03 04:18:30,528 - __main__ - INFO - [FastMCP Tool] calculate_expression(expression='10 + 20 * 2')
mcp-server-1   | 2025-11-03 04:18:30,528 - __main__ - INFO - [FastMCP Tool] calculate_expression result: 50.0
mcp-server-1   | 2025-11-03 04:18:30,529 - mcp.server.lowlevel.server - DEBUG - Response sent
```

**mcp-server → chat-server** (returns tool execution result)

```
mcp-server-1   | 2025-11-03 04:18:30,529 - mcp.server.sse - DEBUG - Sending message via SSE: SessionMessage(message=JSONRPCMessage(root=JSONRPCResponse(jsonrpc='2.0', id=1, result={'content': [{'type': 'text', 'text': '50.0'}], 'structuredContent': {'result': 50.0}, 'isError': False})), metadata=None)
```

**Formatted tool call response:**

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

**Explanation**:
- chat-server (Agent) decides to call `calculate_expression` tool based on user request, parameter is `"10 + 20 * 2"`
- mcp-server executes tool function, calculation result is `50.0`
- mcp-server returns formatted result, containing both text format and structured format

---

#### 6. Final Response

**chat-server returns to user:**

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

### Key Findings

1. **Bidirectional Communication**:
   - chat-server → mcp-server: Sends JSON-RPC requests via `POST /messages/`
   - mcp-server → chat-server: Returns JSON-RPC responses via SSE stream

2. **Session Management**:
   - Each SSE connection has a unique `session_id`
   - All requests are associated with the same session through `?session_id=xxx` parameter

3. **Request-Response Matching**:
   - JSON-RPC protocol matches requests and responses through `id` field
   - For example: initialization request `id=0`, corresponding response is also `id=0`

4. **Tool Call Flow**:
   - Agent first gets tool list (understand available tools)
   - Agent analyzes user request, decides which tool to call
   - Agent sends `tools/call` request, containing tool name and parameters
   - mcp-server executes tool and returns result
   - Agent integrates result into final reply

5. **Role of Log Formatter**:
   - Automatically formats JSON-RPC messages for readability
   - Converts Unicode escape sequences to readable text
   - Formats JSON data in SSE chunks
   - Helps developers understand detailed MCP protocol interaction process

### Log Viewing Tips

1. **View Complete MCP Interaction**: Search for `Sending message via SSE` or `Received JSON` in mcp-server logs
2. **View Tool Execution**: Search for `[FastMCP Tool]` to view actual tool execution
3. **View Formatted JSON**: Search for `[SSE Chunk - Formatted]` to view formatted JSON responses
4. **Track Sessions**: Track all requests and responses of the same session through `session_id`

### Protocol Flow Diagram

```
User Request: "Calculate 10 + 20 * 2"
    ↓
chat-server (Agent)
    ↓
1. GET /sse (Establish SSE connection)
    ↓
2. POST /messages/ (initialize)
    ↓
3. POST /messages/ (notifications/initialized)
    ↓
4. POST /messages/ (tools/list) ← mcp-server returns tool list
    ↓
5. Agent analysis: Need to call calculate_expression
    ↓
6. POST /messages/ (tools/call) ← mcp-server executes tool and returns result
    ↓
7. Agent generates final reply
    ↓
Return to user: {"raw_response": "...", "tools_available": [...]}
```

---

**Note**: The above logs are based on DEBUG level log output. By default, MCP related logs are set to DEBUG level and use custom formatter for formatting, ensuring JSON data is output in readable format.

## Debugging and Container Commands

### Enter Container for Debugging

When you need to debug in depth or troubleshoot issues, you can enter the container to execute commands.

#### View Running Containers

```bash
docker ps
```

#### Enter mcp-server Container

```bash
docker exec -it fastmcp_demo-mcp-server-1 /bin/bash
```

#### Enter chat-server Container

```bash
docker exec -it fastmcp_demo-chat-server-1 /bin/bash
```

### Common Debugging Commands

#### 1. Check FastMCP Instance Attributes

Check FastMCP instance structure in mcp-server container:

```bash
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp.server.fastmcp import FastMCP
mcp = FastMCP('Test')
print('app:', hasattr(mcp, 'app'))
print('_app:', hasattr(mcp, '_app'))
print('sse_app:', hasattr(mcp, 'sse_app'))
print('streamable_http_app:', hasattr(mcp, 'streamable_http_app'))
print('Attributes containing app:', [x for x in dir(mcp) if 'app' in x.lower()])
"
```

**Output Example:**
```
app: False
_app: False
sse_app: True
streamable_http_app: True
Attributes containing app: ['sse_app', 'streamable_http_app']
```

#### 2. Check Python Environment and Dependencies

```bash
# Check Python version
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python --version

# Check installed packages
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/pip list

# Check specific package
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/pip show fastmcp
```

#### 3. Check Log Configuration

```bash
# Test log formatter inside container
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

#### 4. Check MCP Tool Registration

```bash
# Check if tools are correctly registered
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import mcp
print('FastMCP instance:', mcp)
print('Tool count:', len([x for x in dir(mcp) if not x.startswith('_')]))
"
```

#### 5. Test Tool Functions

```bash
# Directly test tool functions
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import calculate_expression
result = calculate_expression('10 + 20 * 2')
print('Calculation result:', result)
"
```

#### 6. Check Network Connection

```bash
# Test connection from chat-server container to mcp-server
docker exec fastmcp_demo-chat-server-1 /bin/bash -c "
curl -v http://mcp-server:8100/sse 2>&1 | head -20
"

# Test from mcp-server container to itself
docker exec fastmcp_demo-mcp-server-1 /bin/bash -c "
curl -v http://localhost:8100/sse 2>&1 | head -20
"
```

#### 7. View Real-time Logs

```bash
# View mcp-server logs
docker logs -f fastmcp_demo-mcp-server-1

# View chat-server logs
docker logs -f fastmcp_demo-chat-server-1

# View logs of both services simultaneously
docker-compose logs -f
```

#### 8. Check Environment Variables

```bash
# View mcp-server environment variables
docker exec fastmcp_demo-mcp-server-1 env

# View chat-server environment variables
docker exec fastmcp_demo-chat-server-1 env
```

#### 9. Check File System

```bash
# Check if model file exists
docker exec fastmcp_demo-chat-server-1 ls -lh /app/models/

# Check virtual environment
docker exec fastmcp_demo-mcp-server-1 ls -la /app/.venv/bin/ | head -20

# Check code files
docker exec fastmcp_demo-mcp-server-1 cat /app/mcp_server.py | head -50
```

### Debugging Tips

1. **Use Interactive Python Shell**:
   ```bash
   docker exec -it fastmcp_demo-mcp-server-1 /app/.venv/bin/python
   ```
   Then import modules in Python shell for interactive debugging:
   ```python
   >>> from mcp_server import mcp
   >>> import inspect
   >>> print(inspect.getmembers(mcp))
   ```

2. **Modify Code and Reload**:
   - If using Docker volumes to mount code, container will automatically detect changes (if using development mode)
   - Or need to restart container: `docker-compose restart mcp-server`

3. **Enable More Detailed Logs**:
   - Modify log level or add temporary log statements inside container
   - View formatted log output

4. **Network Debugging**:
   - Use `curl` or `wget` to test HTTP endpoints
   - Check if port is open: `netstat -tlnp` (if available)

### Common Issue Troubleshooting

#### Issue: Container Cannot Start

```bash
# View container startup logs
docker logs fastmcp_demo-mcp-server-1

# Check container status
docker ps -a | grep fastmcp_demo
```

#### Issue: Module Import Error

```bash
# Check Python path
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "import sys; print(sys.path)"

# Check if module can be imported
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "import mcp_server; print('Import successful')"
```

#### Issue: Tool Call Failed

```bash
# Directly test tool functions
docker exec fastmcp_demo-mcp-server-1 /app/.venv/bin/python -c "
from mcp_server import add_numbers, multiply_numbers, calculate_expression
print('add_numbers(2, 3):', add_numbers(2, 3))
print('multiply_numbers(4, 5):', multiply_numbers(4, 5))
print('calculate_expression(\"10+20*2\"):', calculate_expression('10+20*2'))
"
```

---

**Tip**: The above commands can help quickly locate issues. If you encounter unsolvable problems, you can check complete container logs or contact maintainers.
