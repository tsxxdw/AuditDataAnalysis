#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from utils.encryption_util import encrypt_api_key, decrypt_api_key, is_encrypted
from service.log.logger import app_logger  # 导入app_logger

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelService:
    """大模型服务类，负责与各种AI模型API交互"""
    
    CONFIG_PATH = os.path.join('config', 'settings', 'model_service_config.json')
    
    def __init__(self):
        """初始化模型服务"""
        self.config = self._load_config()
        self.default_provider = self.config.get('defaultProvider', 'ollama')
        
        # 启动时验证Ollama模型
        self._validate_ollama_models()
    
    def _load_config(self) -> Dict:
        """加载模型服务配置"""
        try:
            with open(self.CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 配置文件中的API密钥无需在这里解密
                # 只有在实际使用时才解密
                
                return config
        except Exception as e:
            logger.error(f"加载模型配置文件失败: {str(e)}")
            # 返回默认配置
            return {"defaultProvider": "ollama", "providers": {}}
    
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
            
            with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存模型配置文件失败: {str(e)}")
            return False
    
    def get_providers(self) -> List[Dict]:
        """获取所有服务提供商信息"""
        providers = []
        for key, provider in self.config.get('providers', {}).items():
            # 创建提供商信息的副本，去除敏感信息
            provider_info = {
                'id': key,
                'name': provider.get('name', key),
                'apiUrl': provider.get('apiUrl', ''),
                'enabled': provider.get('enabled', False),
                'hasApiKey': bool(provider.get('apiKey', ''))
            }
            providers.append(provider_info)
        
        return providers
    
    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """获取指定服务提供商信息"""
        provider = self.config.get('providers', {}).get(provider_id)
        if not provider:
            return None
        
        # 创建提供商信息的副本，去除敏感信息
        return {
            'id': provider_id,
            'name': provider.get('name', provider_id),
            'apiUrl': provider.get('apiUrl', ''),
            'apiVersion': provider.get('apiVersion', 'v1'),
            'enabled': provider.get('enabled', False),
            'hasApiKey': bool(provider.get('apiKey', ''))
        }
    
    def get_models(self, provider_id: str = None) -> List[Dict]:
        """获取指定提供商的模型列表，不指定则获取默认提供商的模型"""
        if not provider_id:
            provider_id = self.default_provider
        
        provider = self.config.get('providers', {}).get(provider_id)
        if not provider:
            return []
        
        return provider.get('models', [])
    
    def get_models_by_category(self, provider_id: str = None) -> Dict[str, List[Dict]]:
        """按类别获取模型列表"""
        models = self.get_models(provider_id)
        categorized = {}
        
        for model in models:
            if model.get('visible', True):
                category = model.get('category', '其他')
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(model)
        
        return categorized
    
    def update_provider(self, provider_id: str, data: Dict) -> bool:
        """更新服务提供商配置"""
        if provider_id not in self.config.get('providers', {}):
            return False
        
        # 只更新允许的字段
        allowed_fields = ['apiKey', 'apiUrl', 'apiVersion', 'enabled', 'name']
        for field in allowed_fields:
            if field in data:
                # 对API密钥特殊处理：加密后再存储
                if field == 'apiKey' and data[field]:
                    # 加密API密钥
                    self.config['providers'][provider_id][field] = encrypt_api_key(data[field])
                else:
                    self.config['providers'][provider_id][field] = data[field]
        
        return self._save_config()
    
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
    
    def add_model(self, provider_id: str, model_data: Dict) -> bool:
        """添加模型到提供商"""
        if provider_id not in self.config.get('providers', {}):
            return False
        
        # 验证必要字段
        required_fields = ['id', 'name', 'category']
        for field in required_fields:
            if field not in model_data:
                return False
        
        # 检查模型ID是否已存在
        models = self.config['providers'][provider_id].get('models', [])
        for model in models:
            if model['id'] == model_data['id']:
                return False  # 模型已存在
        
        # 设置默认值
        model_data.setdefault('visible', True)
        model_data.setdefault('description', '')
        
        # 添加模型
        if 'models' not in self.config['providers'][provider_id]:
            self.config['providers'][provider_id]['models'] = []
        
        self.config['providers'][provider_id]['models'].append(model_data)
        return self._save_config()
    
    def update_model(self, provider_id: str, model_id: str, data: Dict) -> bool:
        """更新模型信息"""
        if provider_id not in self.config.get('providers', {}):
            return False
        
        # 查找模型
        models = self.config['providers'][provider_id].get('models', [])
        for i, model in enumerate(models):
            if model['id'] == model_id:
                # 只更新允许的字段
                allowed_fields = ['name', 'visible', 'category', 'description']
                for field in allowed_fields:
                    if field in data:
                        self.config['providers'][provider_id]['models'][i][field] = data[field]
                return self._save_config()
        
        return False  # 未找到模型
    
    def delete_model(self, provider_id: str, model_id: str) -> bool:
        """删除模型"""
        if provider_id not in self.config.get('providers', {}):
            return False
        
        # 查找并删除模型
        models = self.config['providers'][provider_id].get('models', [])
        for i, model in enumerate(models):
            if model['id'] == model_id:
                self.config['providers'][provider_id]['models'].pop(i)
                return self._save_config()
        
        return False  # 未找到模型
    
    def toggle_model_visibility(self, provider_id: str, model_id: str, visible: bool) -> bool:
        """切换模型的可见性"""
        return self.update_model(provider_id, model_id, {'visible': visible})
    
    def chat_completion(self, provider_id: str, model_id: str, messages: List[Dict], options: Dict = None) -> Dict:
        """调用大模型进行对话"""
        # 记录传递的参数
        app_logger.info(f"开始调用大模型 - 提供商: {provider_id}, 模型: {model_id}")
        app_logger.info(f"系统提示词: {messages[0]['content'] if messages and messages[0]['role'] == 'system' else '无'}")
        app_logger.info(f"用户提示词: {messages[-1]['content'] if messages and messages[-1]['role'] == 'user' else '无'}")
        if options:
            app_logger.info(f"调用参数: {options}")
        
        # 获取提供商配置
        provider = self.config.get('providers', {}).get(provider_id)
        if not provider:
            error_msg = "未找到指定的服务提供商"
            app_logger.error(f"调用大模型失败 - {error_msg}")
            return {"error": error_msg}
        
        # 检查模型是否存在
        model_exists = False
        for model in provider.get('models', []):
            if model['id'] == model_id:
                model_exists = True
                break
        
        if not model_exists:
            error_msg = "未找到指定的模型"
            app_logger.error(f"调用大模型失败 - {error_msg}")
            return {"error": error_msg}
        
        # 准备请求参数
        api_key = provider.get('apiKey', '')
        # 解密API密钥
        if api_key and is_encrypted(api_key):
            api_key = decrypt_api_key(api_key)
            
        api_url = provider.get('apiUrl', '')
        api_version = provider.get('apiVersion', 'v1')
        
        if not api_url:
            error_msg = "API地址不能为空"
            app_logger.error(f"调用大模型失败 - {error_msg}")
            return {"error": error_msg}
        
        # 对Ollama特殊处理
        if provider_id == 'ollama':
            result = self._ollama_chat_completion(api_url, model_id, messages, options)
            # 记录返回结果
            if "error" in result:
                app_logger.error(f"调用大模型失败 - {result['error']}")
            else:
                generated_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                app_logger.info(f"大模型调用成功 - 提供商: {provider_id}, 模型: {model_id}")
                app_logger.info(f"生成内容: {generated_content[:200]}..." if len(generated_content) > 200 else f"生成内容: {generated_content}")
            return result
        
        # 一般大模型API (OpenAI兼容格式)
        headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # 构建请求体
        request_body = {
            "model": model_id,
            "messages": messages
        }
        
        # 添加可选参数
        if options:
            for key, value in options.items():
                request_body[key] = value
        
        # 发送请求
        try:
            url = f"{api_url}/{api_version}/chat/completions"
            app_logger.debug(f"发送API请求到 {url}")
            
            response = requests.post(url, headers=headers, json=request_body, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                generated_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                app_logger.info(f"大模型调用成功 - 提供商: {provider_id}, 模型: {model_id}")
                app_logger.info(f"生成内容: {generated_content[:200]}..." if len(generated_content) > 200 else f"生成内容: {generated_content}")
                return result
            else:
                error_msg = f"API调用失败，状态码: {response.status_code}, 响应: {response.text}"
                app_logger.error(f"大模型调用失败 - {error_msg}")
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"调用模型时发生错误: {str(e)}"
            app_logger.error(f"大模型调用失败 - {error_msg}")
            return {"error": error_msg}
    
    def _ollama_chat_completion(self, api_url: str, model_id: str, messages: List[Dict], options: Dict = None) -> Dict:
        """Ollama特定的聊天API调用"""
        try:
            # Ollama API格式与OpenAI有所不同
            url = f"{api_url}/api/chat"
            app_logger.debug(f"发送Ollama请求到 {url}")
            
            # 构建请求体
            request_body = {
                "model": model_id,
                "messages": messages
            }
            
            # 添加可选参数
            if options:
                for key, value in options.items():
                    request_body[key] = value
            
            # 发送请求
            response = requests.post(url, json=request_body, timeout=60)
            
            if response.status_code == 200:
                # 将Ollama响应转换为OpenAI兼容格式
                ollama_response = response.json()
                generated_content = ollama_response.get("message", {}).get("content", "")
                app_logger.info(f"Ollama调用成功 - 模型: {model_id}")
                app_logger.debug(f"Ollama生成内容: {generated_content[:200]}..." if len(generated_content) > 200 else f"Ollama生成内容: {generated_content}")
                
                return {
                    "id": f"ollama-{model_id}",
                    "object": "chat.completion",
                    "created": int(import_time()),
                    "model": model_id,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": generated_content
                            },
                            "finish_reason": "stop"
                        }
                    ]
                }
            else:
                error_msg = f"Ollama API调用失败，状态码: {response.status_code}"
                app_logger.error(f"Ollama调用失败 - {error_msg}\n响应: {response.text}")
                return {
                    "error": error_msg,
                    "details": response.text
                }
        except Exception as e:
            error_msg = f"调用Ollama模型时发生错误: {str(e)}"
            app_logger.error(f"Ollama调用失败 - {error_msg}")
            return {"error": error_msg}
    
    def get_all_visible_models(self) -> List[Dict]:
        """获取所有服务提供商中可见的模型"""
        all_visible_models = []
        
        for provider_id, provider in self.config.get('providers', {}).items():
            # 只考虑启用的服务提供商
            if not provider.get('enabled', False):
                continue
                
            provider_name = provider.get('name', provider_id)
            
            # 获取该提供商的所有可见模型
            for model in provider.get('models', []):
                if model.get('visible', True):
                    # 创建包含提供商信息的完整模型数据
                    full_model = model.copy()
                    full_model['provider_id'] = provider_id
                    full_model['provider_name'] = provider_name
                    all_visible_models.append(full_model)
        
        return all_visible_models
    
    def get_default_model(self) -> Dict:
        """获取默认模型的信息"""
        # 首先检查是否设置了全局默认模型
        global_default = self.config.get('defaultModel')
        if global_default:
            provider_id = global_default.get('provider_id')
            model_id = global_default.get('model_id')
            
            # 确保提供商和模型存在且可用
            if provider_id and model_id:
                provider = self.config.get('providers', {}).get(provider_id)
                if provider and provider.get('enabled', False):
                    for model in provider.get('models', []):
                        if model.get('id') == model_id and model.get('visible', True):
                            # 创建包含提供商信息的完整模型数据
                            full_model = model.copy()
                            full_model['provider_id'] = provider_id
                            full_model['provider_name'] = provider.get('name', provider_id)
                            return full_model
        
        # 如果没有设置默认模型或默认模型不可用，返回空字典
        return {}
    
    def set_default_model(self, provider_id: str, model_id: str) -> bool:
        """设置默认模型"""
        # 验证提供商和模型是否存在且可用
        provider = self.config.get('providers', {}).get(provider_id)
        if not provider or not provider.get('enabled', False):
            return False
            
        model_exists = False
        for model in provider.get('models', []):
            if model.get('id') == model_id and model.get('visible', True):
                model_exists = True
                break
                
        if not model_exists:
            return False
            
        # 设置默认模型
        self.config['defaultModel'] = {
            'provider_id': provider_id,
            'model_id': model_id
        }
        
        # 保存配置
        return self._save_config()

# 创建全局单例实例
model_service = ModelService()

# 辅助方法
def import_time():
    """导入time模块并获取当前时间戳"""
    import time
    return time.time() 