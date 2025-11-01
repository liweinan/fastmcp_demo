"""
MCP服务器 + HTTP API wrapper (真实LLM版本)
"""
import os
import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
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
    """加载LLM模型"""
    global llm
    model_path = "./models/qwen2-1_5b-instruct-q4_k_m.gguf"
    
    if not os.path.exists(model_path):
        logger.warning(f"模型文件不存在: {model_path}，无法加载真实模型")
        raise FileNotFoundError(f"模型文件不存在: {model_path}，请先下载模型文件")
    
    try:
        logger.info(f"正在加载模型: {model_path}")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,           # 上下文长度
            n_threads=4,          # CPU线程数
            verbose=False         # 不输出详细日志
        )
        logger.info("模型加载完成")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise

def create_tool_prompt(tools: List[Dict]) -> str:
    """创建工具调用的系统提示"""
    tools_desc = []
    for tool in tools:
        name = tool['name']
        desc = tool['description']
        params = tool['parameters']['properties']
        required = tool['parameters'].get('required', [])
        
        param_desc = []
        for param_name, param_info in params.items():
            param_type = param_info.get('type', 'any')
            param_desc_str = f"{param_name} ({param_type})"
            if param_name in required:
                param_desc_str += " [必需]"
            param_desc.append(f"    - {param_desc_str}: {param_info.get('description', '')}")
        
        tool_info = f"- {name}: {desc}\n  参数:\n" + "\n".join(param_desc)
        tools_desc.append(tool_info)
    
    return f"""你是一个友善的数学计算助手。你的主要功能是帮助用户进行数学计算，但你也可以友好地回复用户的问候和一般性对话。

可用工具：
{chr(10).join(tools_desc)}

当用户需要数学计算时，使用以下格式调用工具：
```json
{{"tool": "工具名", "arguments": {{"参数名": "参数值"}}}}
```

计算示例：
- "计算 2 + 3" → {{"tool": "add", "arguments": {{"a": 2, "b": 3}}}}
- "计算 4 * 5" → {{"tool": "multiply", "arguments": {{"a": 4, "b": 5}}}}
- "计算 2+3*4" → {{"tool": "calculate", "arguments": {{"expression": "2+3*4"}}}}

重要规则：
1. 如果用户询问数学计算问题，必须使用工具调用格式返回JSON
2. 如果用户只是打招呼、闲聊或询问非计算问题，请用自然语言友好回复，不要使用工具调用
3. 工具调用时必须包含所有必需参数，参数值类型正确

请根据用户消息的类型，选择返回工具调用JSON或自然语言回复。"""

