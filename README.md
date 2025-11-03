# FastMCP 极简示例

这是一个基于 FastMCP 的极简示例，展示了如何构建一个完整的工具调用系统：
- **FastMCP 服务器**：暴露计算工具接口（通过 MCP 协议和 SSE 传输）
- **FastAPI Chat 服务器**：提供聊天服务，LLM 通过 MCP 客户端调用 FastMCP 工具

<img width="3840" height="2110" alt="b076f65573ef5b15190df9424cd20a12" src="https://github.com/user-attachments/assets/30232728-9b46-4393-8a54-8b09b26f685b" />

## 相关项目：

- https://github.com/fastapi/fastapi
- https://github.com/jlowin/fastmcp
- https://github.com/ggml-org/llama.cpp
- https://github.com/run-llama/llama_index

## 使用模型

- https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF

## 参考文档

- https://developers.llamaindex.ai/python/examples/agent/react_agent/
- https://www.ibm.com/think/topics/react-agent
- https://modelcontextprotocol.io/docs/getting-started/intro
- https://hackteam.io/blog/your-llm-does-not-care-about-mcp/
- https://medium.com/@infin94/kickstart-your-research-instantly-generate-synthetic-text-data-with-llama-3-1-56eaee6fbf48
- https://levelup.gitconnected.com/how-i-built-a-tool-calling-llama-agent-with-a-custom-mcp-server-3bc057d27e85
- https://www.anthropic.com/news/model-context-protocol
- https://github.com/Kludex/starlette

## 功能特性

- 🤖 **真实的LLM推理**：使用 Llama 3.1 8B 语言模型（支持原生tool_calls）
- 💬 **友好对话**：支持自然语言对话，可以友好地回复问候和闲聊
- 🛠️ **智能工具调用**：使用 LlamaIndex ReActAgent 自动处理工具调用，LLM 通过 MCP 协议调用 FastMCP 服务器提供的工具
- 🔌 **FastMCP 集成**：使用 FastMCP 框架暴露工具，通过 SSE 协议提供工具接口
- 🐳 Docker 容器化部署：支持多服务架构（FastMCP 服务器 + Chat 服务器）
- 🌐 HTTP API 接口，支持 curl 交互
- ⚡ 基于 llama.cpp 的 CPU 推理
- 🛡️ 完善的错误处理和友好的错误提示

## 快速开始

### 1. 下载模型

项目使用 **Llama 3.1 8B-Instruct** 模型（支持原生tool_calls）。

**特点**：
- 模型大小：约4.6GB
- 内存需求：约8GB RAM
- 工具调用：原生tool_calls支持，通过LlamaIndex自动处理
- 推理速度：中等
- **优势**：工具调用更准确、更可靠，上下文理解更好

**下载方法**：

**重要**：Meta官方版本（`meta-llama/Llama-3.1-8B-Instruct`）需要登录认证。  
**推荐**：使用社区公开量化版本（无需认证，功能相同）：

```bash
# 方法1：使用wget直接下载（推荐，最简单）
mkdir -p models
# 从bartowski下载（公开版本，无需认证，约4.6GB）
wget -O models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# 注意：文件名必须为 Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf，否则服务无法启动

# 方法2：使用huggingface-cli（bartowski版本，无需登录）
pip install huggingface_hub
huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \
  --include "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" --local-dir ./models
```

**备选公开源**（都无需认证，按下载量排序）：
- `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF`（95k+下载，推荐）
- `MaziyarPanahi/Meta-Llama-3.1-8B-Instruct-GGUF`（76.2k下载）
- `QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF`（55.5k下载）

**说明**：
- 文件大小约4.6GB，确保有足够的磁盘空间
- 模型文件名固定为：`Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
- 文件必须放在 `./models/` 目录下

### 2. 构建和启动

#### 方法一：使用构建脚本（推荐）
```bash
# 1. 配置代理（可选）
cp env.example .env
# 编辑 .env 文件，设置你的代理配置

# 2. 使用构建脚本
./build.sh

# 3. 启动服务
docker-compose up
```

#### 方法二：手动构建
```bash
# 无代理环境
docker-compose build
docker-compose up

# 企业代理环境
export PROXY_URL=http://your-proxy:port
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
export NO_PROXY=localhost,127.0.0.1

docker-compose build --build-arg proxy_url=$PROXY_URL --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY --build-arg no_proxy=$NO_PROXY
docker-compose up
```

#### 配置说明
- **PROXY_URL**: 代理服务器地址（如 `http://proxy.company.com:8080`）
- **HTTP_PROXY/HTTPS_PROXY**: Docker 构建时的代理设置
- **NO_PROXY**: 不使用代理的地址列表

