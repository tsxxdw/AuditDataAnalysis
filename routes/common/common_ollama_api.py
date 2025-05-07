"""
Ollama API模块

提供调用Ollama大语言模型的API接口，使用ollama Python包
"""

import ollama
from flask import Blueprint, jsonify, request
from service.log.logger import app_logger
import re

# 创建Ollama API蓝图
common_ollama_bp = Blueprint('common_ollama_api', __name__, url_prefix='/api/common/ollama')

# Ollama 配置
OLLAMA_MODEL = "qwen3:1.7b"

@common_ollama_bp.route('/generate', methods=['POST'])
def generate_text():
    """调用Ollama模型生成文本
    
    请求体:
        user_prompt: 用户提示词
        system_prompt: 系统提示词(可选)
        max_tokens: 最大生成token数(可选)
        temperature: 温度参数(可选，默认0.7)
        
    返回:
        JSON: 包含生成的文本内容
    """
    app_logger.info("调用Ollama模型生成文本")
    
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False, 
                "message": "请求参数为空"
            }), 400
        
        user_prompt = data.get('user_prompt')
        if not user_prompt:
            return jsonify({
                "success": False, 
                "message": "用户提示词(user_prompt)不能为空"
            }), 400
        
        # 准备请求参数
        ollama_params = {
            "model": OLLAMA_MODEL,
            "prompt": user_prompt,
            "options": {
                "temperature": data.get("temperature", 0.7)
            }
        }
        
        # 添加可选参数
        if "system_prompt" in data:
            ollama_params["system"] = data.get("system_prompt")
        
        if "max_tokens" in data:
            ollama_params["options"]["num_predict"] = data.get("max_tokens")
        
        # 调用Ollama API
        app_logger.info(f"调用Ollama模型, 模型: {OLLAMA_MODEL}")
        app_logger.info(f"Ollama请求参数: {ollama_params}")
        
        # 使用ollama包生成文本
        response = ollama.generate(**ollama_params)
        
        app_logger.info(f"Ollama返回数据: {response}")
        
        # 获取响应文本并去除<think>标签内容
        response_text = response.get("response", "")
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        return jsonify({
            "success": True,
            "message": "成功生成文本",
            "response": response_text,
            "model": OLLAMA_MODEL
        })
        
    except Exception as e:
        app_logger.error(f"调用Ollama模型失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"调用Ollama模型失败: {str(e)}"
        }), 500

@common_ollama_bp.route('/models', methods=['GET'])
def list_models():
    """获取可用的Ollama模型列表
    
    返回:
        JSON: 包含可用模型的列表
    """
    app_logger.info("获取Ollama可用模型列表")
    
    try:
        # 使用ollama包获取模型列表
        models_list = ollama.list()
        models = models_list.get("models", [])
        
        return jsonify({
            "success": True,
            "message": "成功获取模型列表",
            "models": models,
            "default_model": OLLAMA_MODEL
        })
        
    except Exception as e:
        app_logger.error(f"获取Ollama模型列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取Ollama模型列表失败: {str(e)}"
        }), 500 