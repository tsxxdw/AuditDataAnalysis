#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from service.common.model_common_service import model_service
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
        providers = model_service.get_providers()
        return jsonify({"success": True, "providers": providers})
    except Exception as e:
        logger.error(f"获取服务提供商列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    """获取指定服务提供商信息"""
    try:
        provider = model_service.get_provider(provider_id)
        if not provider:
            return jsonify({"success": False, "message": "未找到指定的服务提供商"}), 404
        
        return jsonify({"success": True, "provider": provider})
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
        
        # 更新提供商信息
        success = model_service.update_provider(provider_id, data)
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
        models = model_service.get_models(provider_id)
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"获取模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/categories', methods=['GET'])
def get_models_by_category(provider_id):
    """按类别获取模型列表"""
    try:
        models_by_category = model_service.get_models_by_category(provider_id)
        return jsonify({"success": True, "categories": models_by_category})
    except Exception as e:
        logger.error(f"获取分类模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/add', methods=['POST'])
def add_model(provider_id):
    """添加模型"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        # 添加模型
        success = model_service.add_model(provider_id, data)
        if not success:
            return jsonify({"success": False, "message": "添加模型失败，请检查模型ID是否已存在"}), 400
        
        return jsonify({"success": True, "message": "模型添加成功"})
    except Exception as e:
        logger.error(f"添加模型时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/update', methods=['PUT'])
def update_model(provider_id):
    """更新模型信息"""
    try:
        data = request.get_json()
        if not data or 'modelId' not in data:
            return jsonify({"success": False, "message": "请提供模型ID和更新数据"}), 400
        
        model_id = data.pop('modelId')  # 从数据中提取模型ID并移除
        
        # 更新模型
        success = model_service.update_model(provider_id, model_id, data)
        if not success:
            return jsonify({"success": False, "message": "更新模型失败"}), 400
        
        return jsonify({"success": True, "message": "模型信息已更新"})
    except Exception as e:
        logger.error(f"更新模型信息时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/delete', methods=['DELETE'])
def delete_model(provider_id):
    """删除指定的模型"""
    try:
        # 从查询参数获取模型ID
        model_id = request.args.get('modelId')
        if not model_id:
            return jsonify({"success": False, "message": "请提供模型ID参数"}), 400
        
        # 删除模型
        success = model_service.delete_model(provider_id, model_id)
        
        if success:
            return jsonify({"success": True, "message": "模型已成功删除"})
        else:
            return jsonify({"success": False, "message": "删除模型失败，未找到指定模型或服务提供商"}), 404
    except Exception as e:
        logger.error(f"删除模型时发生错误: {str(e)}")
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
        success = model_service.toggle_model_visibility(provider_id, model_id, visible)
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
        # 从配置文件中读取预设模型
        config_path = os.path.join('config', 'settings', 'model_service_config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查提供商是否存在
        if provider_id not in config.get('providers', {}):
            return jsonify({"success": False, "message": "未找到指定的服务提供商"}), 404
            
        # 获取预设模型列表
        provider_config = config['providers'][provider_id]
        
        # 为Ollama特殊处理，如果没有预设模型，则使用通用模型
        if provider_id == 'ollama' and not provider_config.get('models'):
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
        else:
            models = provider_config.get('models', [])
            
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"获取预设模型列表时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/providers/ollama/available-models', methods=['GET'])
def get_ollama_available_models():
    """获取Ollama可用预设模型列表
    
    返回:
        JSON: 成功/失败信息以及可用模型列表
    """
    logger.info("获取Ollama可用预设模型列表")
    
    # 对于Ollama，我们只显示本地已安装的模型，不显示预设模型
    return jsonify({
        "success": True,
        "message": "Ollama仅使用本地安装的模型",
        "models": []  # 返回空列表以确保不显示预设模型
    })

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