**注意**: 项目包含自动代理配置脚本 `install.sh`，会根据环境变量自动处理容器内部的代理设置。

服务将在以下地址启动：
- **FastMCP 服务器**：`http://localhost:8100`（提供工具接口）
- **Chat 服务器**：`http://localhost:8000`（提供聊天服务）

**启动验证**：
启动后查看日志，应该看到：
- `正在加载模型: ./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
- `模型加载完成`
- `MCP服务器连接成功，发现 3 个工具`
- `Agent初始化完成，工具调用将由LlamaIndex自动处理`

**运行时日志**：
- LlamaIndex会自动处理工具调用，日志会显示工具调用过程
- 使用 `verbose=True` 可以看到详细的工具调用和响应信息

**注意**：
- 需要先下载Llama 3.1 8B模型文件（约4.6GB）
- 工具调用由LlamaIndex ReActAgent自动处理，无需手工解析
- 支持原生tool_calls，无需文本解析
- Agent最大迭代次数设置为10次，避免响应时间过长
- 响应包含简洁答案（`response`）和完整原始输出（`raw_response`）

### 4. 测试接口

#### 健康检查
```bash
curl http://localhost:8000/health
```
**预期输出**:
```json
{"status":"healthy","agent_loaded":true,"mcp_available":true,"tools_count":3}
```

**注意**：如果 `agent_loaded` 为 `false`，说明模型文件未找到或Agent初始化失败，需要先下载模型文件。

#### 查看可用工具

**注意**：FastMCP 服务器使用 SSE 协议（`/sse` 端点），不能直接通过 curl 访问。工具列表通过 Chat 服务器提供的 HTTP API 获取。

**从 Chat 服务器获取工具列表**：
```bash
curl http://localhost:8000/tools
```

#### 聊天测试

**注意**: 
1. 如果中文显示为 Unicode 转义字符（如 `\u6211`），可以使用 `jq` 或 `python3 -m json.tool` 来正确显示
2. 请确保使用**英文引号**，而不是中文引号（""）

```bash
# 问候对话（自然语言回复）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}' | jq .
# 预期输出:
# {
#   "response": "你好！有什么我可以帮助你的吗？",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# 简单加法（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | jq .
# 预期输出:
# {
#   "response": "8",  # 提取后的简洁答案
#   "raw_response": "Thought: ... Answer: 8 ...",  # 完整的Agent输出
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# 乘法运算（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 4 * 7"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 28", 
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# 表达式计算（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 2+3*4"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 14",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# 复杂表达式（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 3 * 7"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 21",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }

# 非计算消息（自然语言回复）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "今天天气如何"}' | jq .
# 预期输出:
# {
#   "response": "今天的天气取决于你所在的地方，你可以告诉我你在哪里吗？",
#   "tools_available": ["add_numbers", "multiply_numbers", "calculate_expression"]
# }
```

**功能说明**：
- 🧮 **计算请求**：当用户询问数学计算问题时，LLM会自动调用相应的工具进行计算
- 💬 **友好对话**：当用户问候或闲聊时，LLM会以自然语言友好回复（不会调用工具）
- 🔍 **智能识别**：LLM会自动识别用户意图，决定是使用工具还是直接回复
- ⚡ **快速响应**：最大迭代次数限制为10次，确保响应时间合理
- 📝 **双重响应**：返回简洁答案（`response`）和完整原始输出（`raw_response`）

**替代方案**（如果系统没有安装 `jq`）：
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | python3 -m json.tool
```

## Project Architecture

### 🔍 架构关系

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

**关键说明**：
- **FastMCP 服务器**（端口8100）：通过 `@mcp.tool()` 装饰器注册工具，提供 SSE 端点（`/sse`）暴露 MCP 协议接口
- **FastAPI Chat 服务器**（端口8000）：使用 llama-cpp-python 进行 LLM 推理，通过 MCP 客户端（BasicMCPClient）连接 FastMCP 服务器的 SSE 端点
- **工作流程**：用户请求 → Chat 服务器 → LLM 分析 → MCP 协议（SSE）调用 FastMCP 工具 → 返回结果 → LLM 生成最终回复

### 🚀 数据流示例

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

## 项目结构

```
fastmcp_demo/
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose 配置（两个服务：mcp-server + chat-server）
├── pyproject.toml          # Python 项目配置和依赖（使用 uv 管理）
├── install.sh             # 自动安装脚本（处理代理配置）
├── build.sh               # 构建脚本（支持环境变量配置）
├── start_servers.sh       # 本地启动脚本（同时启动两个服务）
├── env.example            # 环境配置示例文件
├── mcp_server.py          # FastMCP 服务器（端口8100）
├── chat_server.py         # FastAPI Chat 服务器（端口8000）
├── models/                # 模型文件目录（Volume 挂载）
└── README.md              # 使用说明
```

