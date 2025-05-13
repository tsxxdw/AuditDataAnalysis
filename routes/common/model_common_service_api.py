#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from service.common.model_common_service import model_service
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

@model_api.route('/api/model/providers', methods=['GET'])
def get_providers():
    """获取所有启用的服务提供商"""
    try:
        providers = model_service.get_providers()
        # 仅返回启用的提供商
        enabled_providers = [provider for provider in providers if provider.get('enabled', False)]
        return jsonify({"providers": enabled_providers})
    
    except Exception as e:
        logger.error(f"获取服务提供商列表时发生错误: {str(e)}")
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/model/providers/<provider_id>/models', methods=['GET'])
def get_models(provider_id):
    """获取指定提供商的模型列表"""
    try:
        # 检查提供商是否存在
        provider = model_service.get_provider(provider_id)
        if not provider:
            return jsonify({"error": "未找到指定的服务提供商"}), 404
        
        # 检查提供商是否启用
        if not provider.get('enabled', False):
            return jsonify({"error": "该服务提供商已禁用"}), 403
        
        # 获取分类模型列表
        models_by_category = model_service.get_models_by_category(provider_id)
        return jsonify({"categories": models_by_category})
    
    except Exception as e:
        logger.error(f"获取模型列表时发生错误: {str(e)}")
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

# 添加默认模型相关的API端点
@model_api.route('/api/model/visible-models', methods=['GET'])
def get_visible_models():
    """获取所有服务提供商中可见的模型"""
    try:
        all_visible_models = model_service.get_all_visible_models()
        return jsonify({"success": True, "models": all_visible_models})
    except Exception as e:
        logger.error(f"获取所有可见模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/model/default-model', methods=['GET'])
def get_default_model():
    """获取当前默认模型"""
    try:
        default_model = model_service.get_default_model()
        if default_model:
            return jsonify({"success": True, "model": default_model})
        else:
            return jsonify({"success": True, "model": None})
    except Exception as e:
        logger.error(f"获取默认模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@model_api.route('/api/model/default-model', methods=['POST'])
def set_default_model():
    """设置默认模型"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "请求体不能为空"}), 400
            
        provider_id = data.get('provider_id')
        model_id = data.get('model_id')
        
        if not provider_id or not model_id:
            return jsonify({"success": False, "error": "服务提供商ID和模型ID不能为空"}), 400
            
        result = model_service.set_default_model(provider_id, model_id)
        if result:
            return jsonify({"success": True, "message": "默认模型设置成功"})
        else:
            return jsonify({"success": False, "error": "设置默认模型失败，请确认提供商和模型是否有效"}), 400
    except Exception as e:
        logger.error(f"设置默认模型时发生错误: {str(e)}")
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500 