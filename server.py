"""
MCP服务器 + HTTP API wrapper (模拟版本)
"""
import os
import json
import logging
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from tools import TOOLS, execute_tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全局模型实例
llm = None

def load_model():
    """模拟加载模型（用于演示）"""
    global llm
    model_path = "./models/qwen2-1_5b-instruct-q4_k_m.gguf"
    
    if not os.path.exists(model_path):
        logger.warning(f"模型文件不存在: {model_path}，使用模拟模式")
        llm = "mock_model"  # 模拟模型
    else:
        logger.info("模型文件存在，但使用模拟模式")
        llm = "mock_model"  # 模拟模型
    
    logger.info("模拟模型加载完成")

def create_tool_prompt(tools: List[Dict]) -> str:
    """创建工具调用的系统提示"""
    tools_desc = []
    for tool in tools:
        tools_desc.append(f"- {tool['name']}: {tool['description']}")
    
    return f"""你是一个数学计算助手。你可以使用以下工具来帮助用户计算：

{chr(10).join(tools_desc)}

当用户需要计算时，请使用相应的工具。工具调用格式：
```json
{{"tool": "工具名", "arguments": {{"参数名": "参数值"}}}}
```

请直接返回工具调用，不要添加其他解释。"""

def call_llm_with_tools(user_message: str) -> str:
    """模拟LLM调用并处理工具调用"""
    system_prompt = create_tool_prompt(list(TOOLS.values()))
    
    # 简单的工具调用模拟
    if "加" in user_message or "+" in user_message:
        # 提取数字
        import re
        numbers = re.findall(r'\d+', user_message)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            result = execute_tool("add", {"a": a, "b": b})
            return f"计算结果: {result}"
    
    elif "乘" in user_message or "*" in user_message:
        # 提取数字
        import re
        numbers = re.findall(r'\d+', user_message)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            result = execute_tool("multiply", {"a": a, "b": b})
            return f"计算结果: {result}"
    
    elif "计算" in user_message:
        # 尝试提取表达式
        import re
        expr_match = re.search(r'(\d+(?:\s*[+\-*/]\s*\d+)+)', user_message)
        if expr_match:
            expr = expr_match.group(1)
            result = execute_tool("calculate", {"expression": expr})
            return f"计算结果: {result}"
    
    # 默认回复
    return f"我收到了你的消息: {user_message}。这是一个模拟的AI回复。"

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy", 
        "model_loaded": llm is not None,
        "mode": "mock" if llm == "mock_model" else "real"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "缺少message字段"}), 400
        
        user_message = data['message']
        logger.info(f"收到消息: {user_message}")
        
        if llm is None:
            return jsonify({"error": "模型未加载"}), 500
        
        # 调用LLM处理消息
        response = call_llm_with_tools(user_message)
        
        return jsonify({
            "response": response,
            "tools_available": list(TOOLS.keys())
        })
        
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tools', methods=['GET'])
def list_tools():
    """列出可用工具"""
    return jsonify({"tools": TOOLS})

if __name__ == '__main__':
    # 加载模型
    try:
        load_model()
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        exit(1)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=8000, debug=False)