def parse_tool_call(response_text: str) -> Optional[Dict[str, Any]]:
    """解析LLM返回的工具调用JSON"""
    try:
        # 方法1: 查找 ```json 代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"代码块JSON解析失败: {e}, 内容: {json_str[:100]}")
        
        # 方法2: 尝试直接解析整个响应为JSON
        try:
            parsed = json.loads(response_text.strip())
            if isinstance(parsed, dict) and 'tool' in parsed:
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        # 方法3: 查找包含 "tool" 键的JSON对象（支持嵌套和换行）
        # 使用更宽松的匹配，找到第一个包含 "tool" 的JSON对象
        json_patterns = [
            r'\{[^{}]*"tool"[^{}]*"arguments"[^{}]*\}',  # 简单的单层对象
            r'\{(?:[^{}]|(?:\{[^{}]*\}))*"tool"(?:[^{}]|(?:\{[^{}]*\}))*\}',  # 支持嵌套的arguments
        ]
        
        for pattern in json_patterns:
            json_match = re.search(pattern, response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    continue
        
        # 方法4: 尝试提取完整的JSON对象（从第一个 { 到匹配的 }）
        brace_start = response_text.find('{')
        if brace_start != -1:
            brace_count = 0
            for i, char in enumerate(response_text[brace_start:], start=brace_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            json_str = response_text[brace_start:i+1]
                            parsed = json.loads(json_str)
                            if isinstance(parsed, dict) and 'tool' in parsed:
                                return parsed
                        except json.JSONDecodeError:
                            break
        
        return None
    except Exception as e:
        logger.warning(f"解析工具调用失败: {e}, 响应文本: {response_text[:200]}")
        return None

def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """验证工具参数是否完整"""
    if tool_name not in TOOLS:
        return False, f"未知工具: {tool_name}"
    
    tool_def = TOOLS[tool_name]
    required_params = tool_def['parameters'].get('required', [])
    
    missing_params = []
    for param in required_params:
        if param not in arguments:
            missing_params.append(param)
    
    if missing_params:
        return False, f"缺少必需参数: {', '.join(missing_params)}"
    
    return True, None

def call_llm_with_tools(user_message: str) -> str:
    """调用LLM并处理工具调用"""
    if llm is None:
        raise ValueError("模型未加载")
    
    system_prompt = create_tool_prompt(list(TOOLS.values()))
    
    # 构建对话消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    try:
        # 调用LLM
        logger.info("正在调用LLM进行推理...")
        response = llm.create_chat_completion(
            messages=messages,
            temperature=0.7,      # 提高温度，让回复更自然友好
            max_tokens=512        # 限制输出长度
        )
        
        # 提取响应内容
        response_text = response['choices'][0]['message']['content'].strip()
        logger.info(f"LLM完整响应: {response_text}")
        
        # 尝试解析工具调用
        tool_call = parse_tool_call(response_text)
        logger.info(f"解析后的工具调用: {tool_call}")
        
        if tool_call and 'tool' in tool_call:
            tool_name = tool_call['tool']
            arguments = tool_call.get('arguments', {})
            
            if tool_name in TOOLS:
                # 验证参数
                is_valid, error_msg = validate_tool_arguments(tool_name, arguments)
                if not is_valid:
                    logger.warning(f"参数验证失败: {error_msg}, 工具: {tool_name}, 参数: {arguments}")
                    return f"抱歉，我无法完成这个计算。{error_msg}"
                
                logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
                try:
                    result = execute_tool(tool_name, arguments)
                    return f"计算结果: {result}"
                except KeyError as e:
                    logger.error(f"工具执行时缺少参数: {e}, 工具: {tool_name}, 提供的参数: {arguments}")
                    return f"抱歉，计算过程中出现了问题：缺少参数 {e}"
                except Exception as e:
                    logger.error(f"工具执行失败: {e}, 工具: {tool_name}, 参数: {arguments}")
                    return f"抱歉，计算失败: {str(e)}"
            else:
                logger.warning(f"未知工具: {tool_name}")
                # 如果工具不存在，返回友好提示而不是错误信息
                return f"抱歉，我不认识这个工具 '{tool_name}'。我只能进行加法、乘法和表达式计算。"
        
        # 如果没有工具调用，说明LLM返回的是自然语言回复（问候、闲聊等）
        # 直接返回LLM的响应，提供友好的对话体验
        logger.info("LLM返回自然语言回复，直接返回给用户")
        
        # 清理响应中的可能残留的JSON格式标记
        cleaned_response = response_text
        # 移除可能的JSON代码块标记（如果LLM误加了格式）
        cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
        cleaned_response = re.sub(r'```\s*', '', cleaned_response)
        cleaned_response = cleaned_response.strip()
        
        return cleaned_response
        
    except Exception as e:
        logger.error(f"LLM调用失败: {e}", exc_info=True)
        return f"抱歉，处理您的请求时出现错误: {str(e)}"

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    mode = "real" if llm is not None and not isinstance(llm, str) else "not_loaded"
    return jsonify({
        "status": "healthy", 
        "model_loaded": llm is not None and not isinstance(llm, str),
        "mode": mode
    })

@app.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        # 检查 Content-Type
        if not request.is_json:
            # 尝试从原始数据解析
            if request.data:
                try:
                    data = json.loads(request.data.decode('utf-8'))
                    logger.info("从原始数据成功解析JSON")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    return jsonify({
                        "error": "JSON格式错误",
                        "message": f"无法解析请求体中的JSON数据: {str(e)}",
                        "hint": "请确保使用正确的JSON格式，例如: {\"message\": \"你好\"}",
                        "example": '{"message": "你好"}'
                    }), 400
            else:
                return jsonify({
                    "error": "请求格式错误",
                    "message": "请使用 application/json 格式发送请求",
                    "example": '{"message": "你好"}'
                }), 400
        else:
            # 使用 get_json 的 silent 选项，避免抛出异常
            data = request.get_json(force=False, silent=True)
            if data is None:
                # JSON 解析失败，尝试从原始数据解析
                if request.data:
                    try:
                        data = json.loads(request.data.decode('utf-8'))
                        logger.info("从原始数据成功解析JSON（get_json失败后的备选方案）")
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        return jsonify({
                            "error": "JSON格式错误",
                            "message": f"无法解析请求体中的JSON数据: {str(e)}",
                            "hint": "请检查JSON格式是否正确，确保字符串使用双引号，例如: {\"message\": \"你好\"}",
                            "example": '{"message": "你好"}'
                        }), 400
                else:
                    return jsonify({
                        "error": "请求体为空",
                        "message": "请提供JSON格式的请求体",
                        "example": '{"message": "你好"}'
                    }), 400
        
        if not data:
            return jsonify({
                "error": "请求体为空",
                "message": "请提供JSON格式的请求体",
                "example": '{"message": "你好"}'
            }), 400
        
        if 'message' not in data:
            return jsonify({
                "error": "缺少message字段",
                "message": "请求中必须包含 'message' 字段",
                "example": '{"message": "你好"}'
            }), 400
        
        user_message = data['message']
        if not isinstance(user_message, str) or not user_message.strip():
            return jsonify({
                "error": "message字段无效",
                "message": "message 必须是非空字符串"
            }), 400
        
        logger.info(f"收到消息: {user_message}")
        
        if llm is None:
            return jsonify({
                "error": "模型未加载",
                "message": "服务器未正确初始化，请检查模型文件是否存在"
            }), 500
        
        # 调用LLM处理消息
        response = call_llm_with_tools(user_message)
        
        return jsonify({
            "response": response,
            "tools_available": list(TOOLS.keys())
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return jsonify({
            "error": "JSON格式错误",
            "message": f"请求体中的JSON格式不正确: {str(e)}",
            "hint": "请确保使用正确的JSON格式，例如: {\"message\": \"你好\"}",
            "example": '{"message": "你好"}'
        }), 400
    except Exception as e:
        logger.error(f"处理请求时出错: {e}", exc_info=True)
        # 检查是否是Flask的400错误
        error_str = str(e)
        if "400" in error_str or "Bad Request" in error_str:
            return jsonify({
                "error": "请求格式错误",
                "message": "无法解析请求数据，请检查JSON格式是否正确",
                "hint": "确保使用正确的引号和转义字符",
                "example_correct": '{"message": "你好"}',
                "example_curl": 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d \'{"message": "你好"}\''
            }), 400
        return jsonify({
            "error": "服务器内部错误",
            "message": f"抱歉，处理您的请求时出现了错误: {str(e)}"
        }), 500

@app.route('/tools', methods=['GET'])
def list_tools():
    """列出可用工具"""
    return jsonify({"tools": TOOLS})

if __name__ == '__main__':
    # 加载模型
    try:
        load_model()
        logger.info("服务器启动成功，等待请求...")
    except FileNotFoundError as e:
        logger.error(f"模型加载失败: {e}")
        logger.error("请先下载模型文件，参考README.md中的说明")
        exit(1)
    except ImportError as e:
        logger.error(f"依赖库导入失败: {e}")
        logger.error("请安装所需依赖: pip install -r requirements.txt")
        exit(1)
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        logger.exception("详细错误信息:")
        exit(1)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=8000, debug=False)
