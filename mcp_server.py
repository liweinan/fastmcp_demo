"""
FastMCP服务器 - 暴露计算工具
FastMCP通过SSE端点自动暴露工具列表，无需手工实现
"""
import logging
import re
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例（在构造函数中指定host和端口）
# host='0.0.0.0' 允许从容器外部访问（容器间通信）
mcp = FastMCP("MathTools", host="0.0.0.0", port=8100)

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
    
    # 启动FastMCP服务器（自动提供SSE端点）
    mcp.run(transport="sse")
