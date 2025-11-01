# FastMCP 极简示例

这是一个基于 FastMCP 的极简示例，包含简单的计算工具和本地部署的小型语言模型。

## 功能特性

- 🤖 **真实的LLM推理**：本地部署的 Qwen2-1.5B 语言模型，实际调用进行推理
- 💬 **友好对话**：支持自然语言对话，可以友好地回复问候和闲聊
- 🛠️ **智能工具调用**：自动识别计算需求并调用相应工具（加法、乘法、表达式计算）
- 🐳 Docker 容器化部署
- 🌐 HTTP API 接口，支持 curl 交互
- ⚡ 基于 llama.cpp 的 CPU 推理
- 🛡️ 完善的错误处理和友好的错误提示

## 快速开始

### 1. 下载模型

首先需要手动下载模型文件。在项目根目录下执行：

```bash
# 创建模型目录
mkdir -p models

# 下载 Qwen2-1.5B 模型（约1.2GB）
wget -O models/qwen2-1_5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2-1.5B-Instruct-GGUF/resolve/main/qwen2-1_5b-instruct-q4_k_m.gguf
```

或者使用 huggingface-cli：

```bash
# 安装 huggingface-cli
pip install huggingface_hub

# 下载模型
huggingface-cli download Qwen/Qwen2-1.5B-Instruct-GGUF qwen2-1_5b-instruct-q4_k_m.gguf --local-dir ./models
```

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

服务将在 `http://localhost:8000` 启动。

### 3. 测试接口

#### 健康检查
```bash
curl http://localhost:8000/health
```
**预期输出**:
```json
{"mode":"real","model_loaded":true,"status":"healthy"}
```

**注意**：如果 `model_loaded` 为 `false` 或 `mode` 为 `not_loaded`，说明模型文件未找到，需要先下载模型文件。

#### 查看可用工具
```bash
curl http://localhost:8000/tools
```
**预期输出**:
```json
{
  "tools": {
    "add": {"description": "两数相加", "name": "add", "parameters": {...}},
    "multiply": {"description": "两数相乘", "name": "multiply", "parameters": {...}},
    "calculate": {"description": "计算简单数学表达式", "name": "calculate", "parameters": {...}}
  }
}
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
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 简单加法（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 8",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 乘法运算（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 4 * 7"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 28", 
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 表达式计算（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 2+3*4"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 14",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 复杂表达式（工具调用）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 3 * 7"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 21",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 非计算消息（自然语言回复）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "今天天气如何"}' | jq .
# 预期输出:
# {
#   "response": "今天的天气取决于你所在的地方，你可以告诉我你在哪里吗？",
#   "tools_available": ["add", "multiply", "calculate"]
# }
```

**功能说明**：
- 🧮 **计算请求**：当用户询问数学计算问题时，LLM会自动调用相应的工具进行计算
- 💬 **友好对话**：当用户问候或闲聊时，LLM会以自然语言友好回复
- 🔍 **智能识别**：LLM会自动识别用户意图，决定是使用工具还是直接回复

**替代方案**（如果系统没有安装 `jq`）：
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | python3 -m json.tool
```

## Project Architecture

### 🔍 架构关系

```
Flask HTTP Server → llama-cpp-python → Qwen2 Model
       ↓
   FastMCP Server → Tool Execution Layer
