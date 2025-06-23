#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import logging
from typing import Dict, List
from utils.encryption_util import  decrypt_api_key, is_encrypted
from service.log.logger import app_logger  # 导入app_logger
from service.common.model.model_log_common_service import model_log_service  # 导入model_log_service
from utils.settings.model_config_util import modelConfigUtil  # 导入modelConfigUtil

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelChatCommonService:
    """大模型对话服务类，负责处理与AI模型的对话交互"""
    
    def __init__(self, model_service=None):
        """初始化对话服务
        
        Args:
            model_service: ModelService实例，用于获取配置信息（已弃用，保留参数兼容旧代码）
        """
        # 不再使用model_service，保留参数仅为了兼容性
        pass
    
    def chat_completion(self, provider_id: str, model_id: str, messages: List[Dict], options: Dict = None) -> Dict:
        """调用大模型进行对话
        
        Args:
            provider_id: 服务提供商ID
            model_id: 模型ID
            messages: 消息列表
            options: 可选参数
            
        Returns:
            Dict: 模型响应结果
        """
        # 记录传递的参数
        app_logger.info(f"开始调用大模型 - 提供商: {provider_id}, 模型: {model_id}")
        app_logger.info(f"系统提示词: {messages[0]['content'] if messages and messages[0]['role'] == 'system' else '无'}")
        app_logger.info(f"用户提示词: {messages[-1]['content'] if messages and messages[-1]['role'] == 'user' else '无'}")
        if options:
            app_logger.info(f"调用参数: {options}")
        
        # 记录大模型调用信息到文件
        model_log_service.log_model_call(provider_id, model_id, messages)
        
        # 获取提供商配置
        config_data = modelConfigUtil._load_config()
        provider = config_data.get('providers', {}).get(provider_id)
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
        """Ollama特定的聊天API调用，支持流式和非流式模式
        
        Args:
            api_url: Ollama API地址
            model_id: 模型ID
            messages: 消息列表
            options: 可选参数
            
        Returns:
            Dict: 模型响应结果
        """
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
                                "created": int((lambda: __import__('time').time())()),
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
                            "created": int((lambda: __import__('time').time())()),
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

# 创建全局单例实例
model_chat_service = ModelChatCommonService()