## 技术栈

- **FastMCP 框架**: FastMCP >= 0.1.0（MCP 协议实现）
- **MCP 协议**: Model Context Protocol（工具调用协议）
- **LlamaIndex**: >= 0.10.0（自动处理工具调用的Agent框架）
- **AI 模型**: Llama 3.1 8B-Instruct-GGUF（支持原生tool_calls）
- **推理引擎**: llama-cpp-python（基于 llama.cpp）
- **LLM 库**: llama-cpp-python >= 0.2.0
- **Web 框架**: FastAPI >= 0.104.0（Chat 服务器）
- **HTTP 客户端**: httpx >= 0.25.0（MCP 客户端）
- **ASGI 服务器**: uvicorn >= 0.24.0
- **容器化**: Docker + Docker Compose
- **代理处理**: 自动代理配置脚本

## 模型信息

### Llama 3.1 8B-Instruct（默认，推荐）

- **参数量**: 8B
- **量化**: Q4_K_M (约4.6GB)
- **内存需求**: 约8GB RAM
- **工具调用**: **更强的工具调用能力**（工具调用更准确可靠）
- **推理**: CPU 推理，无需 GPU
- **速度**: 中等（但工具调用更可靠）
- **优势**: 更好的工具调用能力，更准确可靠


## 运行模式

项目**默认使用真实LLM模式**，需要下载模型文件才能运行。模型文件会在启动时自动加载，并进行真实的推理计算。

### 真实LLM模式（默认）
项目使用真实的 Llama 3.1 8B 模型进行推理：
- ✅ **真实LLM推理**：使用 llama-cpp-python 实际调用模型
- ✅ **智能工具调用**：使用LlamaIndex ReActAgent自动处理工具调用
- ✅ **原生tool_calls支持**：Llama 3.1 8B支持原生tool_calls，无需文本解析
- ✅ **友好对话**：支持自然语言对话，可以友好回复问候和闲聊
- ✅ **错误处理**：完善的参数验证和错误提示
- ⚠️ **需要模型文件**：必须下载模型文件到 `./models/` 目录才能运行

如果模型文件不存在，服务将无法启动并显示错误信息。

## 注意事项

1. **模型文件必需**: 必须下载Llama 3.1 8B模型文件（约4.6GB）到 `./models/` 目录，否则服务无法启动
2. **内存要求**: 建议至少 8GB 可用内存（模型约需要8GB RAM）
3. **网络连接**: 首次下载模型需要良好的网络连接
4. **代理环境**: 企业网络环境需要配置代理，详见构建说明
5. **请求格式**: 使用 curl 时请确保JSON使用英文引号，例如 `'{"message": "你好"}'`
6. **工具调用**: 工具调用由LlamaIndex自动处理，无需手工解析或配置

## 大模型使用原理

### 1. 架构概览

项目采用**双服务器架构**：
- **FastMCP 服务器**（`mcp_server.py`）：通过 `@mcp.tool()` 装饰器注册工具，通过 SSE 协议（`/sse` 端点）暴露 MCP 协议接口
- **Chat 服务器**（`chat_server.py`）：使用 llama-cpp-python 进行 LLM 推理，通过 MCP 客户端（BasicMCPClient）连接 FastMCP 服务器的 SSE 端点

### 2. FastMCP 服务器

```python
# 创建 FastMCP 实例
mcp = FastMCP("MathTools")

# 注册工具
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """两数相加"""
    return add(a, b)

# 启动服务器（通过 SSE 传输协议）
# FastMCP 工具注册后，通过 SSE 端点 (/sse) 自动暴露 MCP 协议接口
mcp.run(transport="sse")
```

**FastMCP 服务器功能**：
- 通过 `@mcp.tool()` 装饰器注册工具（`add_numbers`, `multiply_numbers`, `calculate_expression`）
- 使用 SSE 传输协议提供 MCP 协议接口：
  - SSE 端点：`http://0.0.0.0:8100/sse`
  - 工具列表和调用通过 MCP 协议自动暴露
- FastMCP 框架通过 SSE 协议自动处理工具注册和调用

### 3. Chat 服务器与 LLM 推理（使用LlamaIndex自动处理）

#### a) 模型加载和Agent初始化
```python
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.tools.mcp import McpToolSpec, BasicMCPClient
from llama_index.core.agent import ReActAgent

# 加载Llama模型
llm = LlamaCPP(
    model_path=model_path,  # Llama 3.1 8B GGUF文件
    temperature=0.1,
    max_new_tokens=256,
    context_window=4096,
    model_kwargs={"n_threads": 6},
)

# 连接到FastMCP服务器获取工具（通过SSE端点）
mcp_sse_url = "http://localhost:8100/sse"
client = BasicMCPClient(command_or_url=mcp_sse_url, timeout=10)
tool_spec = McpToolSpec(client=client)
tools = await tool_spec.to_tool_list_async()  # 异步获取工具列表

# 创建ReActAgent（自动处理工具调用）
agent = ReActAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True,
    system_prompt="你是一个友善的数学计算助手..."
)
```

