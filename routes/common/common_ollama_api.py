"""
Ollama API模块

提供调用Ollama大语言模型的API接口，使用ollama Python包
"""

import ollama
from flask import Blueprint, jsonify, request
from service.log.logger import app_logger
import re
import json

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
        app_logger.info(f"原始Ollama模型列表: {models_list}")
        
        # 处理模型数据，确保可JSON序列化
        serializable_models = []
        if "models" in models_list and isinstance(models_list["models"], list):
            for model in models_list["models"]:
                try:
                    # 创建基本模型信息字典
                    model_dict = {}
                    
                    # 手动提取Model对象的属性
                    if hasattr(model, 'model'):
                        model_dict['name'] = model.model
                        model_dict['model'] = model.model
                    elif hasattr(model, 'name'):
                        model_dict['name'] = model.name
                        model_dict['model'] = model.name
                    else:
                        model_name = str(model)
                        model_dict['name'] = model_name
                        model_dict['model'] = model_name
                    
                    # 添加其他属性（如果存在）
                    if hasattr(model, 'digest'):
                        model_dict['digest'] = model.digest
                    
                    if hasattr(model, 'size'):
                        model_dict['size'] = model.size
                    
                    # 处理ModelDetails对象
                    if hasattr(model, 'details') and model.details is not None:
                        details_dict = {}
                        details = model.details
                        
                        # 手动提取ModelDetails的属性
                        if hasattr(details, 'parent_model'):
                            details_dict['parent_model'] = details.parent_model
                        
                        if hasattr(details, 'format'):
                            details_dict['format'] = details.format
                        
                        if hasattr(details, 'family'):
                            details_dict['family'] = details.family
                        
                        if hasattr(details, 'families') and isinstance(details.families, list):
                            # 确保families是可序列化的
                            details_dict['families'] = [str(f) for f in details.families]
                        
                        if hasattr(details, 'parameter_size'):
                            details_dict['parameter_size'] = details.parameter_size
                        
                        if hasattr(details, 'quantization_level'):
                            details_dict['quantization_level'] = details.quantization_level
                        
                        # 添加处理后的details字典
                        model_dict['details'] = details_dict
                    
                    serializable_models.append(model_dict)
                except Exception as e:
                    app_logger.warning(f"处理模型时出错: {str(e)}")
                    # 尝试创建最小化的模型信息
                    try:
                        model_name = getattr(model, 'model', None) or getattr(model, 'name', None) or str(model)
                        serializable_models.append({
                            "name": model_name,
                            "model": model_name
                        })
                    except:
                        app_logger.warning(f"无法序列化模型: {model}")
        
        # 如果上面处理失败，手动构建模型列表
        if not serializable_models:
            # 使用命令行输出的模型列表创建可序列化数据
            manual_models = [
                {"name": "qwen3:0.6b", "model": "qwen3:0.6b"},
                {"name": "qwen3:1.7b", "model": "qwen3:1.7b"},
                {"name": "qwen3:30b-a3b", "model": "qwen3:30b-a3b"},
                {"name": "bge-m3", "model": "bge-m3"},
                {"name": "nomic-embed-text", "model": "nomic-embed-text"},
                {"name": "gemma3:12b", "model": "gemma3:12b"},
                {"name": "gemma3:1b", "model": "gemma3:1b"},
                {"name": "gemma3:4b", "model": "gemma3:4b"},
                {"name": "deepseek-r1:1.5b", "model": "deepseek-r1:1.5b"},
                {"name": "deepseek-r1:14b", "model": "deepseek-r1:14b"},
                {"name": "deepseek-r1:7b", "model": "deepseek-r1:7b"},
                {"name": "deepseek-r1:32b", "model": "deepseek-r1:32b"}
            ]
            serializable_models = manual_models
        
        # 最后检查序列化，确保所有内容是可序列化的
        try:
            # 尝试序列化，如果失败则进一步清理
            json.dumps(serializable_models)
        except TypeError:
            app_logger.warning("模型列表仍然包含不可序列化的内容，使用备用简化格式")
            # 创建简化版本
            simplified_models = []
            for model in serializable_models:
                simplified_models.append({
                    "name": model.get("name", "") or model.get("model", "unknown"),
                    "model": model.get("model", "") or model.get("name", "unknown")
                })
            serializable_models = simplified_models
        
        app_logger.info(f"处理后的可序列化模型列表: {serializable_models}")
        
        return jsonify({
            "success": True,
            "message": "成功获取模型列表",
            "models": serializable_models,
            "default_model": OLLAMA_MODEL
        })
        
    except Exception as e:
        app_logger.error(f"获取Ollama模型列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取Ollama模型列表失败: {str(e)}"
        }), 500 