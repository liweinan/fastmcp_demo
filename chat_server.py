"""
FastAPI Chat服务器 - 使用LlamaIndex自动处理工具调用
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core.agent import ReActAgent
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动和关闭"""
    # 启动时初始化
    try:
        await init_agent()
        logger.info("Chat服务器启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise
    
    yield  # 应用运行中
    
    # 关闭时清理资源
    logger.info("Chat服务器正在关闭...")

app = FastAPI(title="FastMCP Chat Server", lifespan=lifespan)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent实例
agent: Optional[ReActAgent] = None
# MCP服务器URL
mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8100")
# SSE端点URL（FastMCP使用SSE协议）
mcp_sse_url = f"{mcp_server_url}/sse"

# 请求模型
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    raw_response: str  # 原始完整响应
    tools_available: List[str]

async def init_agent():
    """初始化LlamaIndex Agent"""
    global agent
    
    # 1. 加载Llama模型
    model_path = find_model_file()
    
    logger.info(f"正在加载模型: {model_path}")
    logger.info(f"上下文长度: 4096, CPU线程数: 6")
    
    # 使用LlamaIndex的LlamaCPP包装器
    # LlamaCPP会自动包装底层的llama-cpp-python
    llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=256,  # 增加生成长度，确保完整回复
        context_window=4096,
        verbose=False,
        # 底层llama-cpp-python的参数通过model_kwargs传递
        model_kwargs={
            "n_threads": 6,
            "n_predict": 256,  # 增加预测token数，确保完整回复
        },
    )
    logger.info("模型加载完成")
    
    # 2. 连接到FastMCP服务器获取工具
    logger.info(f"正在连接MCP服务器: {mcp_sse_url}")
    tools = []
    
    # 等待MCP服务器启动（重试逻辑）
    max_retries = 15
    retry_delay = 2  # 秒
    
    for attempt in range(max_retries):
        try:
            # 使用 BasicMCPClient 创建客户端（支持 SSE URL）
            # BasicMCPClient 会自动检测 SSE 端点（URL 以 /sse 结尾）
            logger.debug(f"尝试创建 MCP 客户端连接到: {mcp_sse_url}")
            client = BasicMCPClient(command_or_url=mcp_sse_url, timeout=10)
            # 创建 McpToolSpec
            tool_spec = McpToolSpec(client=client)
            # 在异步环境中使用异步方法获取工具列表
            logger.debug("正在获取工具列表...")
            tools = await tool_spec.to_tool_list_async()
            logger.info(f"MCP服务器连接成功，发现 {len(tools)} 个工具: {[t.metadata.name for t in tools]}")
            break  # 成功连接，退出重试循环
            
        except Exception as e:
            # 处理异常（包括 ExceptionGroup）
            error_msg = f"{type(e).__name__}: {str(e)}"
            # 如果是 ExceptionGroup，提取所有异常信息
            if hasattr(e, 'exceptions'):
                errors = []
                for exc in e.exceptions:
                    errors.append(f"{type(exc).__name__}: {str(exc)}")
                error_msg = "; ".join(errors)
            
            if attempt < max_retries - 1:
                logger.info(f"等待MCP服务器启动... (尝试 {attempt + 1}/{max_retries}, 错误: {error_msg})")
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.warning(f"MCP服务器连接失败: {error_msg}，将尝试继续启动（工具可能不可用）")
                import traceback
                logger.error(f"MCP连接详细错误:\n{traceback.format_exc()}")
                tools = []

    # 3. 创建ReActAgent（自动处理工具调用）
    # System prompt 明确指导 Agent 何时使用工具
    # 注意：对于非数学问题（如问候），应该直接回复，不要使用任何工具
    system_prompt = """你是一个友善的数学计算助手。

CRITICAL RULES - 必须严格遵守：
1. 如果用户说的是问候语（如"你好"、"hello"、"hi"等），直接友好回复，绝对不要调用任何工具
2. 如果用户的问题不涉及数学计算，直接回答，不要调用工具
3. 只有在用户明确要求进行数学计算时，才使用工具
4. **最重要**：每次请求最多只调用一次工具。调用工具得到结果后，必须立即返回最终答案并结束处理，绝对不要再调用任何工具或进行任何迭代

工作流程（严格遵守）：
- 步骤1：分析用户请求，决定是否需要计算
- 步骤2：如果需要计算，调用一次工具（add_numbers、multiply_numbers 或 calculate_expression）
- 步骤3：得到工具结果后，立即生成最终回复并结束，格式为："答案是 [结果]" 或 "计算结果为 [结果]"
- **绝对不要进入步骤4**：不要再次调用工具，不要继续迭代

可用工具（仅在需要数学计算时使用，且每种计算只能调用一次）：
- add_numbers(a, b): 两数相加
- multiply_numbers(a, b): 两数相乘  
- calculate_expression(expression): 计算数学表达式（仅支持数字和基本运算符，如 +-*/）

正确示例（这些只是说明，不要执行）：
- 如果用户说问候语 → 直接友好回复，不使用工具
- 如果用户说"计算 X + Y" → 调用一次 add_numbers(X, Y)，得到结果后立即回复并结束
- 如果用户说"X * Y" → 调用一次 multiply_numbers(X, Y)，得到结果后立即回复并结束
- 如果用户给出数学表达式字符串 → 调用一次 calculate_expression(表达式)，得到结果后立即回复并结束

**绝对禁止**：
- 调用工具后再次调用任何工具
- 在得到工具结果后继续迭代
- 对同一个计算问题调用多个工具"""
    
    agent = ReActAgent(
        tools=tools if tools else None,
        llm=llm,
        verbose=True,  # 启用详细日志以查看工具调用过程
        system_prompt=system_prompt
    )
    
    logger.info("Agent初始化完成，工具调用将由LlamaIndex自动处理")

