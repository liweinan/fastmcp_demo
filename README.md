# FastMCP 极简示例

这是一个基于 FastMCP 的极简示例，展示了如何构建一个完整的工具调用系统：
- **FastMCP 服务器**：暴露计算工具接口（通过 MCP 协议和 SSE 传输）
- **FastAPI Chat 服务器**：提供聊天服务，LLM 通过 MCP 客户端调用 FastMCP 工具

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
