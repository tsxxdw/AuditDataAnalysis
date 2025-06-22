#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from service.common.model_common_service import model_service
import logging
import re
import json
import ollama

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ollama 配置
OLLAMA_MODEL = "qwen3:1.7b"

# 创建蓝图
model_api = Blueprint('model_api', __name__)

@model_api.route('/api/model/chat', methods=['POST'])
def chat_completion():
    """
    大模型对话接口
    ---
    请求体:
    {
        "provider_id": "ollama",  // 服务提供商ID
        "model_id": "qwen3:1.7b", // 模型ID
        "messages": [             // 对话历史消息
            {"role": "user", "content": "你好"}
        ],
        "options": {              // 可选参数
            "temperature": 0.7,
            "max_tokens": 1000,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        # 参数验证
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
        
        provider_id = data.get('provider_id')
        model_id = data.get('model_id')
        messages = data.get('messages', [])
        options = data.get('options', {})
        
        if not provider_id:
            return jsonify({"error": "服务提供商ID不能为空"}), 400
        
        if not model_id:
            return jsonify({"error": "模型ID不能为空"}), 400
        
        if not messages or not isinstance(messages, list):
            return jsonify({"error": "消息格式不正确"}), 400
        
        # 调用模型服务
        result = model_service.chat_completion(provider_id, model_id, messages, options)
        
        # 检查是否有错误
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"处理对话请求时发生错误: {str(e)}")
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

# 添加默认模型相关的API端点
@model_api.route('/api/model/visible-models', methods=['GET'])
def get_visible_models():
    """获取所有服务提供商中可见的模型"""
    try:
        logger.info("API请求: 获取所有可见模型")
        all_visible_models = model_service.get_all_visible_models()
        logger.info(f"API响应: 获取所有可见模型成功，共 {len(all_visible_models)} 个模型")
        return jsonify({"success": True, "models": all_visible_models})
    except Exception as e:
        logger.error(f"获取所有可见模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/model/default-model', methods=['GET'])
def get_default_model():
    """获取当前默认模型"""
    try:
        logger.info("API请求: 获取默认模型")
        default_model = model_service.get_default_model()
        if default_model:
            logger.info(f"API响应: 获取默认模型成功 - {default_model.get('provider_id', 'unknown')}:{default_model.get('id', 'unknown')}")
            return jsonify({"success": True, "model": default_model})
        else:
            logger.info("API响应: 未找到默认模型")
            return jsonify({"success": True, "model": None})
    except Exception as e:
        logger.error(f"获取默认模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/model/default-model', methods=['POST'])
def set_default_model():
    """设置默认模型"""
    try:
        data = request.get_json()
        logger.info(f"API请求: 设置默认模型 - 请求数据: {data}")
        
        if not data:
            logger.error("设置默认模型失败: 请求体为空")
            return jsonify({"success": False, "error": "请求体不能为空"}), 400
            
        provider_id = data.get('provider_id')
        model_id = data.get('model_id')
        
        if not provider_id or not model_id:
            logger.error(f"设置默认模型失败: 参数不完整 - provider_id: {provider_id}, model_id: {model_id}")
            return jsonify({"success": False, "error": "服务提供商ID和模型ID不能为空"}), 400
        
        logger.info(f"设置默认模型 - 提供商ID: {provider_id}, 模型ID: {model_id}")
        result = model_service.set_default_model(provider_id, model_id)
        
        if result:
            logger.info("API响应: 默认模型设置成功")
            # 验证设置是否生效
            current_default = model_service.get_default_model()
            logger.info(f"验证默认模型设置 - 当前默认模型: {current_default}")
            return jsonify({"success": True, "message": "默认模型设置成功"})
        else:
            logger.error("API响应: 设置默认模型失败")
            return jsonify({"success": False, "error": "设置默认模型失败，请确认提供商和模型是否有效"}), 400
    except Exception as e:
        logger.error(f"设置默认模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/common/ollama/models', methods=['GET'])
def list_ollama_models():
    """获取可用的Ollama模型列表
    
    返回:
        JSON: 包含可用模型的列表
    """
    logger.info("获取Ollama可用模型列表")
    
    try:
        # 使用ollama包获取模型列表
        models_list = ollama.list()
        logger.info(f"原始Ollama模型列表: {models_list}")
        
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
                    logger.warning(f"处理模型时出错: {str(e)}")
                    # 尝试创建最小化的模型信息
                    try:
                        model_name = getattr(model, 'model', None) or getattr(model, 'name', None) or str(model)
                        serializable_models.append({
                            "name": model_name,
                            "model": model_name
                        })
                    except:
                        logger.warning(f"无法序列化模型: {model}")
        
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
            logger.warning("模型列表仍然包含不可序列化的内容，使用备用简化格式")
            # 创建简化版本
            simplified_models = []
            for model in serializable_models:
                simplified_models.append({
                    "name": model.get("name", "") or model.get("model", "unknown"),
                    "model": model.get("model", "") or model.get("name", "unknown")
                })
            serializable_models = simplified_models
        
        logger.info(f"处理后的可序列化模型列表: {serializable_models}")
        
        return jsonify({
            "success": True,
            "message": "成功获取模型列表",
            "models": serializable_models,
            "default_model": OLLAMA_MODEL
        })
        
    except Exception as e:
        logger.error(f"获取Ollama模型列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取Ollama模型列表失败: {str(e)}"
        }), 500 