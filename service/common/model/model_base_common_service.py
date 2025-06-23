#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
from utils.encryption_util import encrypt_api_key, decrypt_api_key, is_encrypted
from utils.settings.model_config_util import modelConfigUtil  # 导入modelConfigUtil
from service.log.logger import app_logger  # 导入app_logger
from service.common.model.model_log_common_service import model_log_service  # 导入model_log_service
from service.common.model.model_chat_common_service import ModelChatCommonService, model_chat_service  # 导入ModelChatCommonService和model_chat_service

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelBaseCommonService:
    """大模型服务类，负责与各种AI模型API交互"""
    
    def __init__(self):
        """初始化模型服务"""
        # 空实现，所有功能通过modelConfigUtil实现
        pass
    
    def test_connection(self, provider_id: str, api_key: str = None, api_url: str = None) -> Dict:
        """测试与服务提供商的连接"""
        config_data = modelConfigUtil._load_config()
        provider = config_data.get('providers', {}).get(provider_id)
        
        if not provider:
            return {"success": False, "message": "未找到指定的服务提供商"}
        
        # 使用传入的参数，否则使用配置中的参数（需解密）
        stored_api_key = provider.get('apiKey', '')
        if stored_api_key and is_encrypted(stored_api_key):
            stored_api_key = decrypt_api_key(stored_api_key)
            
        api_key = api_key or stored_api_key
        api_url = api_url or provider.get('apiUrl', '')
        api_version = provider.get('apiVersion', 'v1')
        
        # 如果没有API密钥但是需要的情况下，返回错误
        if not api_key and provider_id not in ['ollama']:  # Ollama本地服务可能不需要API密钥
            return {"success": False, "message": "API密钥不能为空"}
        
        if not api_url:
            return {"success": False, "message": "API地址不能为空"}
        
        # 构建测试请求
        try:
            # 根据不同提供商构建不同的测试请求
            if provider_id == 'ollama':
                # Ollama使用List models API
                url = f"{api_url}/api/tags"
                response = requests.get(url, timeout=5)
            else:
                # 通用测试方法，尝试获取模型列表或简单的验证接口
                url = f"{api_url}/{api_version}/models"
                headers = {"Authorization": f"Bearer {api_key}"}
                response = requests.get(url, headers=headers, timeout=5)
            
            # 检查响应
            if response.status_code == 200:
                return {"success": True, "message": "连接成功"}
            else:
                return {
                    "success": False, 
                    "message": f"连接失败，状态码: {response.status_code}", 
                    "details": response.text
                }
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "无法连接到服务器，请检查API地址"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "连接超时，请检查API地址"}
        except Exception as e:
            logger.error(f"测试连接时发生错误: {str(e)}")
            return {"success": False, "message": f"发生错误: {str(e)}"}

# 创建全局单例实例
model_base_common_service = ModelBaseCommonService()
