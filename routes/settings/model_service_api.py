#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from service.common.model_common_service import model_service
import logging

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

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/<model_id>/update', methods=['PUT'])
def update_model(provider_id, model_id):
    """更新模型信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        # 更新模型
        success = model_service.update_model(provider_id, model_id, data)
        if not success:
            return jsonify({"success": False, "message": "更新模型失败"}), 400
        
        return jsonify({"success": True, "message": "模型信息已更新"})
    except Exception as e:
        logger.error(f"更新模型信息时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/<model_id>/delete', methods=['DELETE'])
def delete_model(provider_id, model_id):
    """删除模型"""
    try:
        # 删除模型
        success = model_service.delete_model(provider_id, model_id)
        if not success:
            return jsonify({"success": False, "message": "删除模型失败"}), 400
        
        return jsonify({"success": True, "message": "模型已删除"})
    except Exception as e:
        logger.error(f"删除模型时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@model_settings_api.route('/api/settings/model/providers/<provider_id>/models/<model_id>/visibility', methods=['PUT'])
def toggle_model_visibility(provider_id, model_id):
    """切换模型可见性"""
    try:
        data = request.get_json()
        if not data or 'visible' not in data:
            return jsonify({"success": False, "message": "请提供可见性参数"}), 400
        
        visible = data.get('visible')
        
        # 切换可见性
        success = model_service.toggle_model_visibility(provider_id, model_id, visible)
        if not success:
            return jsonify({"success": False, "message": "更新模型可见性失败"}), 400
        
        return jsonify({"success": True, "message": "模型可见性已更新"})
    except Exception as e:
        logger.error(f"更新模型可见性时发生错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500 