"""
FastAPI Chat服务器 - 使用LlamaIndex自动处理工具调用
"""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llama_index.core.agent import ReActAgent
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.tools.mcp import McpToolSpec, BasicMCPClient

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
    response: str  # 提取后的简洁答案
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
        max_new_tokens=256,
        context_window=4096,
        verbose=False,
        # 底层llama-cpp-python的参数通过model_kwargs传递
        model_kwargs={
            "n_threads": 6,
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
            client = BasicMCPClient(command_or_url=mcp_sse_url, timeout=10)
            # 创建 McpToolSpec
            tool_spec = McpToolSpec(client=client)
            # 在异步环境中使用异步方法获取工具列表
            tools = await tool_spec.to_tool_list_async()
            logger.info(f"MCP服务器连接成功，发现 {len(tools)} 个工具: {[t.metadata.name for t in tools]}")
            break  # 成功连接，退出重试循环
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(f"等待MCP服务器启动... (尝试 {attempt + 1}/{max_retries}, 错误: {type(e).__name__})")
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.warning(f"MCP服务器连接失败: {e}，将尝试继续启动（工具可能不可用）")
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

可用工具（仅在需要数学计算时使用）：
- add_numbers(a, b): 两数相加
- multiply_numbers(a, b): 两数相乘  
- calculate_expression(expression): 计算数学表达式（仅支持数字和基本运算符，如 +-*/）

正确示例：
- 用户："你好" → 回复："你好！我是数学计算助手，可以帮你进行数学计算。"（不使用工具）
- 用户："计算 5 + 3" → 使用工具：add_numbers(5, 3)
- 用户："2 * 4" → 使用工具：multiply_numbers(2, 4)
- 用户："2+3*4" → 使用工具：calculate_expression("2+3*4")

记住：问候和闲聊绝对不要调用工具！"""
    
    agent = ReActAgent(
        tools=tools if tools else None,
        llm=llm,
        verbose=True,  # 启用详细日志以查看工具调用过程
        system_prompt=system_prompt
    )
    
    logger.info("Agent初始化完成，工具调用将由LlamaIndex自动处理")

def extract_final_answer(raw_response: str) -> str:
    """
    从原始响应中提取最终答案
    
    Args:
        raw_response: Agent 返回的原始响应文本
        
    Returns:
        提取后的简洁答案
    """
    import re
    
    if not raw_response:
        return ""
    
    original_text = raw_response
    
    # 方法1：查找最后一个 "Answer:" 后的内容
    if 'Answer:' in raw_response:
        parts = raw_response.rsplit('Answer:', 1)
        if len(parts) > 1:
            answer_section = parts[-1].strip()
            # 提取第一个简洁的答案（通常是数字或简短文本）
            lines = [line.strip() for line in answer_section.split('\n') if line.strip()]
            for line in lines[:3]:  # 只检查前3行
                # 如果这行是纯数字或很简短，可能就是答案
                cleaned = line.replace('$', '').replace('\\boxed{', '').replace('}', '').strip()
                if len(cleaned) < 30:
                    # 检查是否主要是数字
                    if re.match(r'^-?\d+\.?\d*$', cleaned) or len(cleaned.split()) < 5:
                        return cleaned
            
            # 如果没找到，尝试从 answer_section 中提取第一个数字
            numbers = re.findall(r'-?\d+\.?\d*', answer_section)
            if numbers:
                return numbers[0]
    
    # 方法2：如果响应仍然很长或包含多余内容，提取数值答案
    if len(raw_response) > 50 or 'Step' in raw_response or 'Thought' in raw_response:
        # 从整个响应中提取数字，优先使用最后出现的数字（通常是最终答案）
        all_numbers = re.findall(r'-?\d+\.?\d*', original_text)
        if all_numbers:
            # 使用最后一个数字（通常是最終答案）
            return all_numbers[-1]
        else:
            # 如果没有数字，尝试提取 "Answer:" 后的第一行
            if 'Answer:' in original_text:
                answer_part = original_text.split('Answer:')[-1].strip()
                first_line = answer_part.split('\n')[0].strip()
                # 清理 Markdown 和其他格式
                first_line = re.sub(r'[\\$`{}]', '', first_line).strip()
                if len(first_line) < 100:
                    return first_line
    
    # 如果无法提取，返回原始响应的前200个字符
    return raw_response[:200].strip() if len(raw_response) > 200 else raw_response.strip()

def find_model_file() -> str:
    """获取模型文件路径"""
    model_path = os.getenv("LLAMA_MODEL_PATH", None)
    
    # 如果指定了路径，直接使用
    if model_path and os.path.exists(model_path):
        return model_path
    
    # 如果未指定或路径不存在，尝试在 models 目录下查找
    models_dir = "./models"
    if model_path and not os.path.exists(model_path):
        # 指定的路径不存在，但先尝试查找
        pass
    
    # 可能的文件名模式（大小写不敏感）
    possible_names = [
        "llama-3.1-8b-instruct-q4_k_m.gguf",
        "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "llama-3.1-8b-instruct-q4_k_m.gguf.1",  # wget 下载可能带后缀
    ]
    
    # 在 models 目录下查找
    found_path = None
    if os.path.isdir(models_dir):
        import glob
        # 查找所有包含 "llama" 和 "q4_k_m" 的 .gguf 文件（不区分大小写）
        pattern = os.path.join(models_dir, "*llama*3.1*8b*q4_k_m*.gguf*")
        matches = glob.glob(pattern, recursive=False)
        if matches:
            # 选择第一个匹配的文件
            found_path = matches[0]
        else:
            # 如果没有找到，尝试精确匹配
            for name in possible_names:
                path = os.path.join(models_dir, name)
                if os.path.exists(path):
                    found_path = path
                    break
    
    # 如果找到了文件，验证并返回
    if found_path:
        # 验证文件大小
        try:
            file_size = os.path.getsize(found_path)
            if file_size < 100 * 1024 * 1024:  # 至少100MB
                raise FileNotFoundError(
                    f"模型文件大小异常: {found_path} (大小: {file_size} 字节)\n"
                    f"请检查文件是否下载完整。模型文件应该至少100MB。\n"
                    f"请重新下载模型文件，参考README.md中的模型下载说明。"
                )
            return found_path
        except OSError as e:
            raise FileNotFoundError(
                f"无法访问模型文件: {found_path}\n"
                f"错误: {e}"
            )
    
    # 如果都没找到，使用默认路径并报错
    default_path = "./models/llama-3.1-8b-instruct-q4_k_m.gguf"
    raise FileNotFoundError(
        f"模型文件不存在: {model_path or default_path}\n"
        f"请先下载Llama 3.1 8B模型文件。\n"
        f"参考README.md中的模型下载说明。\n"
        f"提示：已检查 models 目录，未找到匹配的模型文件。"
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
            return ChatResponse(
                response="请输入一个有效的问题或计算请求。",
                raw_response="输入消息过短或为空",
                tools_available=tool_names
            )
        
        # 预处理：检测问候语和非数学问题，直接回复（避免小模型过度工具调用）
        # 根据 instructions.md，小于 8B 的模型在提示中包含工具模式会导致不稳定
        user_message_lower = message.lower()
        greeting_keywords = ['你好', 'hello', 'hi', 'hey', 'hi there', 'greetings', '早上好', '下午好', '晚上好']
        is_greeting = any(keyword in user_message_lower for keyword in greeting_keywords)
        
        # 检测是否包含数学计算关键词
        math_keywords = ['计算', '算', '加', '减', '乘', '除', '等于', '等于多少', '+', '-', '*', '/', 'calculate', 'compute', 'add', 'multiply', 'divide']
        has_math_content = any(keyword in user_message_lower for keyword in math_keywords) or \
                          any(char.isdigit() for char in user_message_lower)
        
        # 如果是纯问候且不包含数学内容，直接友好回复，不调用 Agent
        if is_greeting and not has_math_content:
            logger.info("检测到问候语，直接回复，不调用 Agent")
            tool_names = await get_tool_names()
            return ChatResponse(
                response="你好！我是数学计算助手，可以帮助你进行数学计算。你可以问我：\n- 计算 5 + 3\n- 2 * 4 等于多少\n- 计算 10 + 20 * 2\n等等。",
                raw_response="问候语 - 直接回复，未调用 Agent",
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
            max_iterations=10  # 减少迭代次数，避免等待时间过长
        )
        
        # 等待 workflow 完成并获取结果
        result = await handler
        
        # 获取原始响应文本
        if hasattr(result, 'response') and hasattr(result.response, 'content'):
            raw_response = result.response.content or ""
        else:
            raw_response = str(result)
        
        # 提取最终答案
        final_answer = extract_final_answer(raw_response)
        
        # 获取可用工具列表
        tool_names = await get_tool_names()
        
        return ChatResponse(
            response=final_answer,
            raw_response=raw_response,
            tools_available=tool_names
        )
    except WorkflowRuntimeError as e:
        # 处理最大迭代次数达到的错误
        error_msg = str(e)
        logger.warning(f"Agent 达到最大迭代次数: {error_msg}")
        tool_names = await get_tool_names()
        return ChatResponse(
            response="抱歉，处理时间过长。请尝试：\n1. 重新表述您的问题\n2. 将复杂问题拆分为更简单的步骤\n3. 确保问题完整且清晰",
            raw_response=f"错误: {error_msg}",
            tools_available=tool_names
        )
    except Exception as e:
        logger.error(f"处理请求时出错: {e}", exc_info=True)
        tool_names = await get_tool_names()
        return ChatResponse(
            response=f"处理请求时出错: {str(e)}",
            raw_response=f"错误详情: {str(e)}",
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