def find_model_file() -> str:
    """获取模型文件路径"""
    models_dir = "./models"
    default_filename = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    default_path = os.path.join(models_dir, default_filename)
    
    # 如果找到了文件，验证并返回
    if os.path.exists(default_path):
        # 验证文件大小
        try:
            file_size = os.path.getsize(default_path)
            if file_size < 100 * 1024 * 1024:  # 至少100MB
                raise FileNotFoundError(
                    f"模型文件大小异常: {default_path} (大小: {file_size} 字节)\n"
                    f"请检查文件是否下载完整。模型文件应该至少100MB。\n"
                    f"请重新下载模型文件，参考README.md中的模型下载说明。"
                )
            return default_path
        except OSError as e:
            raise FileNotFoundError(
                f"无法访问模型文件: {default_path}\n"
                f"错误: {e}"
            )
    
    # 如果没找到，报错
    raise FileNotFoundError(
        f"模型文件不存在: {default_path}\n"
        f"请先下载Llama 3.1 8B模型文件。\n"
        f"参考README.md中的模型下载说明。\n"
        f"默认文件名: {default_filename}"
    )

async def get_tool_names() -> List[str]:
    """获取可用工具名称列表"""
    # 优先从 Agent 获取工具列表（避免重复连接 MCP）
    if agent is not None and hasattr(agent, 'tools') and agent.tools:
        return [tool.metadata.name if hasattr(tool, 'metadata') else str(tool) for tool in agent.tools]
    
    # 如果 Agent 没有工具，尝试从 MCP 获取
    try:
        client = BasicMCPClient(command_or_url=mcp_sse_url)
        tool_spec = McpToolSpec(client=client)
        tools = await tool_spec.to_tool_list_async()
        return [t.metadata.name for t in tools]
    except Exception as e:
        logger.warning(f"获取工具列表失败: {e}")
        return []

