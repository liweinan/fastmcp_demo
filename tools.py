"""
简单的计算工具定义
"""
import json
from typing import Any, Dict

def add(a: float, b: float) -> float:
    """两数相加"""
    return a + b

def multiply(a: float, b: float) -> float:
    """两数相乘"""
    return a * b

def calculate(expression: str) -> float:
    """简单表达式计算（仅支持基本四则运算）"""
    try:
        # 简单的安全计算，只允许数字和基本运算符
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("表达式包含非法字符")
        
        result = eval(expression)
        return float(result)
    except Exception as e:
        raise ValueError(f"计算错误: {str(e)}")

# 工具定义字典，用于MCP注册
TOOLS = {
    "add": {
        "name": "add",
        "description": "两数相加",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个数"},
                "b": {"type": "number", "description": "第二个数"}
            },
            "required": ["a", "b"]
        }
    },
    "multiply": {
        "name": "multiply", 
        "description": "两数相乘",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个数"},
                "b": {"type": "number", "description": "第二个数"}
            },
            "required": ["a", "b"]
        }
    },
    "calculate": {
        "name": "calculate",
        "description": "计算简单数学表达式",
        "parameters": {
            "type": "object", 
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，如 '2+3*4'"}
            },
            "required": ["expression"]
        }
    }
}

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """执行指定工具"""
    if tool_name == "add":
        return add(arguments["a"], arguments["b"])
    elif tool_name == "multiply":
        return multiply(arguments["a"], arguments["b"])
    elif tool_name == "calculate":
        return calculate(arguments["expression"])
    else:
        raise ValueError(f"未知工具: {tool_name}")
