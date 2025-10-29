# FastMCP 极简示例

这是一个基于 FastMCP 的极简示例，包含简单的计算工具和本地部署的小型语言模型。

## 功能特性

- 🤖 本地部署的 Qwen2-1.5B 语言模型
- 🛠️ 简单的数学计算工具（加法、乘法、表达式计算）
- 🐳 Docker 容器化部署
- 🌐 HTTP API 接口，支持 curl 交互
- ⚡ 基于 llama.cpp 的 CPU 推理

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
{"mode":"mock","model_loaded":true,"status":"healthy"}
```

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

**注意**: 如果中文显示为 Unicode 转义字符（如 `\u6211`），可以使用 `jq` 或 `python3 -m json.tool` 来正确显示：

```bash
# 简单加法
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 5 + 3"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 8",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 乘法运算
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 4 * 7"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 28", 
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 表达式计算
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 2+3*4"}' | jq .
# 预期输出:
# {
#   "response": "计算结果: 5",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 非计算消息
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，今天天气怎么样？"}' | jq .
# 预期输出:
# {
#   "response": "我收到了你的消息: 你好，今天天气怎么样？。这是一个模拟的AI回复。",
#   "tools_available": ["add", "multiply", "calculate"]
# }

# 英文消息
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "tell me todays date"}' | jq .
# 预期输出:
# {
#   "response": "我收到了你的消息: tell me todays date。这是一个模拟的AI回复。",
#   "tools_available": ["add", "multiply", "calculate"]
# }
```

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
- **AI 模型**: Qwen2-1.5B-Instruct-GGUF（可选）
- **推理引擎**: llama-cpp-python（真实模式）/ 模式匹配（模拟模式）
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

### 模拟模式（默认）
项目默认运行在**模拟模式**下，无需下载模型文件即可体验功能：
- ✅ 支持所有计算工具（add、multiply、calculate）
- ✅ 通过简单的模式匹配识别计算请求
- ✅ 快速响应，适合演示和测试
- ⚠️ 不支持复杂的自然语言理解

### 真实模型模式
要使用真实的 Qwen2 模型：
1. 下载模型文件到 `./models/` 目录
2. 修改 `server.py` 中的 `load_model()` 函数
3. 重新构建容器

## 注意事项

1. **模拟模式**: 无需下载模型文件，可直接体验功能
2. **真实模式**: 首次启动需要下载模型文件（约1.2GB），请确保网络连接正常
3. **内存要求**: 建议在 64GB 内存环境下运行以获得最佳性能
4. **代理环境**: 企业网络环境需要配置代理，详见构建说明

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
大模型被"教导"如何使用工具：
- 告诉模型它是一个数学计算助手
- 列出所有可用工具（add、multiply、calculate）
- 指定工具调用的JSON格式

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
    temperature=0.1,    # 低温度，更确定性的输出
    max_tokens=512      # 限制输出长度
)
```

### 4. 工具调用解析与执行
大模型返回的内容会被解析：

1. **检测工具调用**：查找 ````json` 格式的工具调用
2. **解析JSON**：提取工具名和参数
3. **执行工具**：调用对应的计算函数
4. **返回结果**：将计算结果返回给用户

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

- **本地推理**：模型完全在本地运行，无需网络
- **CPU优化**：使用 llama.cpp 进行高效的CPU推理
- **工具集成**：大模型可以智能选择和使用预定义工具
- **对话式**：支持多轮对话，保持上下文

这种设计让大模型不仅能够理解和生成文本，还能主动调用工具来执行具体的计算任务，实现了"思考+行动"的智能助手模式。

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
- **模拟模式**：无需模型文件，可直接运行
- **真实模式**：确保模型文件已正确下载到 `./models/` 目录下

### 内存不足
如果遇到内存不足，可以尝试：
- 减少 `n_ctx` 参数（在 server.py 中）
- 使用更小的量化版本模型
- 使用模拟模式（无需模型文件）

### 端口冲突
如果 8000 端口被占用，可以在 `docker-compose.yml` 中修改端口映射。

### 构建失败
如果 Docker 构建失败：
1. 检查网络连接
2. 确认代理配置正确
3. 尝试清理 Docker 缓存：`docker system prune -a`
4. 使用 `--no-cache` 重新构建