@app.get("/health")
async def health():
    """健康检查"""
    try:
        tool_names = await get_tool_names()
        mcp_available = len(tool_names) > 0
    except:
        mcp_available = False
        tool_names = []
    
    return {
        "status": "healthy",
        "agent_loaded": agent is not None,
        "mcp_available": mcp_available,
        "tools_count": len(tool_names)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent未初始化")
    
    try:
        logger.info(f"收到消息: {request.message}")
        
        # 输入验证：检查消息是否为空或过短
        message = request.message.strip()
        if not message or len(message) < 2:
            tool_names = await get_tool_names()
            raw_response = "输入消息过短或为空"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # 使用白名单：包含"加减乘除计算"的才调用大模型
        user_message_lower = message.lower()
        math_keywords = ['计算', '算', '加', '减', '乘', '除', '等于', '等于多少', '+', '-', '*', '/', 'calculate', 'compute', 'add', 'multiply', 'divide']
        has_math_content = any(keyword in user_message_lower for keyword in math_keywords) or \
                          any(char.isdigit() for char in user_message_lower)
        
        # 如果不包含数学内容，直接友好回复，不调用 Agent
        if not has_math_content:
            logger.info("未检测到数学计算内容，直接回复，不调用 Agent")
            tool_names = await get_tool_names()
            raw_response = "非数学问题 - 直接回复，未调用 Agent"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # 使用LlamaIndex Agent处理请求（自动处理工具调用）
        # ReActAgent 基于 Workflow，需要使用 run() 方法
        # 使用新的 Context 确保每次请求都是独立的，不保留历史
        from llama_index.core.workflow import Context
        from llama_index.core.memory import ChatMemoryBuffer
        from llama_index.core.workflow.errors import WorkflowRuntimeError
        
        # 创建新的内存和上下文，确保每次请求都是独立的
        # ChatMemoryBuffer 需要设置 token_limit
        memory = ChatMemoryBuffer(token_limit=3000)
        ctx = Context(agent)
        
        # 设置最大迭代次数（减少迭代避免等待时间过长）
        handler = agent.run(
            user_msg=message, 
            memory=memory, 
            ctx=ctx,
            max_iterations=3  # 减少到3次，简单计算通常只需要1次迭代
        )
        
        # 等待 workflow 完成并获取结果（添加超时）
        try:
            result = await asyncio.wait_for(handler, timeout=120.0)  # 增加到120秒超时，因为生成更多token需要更长时间
        except asyncio.TimeoutError:
            logger.warning("Agent 处理超时（120秒）")
            tool_names = await get_tool_names()
            raw_response = "超时错误: Agent 处理超过120秒"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # 获取原始响应文本
        if hasattr(result, 'response') and hasattr(result.response, 'content'):
            raw_response = result.response.content or ""
        else:
            raw_response = str(result)
        
        # 直接使用原始响应，不进行提取处理
        # 获取可用工具列表
        tool_names = await get_tool_names()
        
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )
    except WorkflowRuntimeError as e:
        # 处理最大迭代次数达到的错误
        error_msg = str(e)
        logger.warning(f"Agent 达到最大迭代次数: {error_msg}")
        tool_names = await get_tool_names()
        raw_response = f"错误: {error_msg}"
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )
    except Exception as e:
        logger.error(f"处理请求时出错: {e}", exc_info=True)
        tool_names = await get_tool_names()
        raw_response = f"错误详情: {str(e)}"
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )

@app.get("/tools")
async def list_tools():
    """列出可用工具"""
    try:
        client = BasicMCPClient(command_or_url=mcp_sse_url)
        tool_spec = McpToolSpec(client=client)
        tools = await tool_spec.to_tool_list_async()
        
        tools_list = []
        for tool in tools:
            tools_list.append({
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "parameters": tool.metadata.parameters_schema if hasattr(tool.metadata, 'parameters_schema') else {}
            })
        return {"tools": tools_list}
    except Exception as e:
        logger.error(f"获取工具列表失败: {e}")
        return {"tools": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
