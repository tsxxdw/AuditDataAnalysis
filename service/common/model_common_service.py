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

class ModelService:
    """大模型服务类，负责与各种AI模型API交互"""
    
    CONFIG_PATH = os.path.join('config', 'settings', 'model_config.json')
    
    def __init__(self):
        """初始化模型服务"""
        self.config = self._load_config()
        self.default_provider = self.config.get('defaultProvider', 'ollama')
        
        # 启动时验证Ollama模型
        self._validate_ollama_models()
        
        # 初始化聊天服务
        global model_chat_service
        from service.common.model.model_chat_common_service import model_chat_service
        if model_chat_service is None:
            model_chat_service = ModelChatCommonService(self)
    
    def _load_config(self) -> Dict:
        """加载模型服务配置"""
        try:
            # 记录当前工作目录和配置文件的绝对路径
            current_dir = os.getcwd()
            abs_config_path = os.path.abspath(self.CONFIG_PATH)
            logger.info(f"加载模型配置 - 当前工作目录: {current_dir}")
            logger.info(f"加载模型配置 - 配置文件绝对路径: {abs_config_path}")
            
            # 检查文件是否存在
            if not os.path.exists(self.CONFIG_PATH):
                logger.warning(f"加载模型配置 - 配置文件不存在: {self.CONFIG_PATH}")
                # 返回默认配置
                default_config = {"defaultProvider": "ollama", "providers": {}}
                logger.info(f"加载模型配置 - 返回默认配置: {default_config}")
                return default_config
            
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 记录加载到的默认模型
                if 'defaultModel' in config:
                    logger.info(f"加载模型配置 - 读取到的默认模型: {config['defaultModel']}")
                else:
                    logger.warning("加载模型配置 - 配置中没有默认模型设置")
                
                # 配置文件中的API密钥无需在这里解密
                # 只有在实际使用时才解密
                
                return config
        except Exception as e:
            logger.error(f"加载模型配置文件失败: {str(e)}")
            # 返回默认配置
            default_config = {"defaultProvider": "ollama", "providers": {}}
            logger.info(f"加载模型配置 - 因错误返回默认配置")
            return default_config
    
    def _validate_ollama_models(self) -> None:
        """验证Ollama模型配置，移除本地不存在的模型记录"""
        try:
            # 检查Ollama提供商是否存在
            if 'ollama' not in self.config.get('providers', {}):
                logger.info("Ollama提供商不存在，跳过验证")
                return
            
            # 获取Ollama提供商的配置
            ollama_provider = self.config['providers']['ollama']
            
            # 检查是否有配置的模型
            if 'models' not in ollama_provider or not ollama_provider['models']:
                logger.info("Ollama没有配置的模型，跳过验证")
                return
            
            # 尝试获取本地Ollama模型列表
            try:
                import ollama
                local_models = ollama.list()
                
                # 提取模型ID列表
                local_model_ids = []
                if "models" in local_models and isinstance(local_models["models"], list):
                    for model in local_models["models"]:
                        if hasattr(model, 'model'):
                            local_model_ids.append(model.model)
                        elif hasattr(model, 'name'):
                            local_model_ids.append(model.name)
                
                logger.info(f"本地Ollama模型列表: {local_model_ids}")
                
                # 检查配置中的每个模型是否在本地存在
                if not local_model_ids:
                    logger.warning("未获取到本地Ollama模型列表，无法验证")
                    return
                
                models_to_keep = []
                models_to_remove = []
                
                for model in ollama_provider['models']:
                    model_id = model['id']
                    if model_id in local_model_ids:
                        models_to_keep.append(model)
                    else:
                        models_to_remove.append(model_id)
                
                # 如果有需要移除的模型
                if models_to_remove:
                    logger.info(f"移除不存在的Ollama模型: {models_to_remove}")
                    ollama_provider['models'] = models_to_keep
                    self._save_config()
                    logger.info("已更新Ollama模型配置")
                else:
                    logger.info("所有配置的Ollama模型都存在于本地")
                
            except ImportError:
                logger.warning("未安装ollama包，无法验证Ollama模型")
            except Exception as e:
                logger.error(f"验证Ollama模型时出错: {str(e)}")
        
        except Exception as e:
            logger.error(f"验证Ollama模型配置时发生错误: {str(e)}")
    
    def _save_config(self) -> bool:
        """保存模型服务配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            
            # 添加日志记录当前工作目录和配置文件的绝对路径
            current_dir = os.getcwd()
            abs_config_path = os.path.abspath(self.CONFIG_PATH)
            logger.info(f"保存模型配置 - 当前工作目录: {current_dir}")
            logger.info(f"保存模型配置 - 配置文件绝对路径: {abs_config_path}")
            logger.info(f"保存模型配置 - 配置内容: {json.dumps(self.config, ensure_ascii=False)}")
            
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # 验证文件是否成功写入
            if os.path.exists(self.CONFIG_PATH):
                file_size = os.path.getsize(self.CONFIG_PATH)
                logger.info(f"保存模型配置 - 文件已保存，大小: {file_size} 字节")
                
                # 读取文件内容进行验证
                try:
                    with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                        saved_config = json.load(f)
                    logger.info(f"保存模型配置 - 文件内容验证成功")
                    
                    # 验证默认模型是否正确保存
                    if 'defaultModel' in saved_config:
                        logger.info(f"保存模型配置 - 默认模型已保存: {saved_config['defaultModel']}")
                    else:
                        logger.warning("保存模型配置 - 默认模型未在保存的配置中找到")
                except Exception as e:
                    logger.error(f"保存模型配置 - 验证文件内容时出错: {str(e)}")
            else:
                logger.error(f"保存模型配置 - 文件保存后不存在: {self.CONFIG_PATH}")
            
            return True
        except Exception as e:
            logger.error(f"保存模型配置文件失败: {str(e)}")
            return False
    
    def test_connection(self, provider_id: str, api_key: str = None, api_url: str = None) -> Dict:
        """测试与服务提供商的连接"""
        provider = self.config.get('providers', {}).get(provider_id)
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
model_service = ModelService() 