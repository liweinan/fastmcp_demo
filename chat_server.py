"""
FastAPI Chat Server - Uses LlamaIndex to automatically handle tool calls
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management: startup and shutdown"""
    # Initialize on startup
    try:
        await init_agent()
        logger.info("Chat server started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield  # Application running
    
    # Cleanup resources on shutdown
    logger.info("Chat server is shutting down...")

app = FastAPI(title="FastMCP Chat Server", lifespan=lifespan)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent instance
agent: Optional[ReActAgent] = None
# MCP server URL
mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8100")
# SSE endpoint URL (FastMCP uses SSE protocol)
mcp_sse_url = f"{mcp_server_url}/sse"

# Request models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    raw_response: str  # Raw complete response
    tools_available: List[str]

async def init_agent():
    """Initialize LlamaIndex Agent"""
    global agent
    
    # 1. Load Llama model
    model_path = find_model_file()
    
    logger.info(f"Loading model: {model_path}")
    logger.info(f"Context length: 4096, CPU threads: 6")
    
    # Use LlamaIndex's LlamaCPP wrapper
    # LlamaCPP automatically wraps the underlying llama-cpp-python
    llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=256,  # Increase generation length to ensure complete response
        context_window=4096,
        verbose=False,
        # Underlying llama-cpp-python parameters passed through model_kwargs
        model_kwargs={
            "n_threads": 6,
            "n_predict": 256,  # Increase predicted token count to ensure complete response
        },
    )
    logger.info("Model loaded successfully")
    
    # 2. Connect to FastMCP server to get tools
    logger.info(f"Connecting to MCP server: {mcp_sse_url}")
    tools = []
    
    # Wait for MCP server to start (retry logic)
    max_retries = 15
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Use BasicMCPClient to create client (supports SSE URL)
            # BasicMCPClient automatically detects SSE endpoint (URL ends with /sse)
            logger.debug(f"Attempting to create MCP client connection to: {mcp_sse_url}")
            client = BasicMCPClient(command_or_url=mcp_sse_url, timeout=10)
            # Create McpToolSpec
            tool_spec = McpToolSpec(client=client)
            # Use async method to get tool list in async environment
            logger.debug("Getting tool list...")
            tools = await tool_spec.to_tool_list_async()
            logger.info(f"MCP server connected successfully, found {len(tools)} tools: {[t.metadata.name for t in tools]}")
            break  # Successfully connected, exit retry loop
            
        except Exception as e:
            # Handle exceptions (including ExceptionGroup)
            error_msg = f"{type(e).__name__}: {str(e)}"
            # If ExceptionGroup, extract all exception information
            if hasattr(e, 'exceptions'):
                errors = []
                for exc in e.exceptions:
                    errors.append(f"{type(exc).__name__}: {str(exc)}")
                error_msg = "; ".join(errors)
            
            if attempt < max_retries - 1:
                logger.info(f"Waiting for MCP server to start... (attempt {attempt + 1}/{max_retries}, error: {error_msg})")
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.warning(f"MCP server connection failed: {error_msg}, will try to continue startup (tools may be unavailable)")
                import traceback
                logger.error(f"MCP connection detailed error:\n{traceback.format_exc()}")
                tools = []

    # 3. Create ReActAgent (automatically handles tool calls)
    # System prompt clearly guides Agent on when to use tools
    # Note: For non-mathematical questions (like greetings), reply directly without using any tools
    system_prompt = """You are a friendly math calculation assistant.

CRITICAL RULES - Must strictly follow:
1. If the user says a greeting (like "hello", "hi", etc.), reply friendly directly, absolutely do not call any tools
2. If the user's question does not involve mathematical calculation, answer directly, do not call tools
3. Only use tools when the user explicitly requests mathematical calculation
4. **Most important**: Call at most one tool per request. After getting the tool result, must immediately return the final answer and end processing, absolutely do not call any tools again or continue iterating

Workflow (strictly follow):
- Step 1: Analyze user request, decide if calculation is needed
- Step 2: If calculation is needed, call one tool (add_numbers, multiply_numbers, or calculate_expression)
- Step 3: After getting tool result, immediately generate final reply and end, format as: "The answer is [result]" or "Calculation result is [result]"
- **Never proceed to Step 4**: Do not call tools again, do not continue iterating

Available tools (only use when mathematical calculation is needed, and each calculation can only be called once):
- add_numbers(a, b): Add two numbers
- multiply_numbers(a, b): Multiply two numbers
- calculate_expression(expression): Calculate mathematical expression (only supports numbers and basic operators, like +-*/)

Correct examples (these are just explanations, do not execute):
- If user says greeting → Reply friendly directly, do not use tools
- If user says "calculate X + Y" → Call add_numbers(X, Y) once, get result and immediately reply and end
- If user says "X * Y" → Call multiply_numbers(X, Y) once, get result and immediately reply and end
- If user provides mathematical expression string → Call calculate_expression(expression) once, get result and immediately reply and end

**Absolutely forbidden**:
- Calling any tools again after calling a tool
- Continuing iteration after getting tool result
- Calling multiple tools for the same calculation problem"""
    
    agent = ReActAgent(
        tools=tools if tools else None,
        llm=llm,
        verbose=True,  # Enable verbose logging to view tool call process
        system_prompt=system_prompt
    )
    
    logger.info("Agent initialization complete, tool calls will be automatically handled by LlamaIndex")

