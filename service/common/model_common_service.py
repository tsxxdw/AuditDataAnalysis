#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import logging
import datetime
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
        
        # 确保日志目录存在
        self._ensure_log_directories()
    
    def _ensure_log_directories(self):
        """确保日志目录存在"""
        try:
            # 创建根目录的file文件夹
            root_file_dir = os.path.join('file')
            os.makedirs(root_file_dir, exist_ok=True)
            
            # 创建大模型调用记录文件夹
            big_model_dir = os.path.join(root_file_dir, 'big_model_call_record')
            os.makedirs(big_model_dir, exist_ok=True)
            app_logger.info(f"确保大模型调用记录目录存在: {big_model_dir}")
            
            # 创建当前日期的文件夹 (格式: YYYYMMDD)
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            date_dir = os.path.join(big_model_dir, current_date)
            os.makedirs(date_dir, exist_ok=True)
            app_logger.info(f"确保日期目录存在: {date_dir}")
        except Exception as e:
            app_logger.error(f"创建日志目录时出错: {str(e)}")
    
    def _log_model_call(self, provider_id: str, model_id: str, messages: List[Dict]) -> None:
        """记录大模型调用信息到文件
        
        Args:
            provider_id: 服务提供商ID
            model_id: 模型ID
            messages: 提示词消息列表
        """
        try:
            # 创建时间戳作为文件名 (保持原格式以便于文件排序)
            timestamp_for_filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            
            # 创建格式化的时间戳用于日志内容显示
            formatted_timestamp = datetime.datetime.now().strftime('%Y:%m:%d %H时%M分%S秒')
            
            # 获取当前日期作为目录名
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            
            # 构建日志文件路径
            log_dir = os.path.join('file', 'big_model_call_record', current_date)
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{timestamp_for_filename}.txt")
            
            # 提取系统提示词和用户提示词
            system_prompt = "无系统提示词"
            user_prompt = "无用户提示词"
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    user_prompt = msg['content']
            
            # 组装日志内容 (使用格式化的时间戳)
            log_content = f"调用时间: {formatted_timestamp}\n"
            log_content += f"服务提供商: {provider_id}\n"
            log_content += f"模型: {model_id}\n"
            log_content += f"\n系统提示词:\n{system_prompt}\n"
            log_content += f"\n用户提示词:\n{user_prompt}\n"
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            app_logger.info(f"已记录大模型调用日志到文件: {log_file}")
        except Exception as e:
            app_logger.error(f"记录大模型调用日志失败: {str(e)}")
            
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
        
        # 记录大模型调用信息到文件
        self._log_model_call(provider_id, model_id, messages)
        
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
        """Ollama特定的聊天API调用，支持流式和非流式模式"""
        try:
            # 确定是否使用流式模式，默认为True
            use_stream = True
            if options and 'stream' in options:
                use_stream = options['stream']
            
            # 构建请求体
            request_body = {
                "model": model_id,
                "messages": messages,
                "stream": use_stream
            }
            
            # 添加可选参数
            if options:
                for key, value in options.items():
                    if key != 'stream':  # 避免重复添加stream参数
                        request_body[key] = value
            
            # 记录请求体
            app_logger.debug(f"Ollama请求体: {json.dumps(request_body, ensure_ascii=False)}")
            
            # 根据模式选择不同的API端点
            if use_stream:
                # 流式模式使用/api/chat
                url = f"{api_url}/api/chat"
                app_logger.debug(f"使用流式模式，发送Ollama请求到 {url}")
                
                # 发送流式请求
                response = requests.post(url, json=request_body, stream=True, timeout=60)
                
                # 记录响应状态码
                app_logger.debug(f"Ollama响应状态码: {response.status_code}")
                app_logger.debug(f"Ollama响应头: {response.headers}")
                
                if response.status_code == 200:
                    # 处理流式响应
                    full_content = ""
                    last_response = None
                    
                    try:
                        for line in response.iter_lines():
                            if line:
                                try:
                                    # 解析每行JSON
                                    data = json.loads(line.decode('utf-8'))
                                    app_logger.debug(f"收到流式数据: {json.dumps(data, ensure_ascii=False)[:100]}...")
                                    
                                    # 提取响应内容
                                    if 'message' in data and 'content' in data['message']:
                                        chunk = data['message']['content']
                                        full_content += chunk
                                    
                                    # 保存最后一个完整响应
                                    last_response = data
                                    
                                    # 如果响应完成，记录日志
                                    if data.get('done', False):
                                        app_logger.debug("流式响应完成")
                                        break
                                        
                                except json.JSONDecodeError as je:
                                    app_logger.error(f"解析流式JSON失败: {str(je)}")
                                    app_logger.error(f"问题行内容: {line.decode('utf-8')}")
                        
                        # 使用最后一个响应构建返回结果
                        if last_response:
                            app_logger.info(f"Ollama流式调用成功 - 模型: {model_id}")
                            app_logger.debug(f"Ollama生成内容: {full_content[:200]}..." if len(full_content) > 200 else f"Ollama生成内容: {full_content}")
                            
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
                                            "content": full_content
                                        },
                                        "finish_reason": "stop"
                                    }
                                ]
                            }
                        else:
                            error_msg = "未收到有效的流式响应"
                            app_logger.error(f"Ollama调用失败 - {error_msg}")
                            return {"error": error_msg}
                            
                    except Exception as e:
                        error_msg = f"处理流式响应时发生错误: {str(e)}"
                        app_logger.error(f"Ollama调用失败 - {error_msg}")
                        import traceback
                        app_logger.error(f"异常堆栈: {traceback.format_exc()}")
                        return {"error": error_msg}
                else:
                    error_msg = f"Ollama API调用失败，状态码: {response.status_code}"
                    app_logger.error(f"Ollama调用失败 - {error_msg}")
                    try:
                        response_text = response.text
                        app_logger.error(f"响应内容: {response_text}")
                        return {
                            "error": error_msg,
                            "details": response_text
                        }
                    except:
                        return {"error": error_msg}
            else:
                # 非流式模式使用/api/generate
                url = f"{api_url}/api/generate"
                app_logger.debug(f"使用非流式模式，发送Ollama请求到 {url}")
                
                # 将messages转换为prompt格式
                prompt = ""
                for msg in messages:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    
                    if role == 'system':
                        prompt += f"System: {content}\n\n"
                    elif role == 'user':
                        prompt += f"User: {content}\n\n"
                    elif role == 'assistant':
                        prompt += f"Assistant: {content}\n\n"
                
                # 构建非流式请求体
                generate_body = {
                    "model": model_id,
                    "prompt": prompt.strip(),
                    "stream": False
                }
                
                # 添加options参数
                if options and 'options' in options:
                    generate_body["options"] = options['options']
                elif options:
                    generate_body["options"] = {}
                    for key, value in options.items():
                        if key not in ['stream', 'messages', 'model']:
                            generate_body["options"][key] = value
                
                app_logger.debug(f"非流式请求体: {json.dumps(generate_body, ensure_ascii=False)}")
                
                # 发送非流式请求
                response = requests.post(url, json=generate_body, timeout=60)
                
                # 记录原始响应
                app_logger.debug(f"Ollama响应状态码: {response.status_code}")
                app_logger.debug(f"Ollama响应头: {response.headers}")
                app_logger.debug(f"Ollama原始响应内容: {response.text[:500]}..." if len(response.text) > 500 else f"Ollama原始响应内容: {response.text}")
                
                if response.status_code == 200:
                    try:
                        # 解析JSON响应
                        ollama_response = response.json()
                        generated_content = ollama_response.get("response", "")
                        
                        app_logger.info(f"Ollama非流式调用成功 - 模型: {model_id}")
                        app_logger.debug(f"Ollama生成内容: {generated_content[:200]}..." if len(generated_content) > 200 else f"Ollama生成内容: {generated_content}")
                        
                        # 返回OpenAI兼容格式
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
                    except json.JSONDecodeError as je:
                        error_msg = f"解析Ollama响应JSON失败: {str(je)}"
                        app_logger.error(f"Ollama调用失败 - {error_msg}")
                        app_logger.error(f"JSON解析错误位置: 行 {je.lineno}, 列 {je.colno}, 字符位置 {je.pos}")
                        app_logger.error(f"JSON文档片段: '{response.text[max(0, je.pos-20):je.pos]}' >>> '{response.text[je.pos:min(len(response.text), je.pos+20)]}'")
                        return {"error": error_msg}
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
            import traceback
            app_logger.error(f"异常堆栈: {traceback.format_exc()}")
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
        logger.info(f"设置默认模型 - 提供商ID: {provider_id}, 模型ID: {model_id}")
        
        # 验证提供商和模型是否存在且可用
        provider = self.config.get('providers', {}).get(provider_id)
        if not provider or not provider.get('enabled', False):
            logger.error(f"设置默认模型 - 提供商不存在或未启用: {provider_id}")
            return False
            
        model_exists = False
        for model in provider.get('models', []):
            if model.get('id') == model_id and model.get('visible', True):
                model_exists = True
                logger.info(f"设置默认模型 - 找到匹配的模型: {model_id}")
                break
                
        if not model_exists:
            logger.error(f"设置默认模型 - 未找到匹配的模型: {model_id}")
            return False
            
        # 记录之前的默认模型（如果有）
        old_default = self.config.get('defaultModel', {})
        logger.info(f"设置默认模型 - 之前的默认模型: {old_default}")
        
        # 设置默认模型
        self.config['defaultModel'] = {
            'provider_id': provider_id,
            'model_id': model_id
        }
        
        logger.info(f"设置默认模型 - 新的默认模型设置为: {self.config['defaultModel']}")
        
        # 保存配置
        save_result = self._save_config()
        logger.info(f"设置默认模型 - 配置保存结果: {'成功' if save_result else '失败'}")
        return save_result

# 创建全局单例实例
model_service = ModelService()

# 辅助方法
def import_time():
    """导入time模块并获取当前时间戳"""
    import time
    return time.time() 