```

**关键说明**：
- Flask 直接调用 llama-cpp-python 进行 LLM 推理
- FastMCP 只负责工具注册和执行，不参与 LLM 调用
- LLM 和 FastMCP 是平行关系，都通过 Flask 协调

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastMCP Demo Architecture                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User (curl)   │    │   Docker Host   │    │  GitHub Repo    │
│                 │    │                 │    │                 │
│ curl POST       │    │ ./models/       │    │ fastmcp_demo/   │
│ /chat           │    │ ├── qwen2-*.gguf│    │ ├── server.py   │
│                 │    │                 │    │ ├── tools.py    │
└─────────────────┘    └─────────────────┘    │ ├── Dockerfile  │
         │                       │            │ ├── docker-     │
         │                       │            │ │   compose.yml │
         │                       │            │ └── README.md   │
         │                       │            └─────────────────┘
         │                       │                     │
         │                       │                     │ git clone
         │                       │                     │
         ▼                       ▼                     ▼
┌───────────────────────────────────────────────────────────────┐
│                    Docker Container                           │
│                                                               │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   Flask HTTP    │    │   llama-cpp-    │                   │
│  │   API Server    │    │   python        │                   │
│  │   (Port 8000)   │    │                 │                   │
│  │                 │    │                 │                   │
│  │ /health         │    │ CPU Inference   │                   │
│  │ /chat           │    │ n_threads=4     │                   │
│  │ /tools          │    │ n_ctx=2048      │                   │
│  └─────────────────┘    └─────────────────┘                   │
│           │                       │                           │
│           │                       │                           │
│           ▼                       ▼                           │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   FastMCP       │    │   Qwen2-1.5B    │                   │
│  │   Server        │    │   Model         │                   │
│  │                 │    │                 │                   │
│  │ Tool Registry   │    │ GGUF Format     │                   │
│  │ Tool Calling    │    │ ~1.2GB          │                   │
│  │ MCP Protocol    │    │ Volume Mount    │                   │
│  └─────────────────┘    └─────────────────┘                   │
│           │                       │                           │
│           │                       │                           │
│           ▼                       ▼                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Tool Execution Layer                       │  │
│  │  (add, multiply, calculate functions)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘

Data Flow:
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│User Req │───▶│HTTP API │───▶│LLM Infr │───▶│MCP Tool │───▶│Tool Exec│
│"25+17"  │    │Flask    │    │Qwen2    │    │Call     │    │add()    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│Response │◀───│JSON Resp│◀───│Tool Res │◀───│MCP Exec │◀───│Calc Res │
│"42"     │    │Format   │    │Parse    │    │FastMCP  │    │42       │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## 项目结构

```
fastmcp_demo/
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose 配置
├── requirements.txt        # Python 依赖
├── install.sh             # 自动安装脚本（处理代理配置）
├── build.sh               # 构建脚本（支持环境变量配置）
├── env.example            # 环境配置示例文件
├── server.py              # MCP 服务器 + HTTP API
├── tools.py               # 工具定义
├── models/                # 模型文件目录（Volume 挂载）
└── README.md              # 使用说明
```

## 技术栈

- **MCP 框架**: 自定义实现（基于工具调用模式）
- **AI 模型**: Qwen2-1.5B-Instruct-GGUF（必需）
- **推理引擎**: llama-cpp-python（基于 llama.cpp）
- **LLM 库**: llama-cpp-python >= 0.2.0
- **包管理**: uv（快速 Python 包管理器）
- **Web 框架**: Flask
- **容器化**: Docker + Docker Compose
- **代理处理**: 自动代理配置脚本

## 模型信息

- **模型**: Qwen2-1.5B-Instruct
- **参数量**: 1.5B
- **量化**: Q4_K_M (约1.2GB)
- **支持**: 中英文、工具调用
- **推理**: CPU 推理，无需 GPU

## 运行模式

项目**默认使用真实LLM模式**，需要下载模型文件才能运行。模型文件会在启动时自动加载，并进行真实的推理计算。

### 真实LLM模式（默认）
项目使用真实的 Qwen2 模型进行推理：
- ✅ **真实LLM推理**：使用 llama-cpp-python 实际调用模型
- ✅ **智能工具调用**：LLM自动识别计算需求并调用工具
- ✅ **友好对话**：支持自然语言对话，可以友好回复问候和闲聊
- ✅ **错误处理**：完善的参数验证和错误提示
- ⚠️ **需要模型文件**：必须下载模型文件到 `./models/` 目录才能运行

如果模型文件不存在，服务将无法启动并显示错误信息。

## 注意事项

1. **模型文件必需**: 必须下载模型文件（约1.2GB）到 `./models/` 目录，否则服务无法启动
2. **内存要求**: 建议至少 4GB 可用内存，8GB 以上更佳
3. **网络连接**: 首次下载模型需要良好的网络连接
4. **代理环境**: 企业网络环境需要配置代理，详见构建说明
5. **请求格式**: 使用 curl 时请确保JSON使用英文引号，例如 `'{"message": "你好"}'`

## 大模型使用原理

### 1. 模型加载
```python
llm = Llama(
    model_path=model_path,  # Qwen2-1.5B GGUF文件
    n_ctx=2048,            # 上下文长度2048 tokens
    n_threads=4,           # 使用4个CPU线程
    verbose=False
)
```

### 2. 系统提示构建
大模型被"教导"如何使用工具和进行友好对话：
- 告诉模型它是一个友善的数学计算助手
- 明确区分计算问题和一般对话的处理方式
- 列出所有可用工具（add、multiply、calculate）及其详细参数
- 指定工具调用的JSON格式
- 提供具体的工具调用示例

### 3. 对话处理流程
当用户发送消息时：

#### a) 构建对话消息
```python
messages = [
    {"role": "system", "content": system_prompt},  # 系统角色：定义行为
    {"role": "user", "content": user_message}      # 用户角色：具体问题
]
```

#### b) 调用大模型
```python
response = llm.create_chat_completion(
    messages=messages,
    temperature=0.7,    # 较高温度，让回复更自然友好
    max_tokens=512      # 限制输出长度
)
```

### 4. 响应处理与工具调用
大模型返回的内容会被智能处理：

1. **响应解析**：尝试从LLM响应中提取工具调用JSON
   - 支持多种JSON格式（代码块、纯JSON、嵌入JSON）
   - 使用多种策略提取和解析JSON对象
   
2. **工具调用检测**：判断响应是否包含工具调用
   - 如果包含有效的工具调用，提取工具名和参数
   - 验证参数完整性和类型正确性
   - 执行对应的计算函数
   - 返回计算结果
   
3. **自然语言回复**：如果没有工具调用
   - 直接返回LLM的自然语言响应
   - 清理可能的格式标记
   - 提供友好的对话体验

### 5. 完整工作流程示例

当用户发送 `"计算 25 + 17"` 时：

1. **大模型分析**：理解用户需要加法运算
2. **生成工具调用**：
   ```json
   {"tool": "add", "arguments": {"a": 25, "b": 17}}
   ```
3. **解析并执行**：调用 `add(25, 17)` 函数
4. **返回结果**：`"计算结果: 42"`

### 6. 关键特点

- **本地推理**：模型完全在本地运行，无需网络（除了初始下载）
- **CPU优化**：使用 llama.cpp 进行高效的CPU推理，无需GPU
- **智能工具调用**：大模型可以智能识别计算需求并自动调用工具
- **友好对话**：支持自然语言对话，可以友好地回复问候和闲聊
- **错误处理**：完善的参数验证、JSON解析和错误提示机制
- **双模式响应**：根据用户意图智能选择工具调用或自然语言回复

这种设计让大模型不仅能够理解和生成文本，还能主动调用工具来执行具体的计算任务，同时保持友好的对话体验，实现了"思考+行动+对话"的智能助手模式。

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
1. 确保已下载模型文件到 `./models/qwen2-1_5b-instruct-q4_k_m.gguf`
2. 检查文件路径是否正确（相对路径为 `./models/`）
3. 验证文件权限，确保可读
4. 查看服务器日志了解详细错误信息

### 内存不足
如果遇到内存不足，可以尝试：
- 减少 `n_ctx` 参数（在 server.py 中，默认2048）
- 减少 `n_threads` 参数（在 server.py 中，默认4）
- 使用更小的量化版本模型（如 Q2_K 或 Q3_K_M）
- 关闭其他占用内存的程序

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
如果 8000 端口被占用，可以在 `docker-compose.yml` 中修改端口映射。

### 构建失败
如果 Docker 构建失败：
1. 检查网络连接
2. 确认代理配置正确
3. 尝试清理 Docker 缓存：`docker system prune -a`
4. 使用 `--no-cache` 重新构建
