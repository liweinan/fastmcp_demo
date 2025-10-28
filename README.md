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

```bash
# 构建 Docker 镜像
docker-compose build

# 启动服务
docker-compose up
```

服务将在 `http://localhost:8000` 启动。

### 3. 测试接口

#### 健康检查
```bash
curl http://localhost:8000/health
```

#### 查看可用工具
```bash
curl http://localhost:8000/tools
```

#### 聊天测试
```bash
# 简单加法
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 25 + 17"}'

# 乘法运算
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 8 乘以 9"}'

# 表达式计算
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 (10 + 5) * 3"}'
```

## 项目结构

```
fastmcp_demo/
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # Docker Compose 配置
├── requirements.txt        # Python 依赖
├── server.py              # MCP 服务器 + HTTP API
├── tools.py               # 工具定义
└── README.md              # 使用说明
```

## 技术栈

- **MCP 框架**: fastmcp
- **AI 模型**: Qwen2-1.5B-Instruct-GGUF
- **推理引擎**: llama-cpp-python
- **Web 框架**: Flask
- **容器化**: Docker + Docker Compose

## 模型信息

- **模型**: Qwen2-1.5B-Instruct
- **参数量**: 1.5B
- **量化**: Q4_K_M (约1.2GB)
- **支持**: 中英文、工具调用
- **推理**: CPU 推理，无需 GPU

## 注意事项

1. 首次启动需要下载模型文件，请确保网络连接正常
2. 模型文件较大（约1.2GB），请确保有足够的磁盘空间
3. CPU 推理速度较慢，首次响应可能需要几秒钟
4. 建议在 64GB 内存环境下运行以获得最佳性能

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

### 模型文件不存在
确保模型文件已正确下载到 `./models/` 目录下。

### 内存不足
如果遇到内存不足，可以尝试：
- 减少 `n_ctx` 参数（在 server.py 中）
- 使用更小的量化版本模型

### 端口冲突
如果 8000 端口被占用，可以在 `docker-compose.yml` 中修改端口映射。
