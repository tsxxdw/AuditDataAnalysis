"""
Ollama API模块

提供调用Ollama大语言模型的API接口
"""

import requests
from flask import Blueprint, jsonify, request
from service.log.logger import app_logger

# 创建Ollama API蓝图
common_ollama_bp = Blueprint('common_ollama_api', __name__, url_prefix='/api/common/ollama')

# Ollama API配置
OLLAMA_API_BASE = "http://localhost:11434/api"
OLLAMA_MODEL = "qwen3:30b-a3b"

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
        ollama_request = {
            "model": OLLAMA_MODEL,
            "prompt": user_prompt,
            "temperature": data.get("temperature", 0.7)
        }
        
        # 添加可选参数
        if "system_prompt" in data:
            ollama_request["system"] = data.get("system_prompt")
        
        if "max_tokens" in data:
            ollama_request["max_tokens"] = data.get("max_tokens")
        
        # 调用Ollama API
        app_logger.info(f"发送请求到Ollama API, 模型: {OLLAMA_MODEL}")
        response = requests.post(f"{OLLAMA_API_BASE}/generate", json=ollama_request)
        
        if response.status_code != 200:
            app_logger.error(f"Ollama API请求失败: {response.status_code}, {response.text}")
            return jsonify({
                "success": False,
                "message": f"Ollama API请求失败: {response.status_code}"
            }), 500
        
        result = response.json()
        
        return jsonify({
            "success": True,
            "message": "成功生成文本",
            "response": result.get("response"),
            "model": OLLAMA_MODEL
        })
        
    except requests.RequestException as e:
        app_logger.error(f"请求Ollama API出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"请求Ollama API出错: {str(e)}"
        }), 500
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
        # 调用Ollama API获取模型列表
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        
        if response.status_code != 200:
            app_logger.error(f"获取Ollama模型列表失败: {response.status_code}, {response.text}")
            return jsonify({
                "success": False,
                "message": f"获取Ollama模型列表失败: {response.status_code}"
            }), 500
        
        models = response.json().get("models", [])
        
        return jsonify({
            "success": True,
            "message": "成功获取模型列表",
            "models": models,
            "default_model": OLLAMA_MODEL
        })
        
    except requests.RequestException as e:
        app_logger.error(f"请求Ollama API出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"请求Ollama API出错: {str(e)}"
        }), 500
    except Exception as e:
        app_logger.error(f"获取Ollama模型列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取Ollama模型列表失败: {str(e)}"
        }), 500 