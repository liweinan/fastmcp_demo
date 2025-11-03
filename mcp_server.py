"""
FastMCP服务器 - 暴露计算工具
FastMCP通过SSE端点自动暴露工具列表，无需手工实现
"""
import json
import logging
import re

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

# 配置日志 - 保持原有级别，但添加格式化器让输出更清晰
logging.basicConfig(
    level=logging.INFO,  # 基础日志级别设为 INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建自定义格式化器，用于格式化 MCP 协议相关日志
class MCPProtocolFormatter(logging.Formatter):
    """格式化 MCP 协议日志，使其更易读（中文友好、JSON 格式化，使用 Python json）"""
    
    def _format_json(self, json_str):
        """使用 Python json 模块格式化 JSON"""
        try:
            json_obj = json.loads(json_str)
            return json.dumps(json_obj, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            return json_str
    
    def format(self, record):
        # 先获取格式化后的消息（处理 %s 等占位符）
        try:
            message = record.getMessage()
        except TypeError:
            # 如果格式化失败，直接使用原始消息和参数
            message = record.msg
            if record.args:
                try:
                    message = message % record.args
                except:
                    message = str(record.msg) + ' ' + str(record.args)
        
        original_message = message
        
        # 格式化 JSON-RPC 消息（处理各种可能的格式）
        if any(keyword in message for keyword in ['JSONRPCMessage', 'SessionMessage', 'Sending message', 'Dispatching request', 'Processing request']):
            try:
                json_match = re.search(r'\{.*\}', message, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    formatted_json = self._format_json(json_str)
                    message = message.replace(json_str, '\n' + formatted_json)
            except:
                pass
        
        # 格式化 SSE chunk（处理二进制字符串）
        if 'chunk:' in message:
            try:
                # 匹配 chunk: %s 格式（处理占位符）
                # 如果 record.args 存在且包含数据，直接处理 args
                if record.args and len(record.args) > 0:
                    chunk_data = record.args[0]
                    if isinstance(chunk_data, bytes):
                        try:
                            chunk_str = chunk_data.decode('utf-8', errors='replace')
                            # 查找 JSON（可能在 data: 之后）
                            if 'data:' in chunk_str:
                                data_part = chunk_str.split('data:', 1)[-1].strip()
                                json_match = re.search(r'\{.*\}', data_part, re.DOTALL)
                            else:
                                json_match = re.search(r'\{.*\}', chunk_str, re.DOTALL)
                            
                            if json_match:
                                json_str = json_match.group(0)
                                formatted_json = self._format_json(json_str)
                                message = f"[SSE Chunk - 已格式化]\n{formatted_json}"
                        except:
                            pass
                else:
                    # 尝试从消息字符串中提取
                    chunk_patterns = [
                        r"chunk: b'([^']+)'",
                        r"chunk: b\"([^\"]+)\"",
                        r"chunk: ([^\n]+)"
                    ]
                    for pattern in chunk_patterns:
                        chunk_match = re.search(pattern, message)
                        if chunk_match:
                            chunk_data = chunk_match.group(1)
                            try:
                                decoded = bytes(chunk_data, 'utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                                if 'data:' in decoded:
                                    data_part = decoded.split('data:', 1)[-1].strip()
                                    json_match = re.search(r'\{.*\}', data_part, re.DOTALL)
                                else:
                                    json_match = re.search(r'\{.*\}', decoded, re.DOTALL)
                                
                                if json_match:
                                    json_str = json_match.group(0)
                                    formatted_json = self._format_json(json_str)
                                    message = f"[SSE Chunk - 已格式化]\n{formatted_json}"
                                    break
                            except:
                                pass
            except:
                pass
        
        # 如果有中文转义序列，尝试解码显示中文
        if '\\u' in message or '\\x' in message:
            try:
                decoded_message = message.encode('utf-8').decode('unicode_escape')
                if decoded_message != message:
                    message = decoded_message
            except:
                pass
        
        # 更新记录的消息，清除 args（避免格式化错误）
        if message != original_message:
            record.msg = message
            record.args = ()
        
        return super().format(record)

# 为 MCP 相关日志设置格式化器和 DEBUG 级别（以便查看详细信息）
mcp_formatter = MCPProtocolFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
for logger_name in ['mcp.server.lowlevel.server', 'mcp.server.sse', 'sse_starlette.sse']:
    mcp_log = logging.getLogger(logger_name)
    # 设置为 DEBUG 级别以查看详细信息
    mcp_log.setLevel(logging.DEBUG)
    # 添加格式化器
    for handler in mcp_log.handlers[:]:
        handler.setFormatter(mcp_formatter)
    # 如果没有处理器，添加一个
    if not mcp_log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(mcp_formatter)
        mcp_log.addHandler(handler)

# 创建FastMCP服务器实例（在构造函数中指定host和端口）
# host='0.0.0.0' 允许从容器外部访问（容器间通信）
mcp = FastMCP("MathTools", host="0.0.0.0", port=8100)

# 不使用中间件方式，改用日志格式化器格式化现有日志输出

# 注册工具 - 实现直接放在这里，FastMCP会自动从函数签名和docstring提取工具信息
# 注意：工具描述需要明确说明何时使用，避免在非数学场景下调用
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """
    计算两个数字的加法。
    
    重要：仅在用户明确要求进行加法计算时使用此工具。对于问候、闲聊或非数学问题，不要使用此工具。
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两个数字的和
    """
    logger.info(f"[FastMCP Tool] add_numbers(a={a}, b={b})")
    result = a + b
    logger.info(f"[FastMCP Tool] add_numbers 结果: {result}")
    return result

@mcp.tool()
def multiply_numbers(a: float, b: float) -> float:
    """
    计算两个数字的乘法。
    
    重要：仅在用户明确要求进行乘法计算时使用此工具。对于问候、闲聊或非数学问题，不要使用此工具。
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        两个数字的乘积
    """
    logger.info(f"[FastMCP Tool] multiply_numbers(a={a}, b={b})")
    result = a * b
    logger.info(f"[FastMCP Tool] multiply_numbers 结果: {result}")
    return result

@mcp.tool()
def calculate_expression(expression: str) -> float:
    """
    计算数学表达式。表达式必须只包含数字和基本运算符（+、-、*、/、括号）。
    
    重要：仅在用户明确要求计算数学表达式时使用此工具。expression 参数必须是有效的数学表达式字符串（如 '2+3*4'），不能是问候语、文本或其他非数学内容。对于问候、闲聊或非数学问题，不要使用此工具。
    
    Args:
        expression: 数学表达式字符串，必须只包含数字、运算符和括号，例如 '2+3*4'、'10/2' 等
    
    Returns:
        计算结果的浮点数
    """
    logger.info(f"[FastMCP Tool] calculate_expression(expression='{expression}')")
    try:
        # 简单的安全计算，只允许数字和基本运算符
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("表达式包含非法字符")
        
        result = eval(expression)
        result_float = float(result)
        logger.info(f"[FastMCP Tool] calculate_expression 结果: {result_float}")
        return result_float
    except Exception as e:
        logger.error(f"[FastMCP Tool] calculate_expression 失败: {str(e)}")
        raise ValueError(f"计算错误: {str(e)}")

if __name__ == "__main__":
    # FastMCP通过SSE端点自动暴露工具列表和调用接口
    # 无需手工实现/tools端点，工具列表会自动从@mcp.tool()装饰的函数中提取
    logger.info("启动FastMCP服务器，监听: 0.0.0.0:8100")
    logger.info("SSE端点: http://0.0.0.0:8100/sse")
    logger.info("工具列表和调用接口通过SSE端点自动暴露")
    logger.info("MCP 协议日志已启用，日志输出已格式化为易读格式（JSON 格式化、中文友好）")
    
    # 启动FastMCP服务器（自动提供SSE端点）
    # 注意：MCP 协议日志通过自定义格式化器自动格式化，不修改原有日志级别
    mcp.run(transport="sse")