def find_model_file() -> str:
    """Get model file path"""
    models_dir = "./models"
    default_filename = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    default_path = os.path.join(models_dir, default_filename)
    
    # If file found, validate and return
    if os.path.exists(default_path):
        # Validate file size
        try:
            file_size = os.path.getsize(default_path)
            if file_size < 100 * 1024 * 1024:  # At least 100MB
                raise FileNotFoundError(
                    f"Model file size abnormal: {default_path} (size: {file_size} bytes)\n"
                    f"Please check if the file is downloaded completely. Model file should be at least 100MB.\n"
                    f"Please re-download the model file, refer to README.md for model download instructions."
                )
            return default_path
        except OSError as e:
            raise FileNotFoundError(
                f"Cannot access model file: {default_path}\n"
                f"Error: {e}"
            )
    
    # If not found, raise error
    raise FileNotFoundError(
        f"Model file does not exist: {default_path}\n"
        f"Please download Llama 3.1 8B model file first.\n"
        f"Refer to README.md for model download instructions.\n"
        f"Default filename: {default_filename}"
    )

async def get_tool_names() -> List[str]:
    """Get list of available tool names"""
    # Prefer getting tool list from Agent (avoid duplicate MCP connections)
    if agent is not None and hasattr(agent, 'tools') and agent.tools:
        return [tool.metadata.name if hasattr(tool, 'metadata') else str(tool) for tool in agent.tools]
    
    # If Agent has no tools, try to get from MCP
    try:
        client = BasicMCPClient(command_or_url=mcp_sse_url)
        tool_spec = McpToolSpec(client=client)
        tools = await tool_spec.to_tool_list_async()
        return [t.metadata.name for t in tools]
    except Exception as e:
        logger.warning(f"Failed to get tool list: {e}")
        return []

@app.get("/health")
async def health():
    """Health check"""
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
    """Chat endpoint"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"Received message: {request.message}")
        
        # Input validation: check if message is empty or too short
        message = request.message.strip()
        if not message or len(message) < 2:
            tool_names = await get_tool_names()
            raw_response = "Input message is too short or empty"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # Use whitelist: only call LLM if contains "addition/subtraction/multiplication/division/calculation"
        user_message_lower = message.lower()
        # Math keywords in both Chinese and English for detection
        math_keywords = ['计算', '算', '加', '减', '乘', '除', '等于', '等于多少', '+', '-', '*', '/', 'calculate', 'compute', 'add', 'multiply', 'divide']
        has_math_content = any(keyword in user_message_lower for keyword in math_keywords) or \
                          any(char.isdigit() for char in user_message_lower)
        
        # If no math content, reply friendly directly without calling Agent
        if not has_math_content:
            logger.info("No mathematical calculation content detected, replying directly without calling Agent")
            tool_names = await get_tool_names()
            raw_response = "Non-mathematical question - direct reply, Agent not called"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # Use LlamaIndex Agent to process request (automatically handles tool calls)
        # ReActAgent is based on Workflow, need to use run() method
        # Use new Context to ensure each request is independent, no history retained
        from llama_index.core.workflow import Context
        from llama_index.core.memory import ChatMemoryBuffer
        from llama_index.core.workflow.errors import WorkflowRuntimeError
        
        # Create new memory and context, ensure each request is independent
        # ChatMemoryBuffer needs to set token_limit
        memory = ChatMemoryBuffer(token_limit=3000)
        ctx = Context(agent)
        
        # Set maximum iteration count (reduce iterations to avoid long wait times)
        handler = agent.run(
            user_msg=message, 
            memory=memory, 
            ctx=ctx,
            max_iterations=3  # Reduced to 3, simple calculations usually only need 1 iteration
        )
        
        # Wait for workflow to complete and get result (add timeout)
        try:
            result = await asyncio.wait_for(handler, timeout=120.0)  # Increased to 120 seconds timeout, as generating more tokens takes longer
        except asyncio.TimeoutError:
            logger.warning("Agent processing timeout (120 seconds)")
            tool_names = await get_tool_names()
            raw_response = "Timeout error: Agent processing exceeded 120 seconds"
            return ChatResponse(
                raw_response=raw_response,
                tools_available=tool_names
            )
        
        # Get raw response text
        if hasattr(result, 'response') and hasattr(result.response, 'content'):
            raw_response = result.response.content or ""
        else:
            raw_response = str(result)
        
        # Use raw response directly, no extraction processing
        # Get available tool list
        tool_names = await get_tool_names()
        
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )
    except WorkflowRuntimeError as e:
        # Handle error when maximum iteration count reached
        error_msg = str(e)
        logger.warning(f"Agent reached maximum iteration count: {error_msg}")
        tool_names = await get_tool_names()
        raw_response = f"Error: {error_msg}"
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        tool_names = await get_tool_names()
        raw_response = f"Error details: {str(e)}"
        return ChatResponse(
            raw_response=raw_response,
            tools_available=tool_names
        )

@app.get("/tools")
async def list_tools():
    """List available tools"""
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
        logger.error(f"Failed to get tool list: {e}")
        return {"tools": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
