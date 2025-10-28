"""
FastMCP服务器 + HTTP API wrapper
"""
import os
import json
import logging
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from llama_cpp import Llama
from tools import TOOLS, execute_tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全局模型实例
llm = None

def load_model():
    """加载Qwen2模型"""
    global llm
    model_path = "./models/qwen2-1_5b-instruct-q4_k_m.gguf"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    logger.info("正在加载模型...")
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,  # 上下文长度
        n_threads=4,  # CPU线程数
        verbose=False
    )
    logger.info("模型加载完成")

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
    """调用LLM并处理工具调用"""
    system_prompt = create_tool_prompt(list(TOOLS.values()))
    
    # 构建对话
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 调用模型
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.1,
        max_tokens=512
    )
    
    content = response['choices'][0]['message']['content']
    
    # 尝试解析工具调用
    try:
        # 查找JSON格式的工具调用
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            tool_call = json.loads(json_str)
            
            if "tool" in tool_call and "arguments" in tool_call:
                tool_name = tool_call["tool"]
                arguments = tool_call["arguments"]
                
                # 执行工具
                result = execute_tool(tool_name, arguments)
                return f"计算结果: {result}"
    except Exception as e:
        logger.warning(f"工具调用解析失败: {e}")
    
    # 如果没有工具调用，返回原始回复
    return content

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "healthy", "model_loaded": llm is not None})

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