#### b) 工具调用流程（自动处理）

**LlamaIndex ReActAgent自动处理所有工具调用**：

```python
# 用户请求
handler = agent.run(
    user_msg="计算 25 + 17",
    memory=ChatMemoryBuffer(token_limit=3000),
    ctx=Context(agent),
    max_iterations=10  # 最大迭代次数，避免响应时间过长
)
result = await handler

# LlamaIndex会自动：
# 1. 分析用户请求
# 2. 决定是否需要调用工具
# 3. 如果需要，生成tool_calls（原生格式）
# 4. 执行工具调用
# 5. 将结果反馈给LLM
# 6. 生成最终回复
```

**优势**：
- ✅ 无需手工解析工具调用
- ✅ 自动处理原生tool_calls格式
- ✅ 支持多轮工具调用
- ✅ 完善的错误处理和重试机制
- ✅ 智能响应提取：从完整输出中提取简洁答案
- ✅ 迭代次数限制：最大10次迭代，避免长时间等待

### 4. 完整工作流程示例

当用户发送 `"计算 25 + 17"` 时：

1. **用户请求** → Chat 服务器（`POST /chat`）
2. **LlamaIndex Agent分析**：ReActAgent自动决定需要调用工具
3. **生成tool_calls**：Agent生成原生格式的tool_calls（`add_numbers(a=25, b=17)`）
4. **自动执行工具**：LlamaIndex通过MCP协议调用FastMCP工具
5. **FastMCP 执行工具**：调用 `add_numbers(25, 17)` → 返回 `42`
6. **生成最终回复**：Agent将结果反馈给LLM，生成友好回复
7. **返回最终结果**：`"计算结果: 42"`

### 5. 为什么使用LlamaIndex？

**重要说明**：使用LlamaIndex框架自动处理工具调用，无需手工解析。

#### LlamaIndex的优势

1. **自动处理工具调用**
   - ✅ 自动识别何时需要调用工具
   - ✅ 自动处理原生tool_calls格式
   - ✅ 无需手工解析文本或JSON

2. **完善的Agent架构**
   - ✅ ReActAgent实现了思考-行动-观察循环
   - ✅ 支持多轮工具调用
   - ✅ 自动处理工具执行结果

3. **与MCP协议深度集成**
   - ✅ `McpToolSpec`自动从FastMCP服务器获取工具
   - ✅ 支持SSE协议通信
   - ✅ 自动转换工具格式

#### 关键特点

- **MCP 协议**：使用 FastMCP 框架标准化的工具调用方式
- **LlamaIndex集成**：通过LlamaIndex自动处理所有工具调用逻辑
- **双服务器架构**：工具服务器和聊天服务器分离，职责清晰
- **原生tool_calls支持**：Llama 3.1 8B支持原生tool_calls，LlamaIndex自动处理
- **本地推理**：模型完全在本地运行，无需网络（除了初始下载）
- **CPU优化**：使用 llama.cpp 进行高效的CPU推理，无需GPU

## 故障排除

### 代理相关问题
如果在企业网络环境中遇到连接问题：

1. **使用配置文件**（推荐）：
   ```bash
   cp env.example .env
   # 编辑 .env 文件，设置正确的代理地址
   ./build.sh
   ```

2. **手动设置环境变量**：
   ```bash
   export PROXY_URL=http://your-proxy:port
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ./build.sh
   ```

3. **检查代理连通性**：
   ```bash
   curl -I --proxy $PROXY_URL https://pypi.org
   ```

4. **重新构建**：
   ```bash
   docker-compose build --no-cache --build-arg proxy_url=$PROXY_URL --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY
   ```

### 模型文件不存在
如果服务启动失败，提示模型文件不存在：
1. 确保已下载模型文件到 `./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
2. 检查文件路径是否正确（相对路径为 `./models/`）
3. 验证文件权限，确保可读
4. 查看服务器日志了解详细错误信息

### 内存不足
如果遇到内存不足，可以尝试：
- 减少 `n_ctx` 参数（在 server.py 中，默认2048）
- 减少 `n_threads` 参数（在 server.py 中，默认4）
- 使用更小的量化版本模型（如 Q2_K 或 Q3_K_M）
- 关闭其他占用内存的程序

### 超时和性能调优
如果遇到超时错误（"Agent 处理超时"），可以根据硬件配置调整以下参数：

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
