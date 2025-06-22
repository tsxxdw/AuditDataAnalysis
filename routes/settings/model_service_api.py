#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from service.common.model_common_service import model_service
from utils.settings.model_config_util import modelConfigUtil
import logging
import os
import json
import urllib.parse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建蓝图
model_settings_api = Blueprint('model_settings_api', __name__)

@model_settings_api.route('/api/settings/model/providers', methods=['GET'])
def get_providers():
    """获取所有服务提供商"""
    try:
        providers_dict = modelConfigUtil.get_all_providers()
        # 转换为前端所需格式
        providers = []
        for key, provider in providers_dict.items():
            provider_info = {
                'id': key,
                'name': provider.get('name', key),
                'apiUrl': provider.get('apiUrl', ''),
                'enabled': provider.get('enabled', False),
                'hasApiKey': bool(provider.get('apiKey', ''))
            }
            providers.append(provider_info)
            
        return jsonify({"success": True, "providers": providers})
    except Exception as e:
        logger.error(f"获取服务提供商列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    """获取指定服务提供商信息"""
    try:
        providers = modelConfigUtil.get_all_providers()
        provider = providers.get(provider_id)
        
        if not provider:
            return jsonify({"success": False, "message": "未找到指定的服务提供商"}), 404
        
        # 创建提供商信息的副本，去除敏感信息
        provider_info = {
            'id': provider_id,
            'name': provider.get('name', provider_id),
            'apiUrl': provider.get('apiUrl', ''),
            'apiVersion': provider.get('apiVersion', 'v1'),
            'enabled': provider.get('enabled', False),
            'hasApiKey': bool(provider.get('apiKey', ''))
        }
        
        return jsonify({"success": True, "provider": provider_info})
    except Exception as e:
        logger.error(f"获取服务提供商信息时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/update', methods=['POST'])
def update_provider(provider_id):
    """更新服务提供商配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        # 使用modelConfigUtil更新提供商信息
        success = modelConfigUtil.update_provider(provider_id, data)
        if not success:
            return jsonify({"success": False, "message": "更新服务提供商配置失败"}), 400
        
        return jsonify({"success": True, "message": "服务提供商配置已更新"})
    except Exception as e:
        logger.error(f"更新服务提供商配置时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/test', methods=['POST'])
def test_connection(provider_id):
    """测试与服务提供商的连接"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        api_key = data.get('apiKey')
        api_url = data.get('apiUrl')
        
        # 测试连接
        result = model_service.test_connection(provider_id, api_key, api_url)
        return jsonify(result)
    except Exception as e:
        logger.error(f"测试连接时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models', methods=['GET'])
def get_models(provider_id):
    """获取服务提供商的所有模型"""
    try:
        # 获取所有模型，包括不可见的
        models = modelConfigUtil.get_provider_models(provider_id)
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"获取模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/categories', methods=['GET'])
def get_provider_models_grouped_by_category(provider_id):
    """获取指定服务提供商的模型并按类别分组"""
    try:
        # 获取所有可见模型
        models = modelConfigUtil.get_provider_models(provider_id, only_visible=True)
        
        # 按类别分组
        categorized = {}
        for model in models:
            category = model.get('category', '其他')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(model)
            
        return jsonify({"success": True, "categories": categorized})
    except Exception as e:
        logger.error(f"获取分类模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/visibility', methods=['PUT'])
def toggle_model_visibility(provider_id):
    """切换模型可见性"""
    try:
        data = request.get_json()
        if not data or 'visible' not in data or 'modelId' not in data:
            return jsonify({"success": False, "message": "请提供模型ID和可见性参数"}), 400
        
        model_id = data.get('modelId')
        visible = data.get('visible')
        
        # 切换可见性
        success = modelConfigUtil.update_model_visibility(provider_id, model_id, visible)
        if not success:
            return jsonify({"success": False, "message": "更新模型可见性失败"}), 400
        
        return jsonify({"success": True, "message": "模型可见性已更新"})
    except Exception as e:
        logger.error(f"更新模型可见性时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/available-models', methods=['GET'])
def get_available_models(provider_id):
    """获取服务提供商的所有可用预设模型"""
    try:
        # 直接从modelConfigUtil获取模型列表
        models = modelConfigUtil.get_provider_models(provider_id)
        
        # 为Ollama特殊处理，如果没有预设模型，则使用通用模型
        if provider_id == 'ollama' and not models:
            models = [
                {
                    "id": "llama2",
                    "name": "Llama 2",
                    "category": "通用",
                    "description": "Llama 2 开源大模型",
                    "visible": True
                },
                {
                    "id": "llama2:13b",
                    "name": "Llama 2 13B",
                    "category": "通用",
                    "description": "Llama 2 13B 开源大模型",
                    "visible": True
                },
                {
                    "id": "qwen:4b",
                    "name": "Qwen 4B",
                    "category": "qwen",
                    "description": "通义千问4B开源大模型",
                    "visible": True
                }
            ]
            
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"获取预设模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/ollama/sync', methods=['POST'])
def sync_ollama_models():
    """手动同步本地Ollama模型
    
    返回:
        JSON: 成功/失败信息以及同步结果
    """
    logger.info("手动同步本地Ollama模型")
    
    try:
        import ollama
        
        # 获取本地Ollama模型列表
        local_models = ollama.list()
        local_model_ids = []
        
        # 提取模型ID列表
        if "models" in local_models and isinstance(local_models["models"], list):
            for model in local_models["models"]:
                if hasattr(model, 'model'):
                    local_model_ids.append(model.model)
                elif hasattr(model, 'name'):
                    local_model_ids.append(model.name)
        
        # 获取当前配置
        from service.common.model_common_service import model_service
        ollama_config = model_service.config.get('providers', {}).get('ollama', {})
        configured_models = ollama_config.get('models', [])
        
        # 保留已配置但本地也存在的模型
        models_to_keep = []
        models_removed = []
        
        for model in configured_models:
            model_id = model['id']
            if model_id in local_model_ids:
                models_to_keep.append(model)
            else:
                models_removed.append(model_id)
        
        # 添加本地存在但未配置的模型
        existing_ids = [m['id'] for m in models_to_keep]
        models_added = []
        
        for model_id in local_model_ids:
            if model_id not in existing_ids:
                # 创建新模型配置
                new_model = {
                    'id': model_id,
                    'name': model_id,
                    'category': '本地模型',
                    'description': f'Ollama本地模型 {model_id}',
                    'visible': True
                }
                models_to_keep.append(new_model)
                models_added.append(model_id)
        
        # 更新配置
        if 'ollama' in model_service.config.get('providers', {}):
            model_service.config['providers']['ollama']['models'] = models_to_keep
            model_service._save_config()
            
            # 准备返回消息
            message = "同步完成"
            if models_added:
                message += f"，新增模型: {', '.join(models_added)}"
            if models_removed:
                message += f"，移除模型: {', '.join(models_removed)}"
            
            return jsonify({
                "success": True,
                "message": message,
                "added": models_added,
                "removed": models_removed
            })
        else:
            return jsonify({
                "success": False,
                "message": "Ollama提供商不存在"
            })
            
    except ImportError:
        return jsonify({
            "success": False,
            "message": "未安装ollama包，无法同步模型"
        })
    except Exception as e:
        logger.error(f"同步Ollama模型时出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"同步失败: {str(e)}"
        }), 500

@model_settings_api.route('/api/settings/model/visible-models', methods=['GET'])
def get_all_visible_models():
    """获取所有服务提供商中可见的模型"""
    try:
        logger.info("API请求: 获取所有可见模型")
        all_visible_models = model_service.get_all_visible_models()
        logger.info(f"API响应: 获取所有可见模型成功，共 {len(all_visible_models)} 个模型")
        return jsonify({"success": True, "models": all_visible_models})
    except Exception as e:
        logger.error(f"获取所有可见模型时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500 