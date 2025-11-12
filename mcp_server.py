"""
FastMCP Server - Exposes calculation tools
FastMCP automatically exposes tool lists through SSE endpoints, no manual implementation needed
"""
import json
import logging
import re

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

# Configure logging - keep original level, but add formatter for clearer output
logging.basicConfig(
    level=logging.INFO,  # Base log level set to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create custom formatter for MCP protocol related logs
class MCPProtocolFormatter(logging.Formatter):
    """Format MCP protocol logs to make them more readable (Unicode-friendly, JSON formatted, using Python json)"""
    
    def _format_json(self, json_str):
        """Format JSON using Python json module"""
        try:
            json_obj = json.loads(json_str)
            return json.dumps(json_obj, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            return json_str
    
    def format(self, record):
        # First get formatted message (handle %s placeholders)
        try:
            message = record.getMessage()
        except TypeError:
            # If formatting fails, use original message and args directly
            message = record.msg
            if record.args:
                try:
                    message = message % record.args
                except:
                    message = str(record.msg) + ' ' + str(record.args)
        
        original_message = message
        
        # Format JSON-RPC messages (handle various possible formats)
        if any(keyword in message for keyword in ['JSONRPCMessage', 'SessionMessage', 'Sending message', 'Dispatching request', 'Processing request']):
            try:
                json_match = re.search(r'\{.*\}', message, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    formatted_json = self._format_json(json_str)
                    message = message.replace(json_str, '\n' + formatted_json)
            except:
                pass
        
        # Format SSE chunks (handle binary strings)
        if 'chunk:' in message:
            try:
                # Match chunk: %s format (handle placeholders)
                # If record.args exists and contains data, process args directly
                if record.args and len(record.args) > 0:
                    chunk_data = record.args[0]
                    if isinstance(chunk_data, bytes):
                        try:
                            chunk_str = chunk_data.decode('utf-8', errors='replace')
                            # Find JSON (may be after data:)
                            if 'data:' in chunk_str:
                                data_part = chunk_str.split('data:', 1)[-1].strip()
                                json_match = re.search(r'\{.*\}', data_part, re.DOTALL)
                            else:
                                json_match = re.search(r'\{.*\}', chunk_str, re.DOTALL)
                            
                            if json_match:
                                json_str = json_match.group(0)
                                formatted_json = self._format_json(json_str)
                                message = f"[SSE Chunk - Formatted]\n{formatted_json}"
                        except:
                            pass
                else:
                    # Try to extract from message string
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
                                    message = f"[SSE Chunk - Formatted]\n{formatted_json}"
                                    break
                            except:
                                pass
            except:
                pass
        
        # If there are Unicode escape sequences, try to decode and display
        if '\\u' in message or '\\x' in message:
            try:
                decoded_message = message.encode('utf-8').decode('unicode_escape')
                if decoded_message != message:
                    message = decoded_message
            except:
                pass
        
        # Update record message, clear args (avoid formatting errors)
        if message != original_message:
            record.msg = message
            record.args = ()
        
        return super().format(record)

# Set formatter and DEBUG level for MCP related logs (to view detailed information)
mcp_formatter = MCPProtocolFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
for logger_name in ['mcp.server.lowlevel.server', 'mcp.server.sse', 'sse_starlette.sse']:
    mcp_log = logging.getLogger(logger_name)
    # Set to DEBUG level to view detailed information
    mcp_log.setLevel(logging.DEBUG)
    # Add formatter
    for handler in mcp_log.handlers[:]:
        handler.setFormatter(mcp_formatter)
    # If no handler, add one
    if not mcp_log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(mcp_formatter)
        mcp_log.addHandler(handler)

# Create FastMCP server instance (specify host and port in constructor)
# host='0.0.0.0' allows access from outside container (inter-container communication)
mcp = FastMCP("MathTools", host="0.0.0.0", port=8100)

# Not using middleware approach, use log formatter to format existing log output

# Register tools - implementation directly here, FastMCP automatically extracts tool info from function signatures and docstrings
# Note: Tool descriptions need to clearly specify when to use, avoid calling in non-math scenarios
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """
    Calculate the sum of two numbers.
    
    Important: Only use this tool when the user explicitly requests addition calculation. Do not use this tool for greetings, casual chat, or non-mathematical questions.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of the two numbers
    """
    logger.info(f"[FastMCP Tool] add_numbers(a={a}, b={b})")
    result = a + b
    logger.info(f"[FastMCP Tool] add_numbers result: {result}")
    return result

@mcp.tool()
def multiply_numbers(a: float, b: float) -> float:
    """
    Calculate the product of two numbers.
    
    Important: Only use this tool when the user explicitly requests multiplication calculation. Do not use this tool for greetings, casual chat, or non-mathematical questions.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of the two numbers
    """
    logger.info(f"[FastMCP Tool] multiply_numbers(a={a}, b={b})")
    result = a * b
    logger.info(f"[FastMCP Tool] multiply_numbers result: {result}")
    return result

@mcp.tool()
def calculate_expression(expression: str) -> float:
    """
    Calculate a mathematical expression. The expression must only contain numbers and basic operators (+, -, *, /, parentheses).
    
    Important: Only use this tool when the user explicitly requests calculation of a mathematical expression. The expression parameter must be a valid mathematical expression string (e.g., '2+3*4'), not a greeting, text, or other non-mathematical content. Do not use this tool for greetings, casual chat, or non-mathematical questions.
    
    Args:
        expression: Mathematical expression string, must only contain numbers, operators, and parentheses, e.g., '2+3*4', '10/2', etc.
    
    Returns:
        Floating point result of the calculation
    """
    logger.info(f"[FastMCP Tool] calculate_expression(expression='{expression}')")
    try:
        # Simple safe calculation, only allow numbers and basic operators
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters")
        
        result = eval(expression)
        result_float = float(result)
        logger.info(f"[FastMCP Tool] calculate_expression result: {result_float}")
        return result_float
    except Exception as e:
        logger.error(f"[FastMCP Tool] calculate_expression failed: {str(e)}")
        raise ValueError(f"Calculation error: {str(e)}")

if __name__ == "__main__":
    # FastMCP automatically exposes tool lists and call interfaces through SSE endpoints
    # No need to manually implement /tools endpoint, tool list is automatically extracted from @mcp.tool() decorated functions
    logger.info("Starting FastMCP server, listening on: 0.0.0.0:8100")
    logger.info("SSE endpoint: http://0.0.0.0:8100/sse")
    logger.info("Tool list and call interfaces are automatically exposed through SSE endpoint")
    logger.info("MCP protocol logging enabled, log output formatted for readability (JSON formatted, Unicode-friendly)")
    
    # Start FastMCP server (automatically provides SSE endpoint)
    # Note: MCP protocol logs are automatically formatted through custom formatter, original log level unchanged
    mcp.run(transport="sse")
