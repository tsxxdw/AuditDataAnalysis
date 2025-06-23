"""
本地知识库API路由

处理知识库相关的接口请求，包括文件上传、文本添加、知识库检索等
"""

import os
import uuid
import logging
import traceback
from flask import Blueprint, request, jsonify, current_app
from service.log.logger import app_logger
from service.knowledge_base.kb_service import (
    process_document, 
    add_text_to_knowledge_base,
    search_knowledge_base,
    get_knowledge_items,
    delete_knowledge_item,
    get_knowledge_item_by_id,
)
from werkzeug.utils import secure_filename
from service.common.model.model_base_common_service import ModelBaseCommonService, model_base_common_service as model_service
from service.common.model.model_chat_common_service import model_chat_service
from utils.settings.model_config_util import modelConfigUtil

# 创建知识库API蓝图
knowledge_base_api = Blueprint('knowledge_base_api', __name__)
logger = logging.getLogger(__name__)

# 确保知识库文件夹存在
def ensure_kb_dirs_exist():
    """确保知识库相关目录存在"""
    kb_dirs = [
        'file/knowledge_base',
        'file/knowledge_base/documents',
        'file/knowledge_base/embeddings'
    ]
    for directory in kb_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app_logger.info(f"创建知识库目录: {directory}")

# 初始化知识库目录
ensure_kb_dirs_exist()

# 允许的文件类型
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx'}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@knowledge_base_api.route('/api/knowledge_base/upload', methods=['POST'])
def upload_files():
    """文件上传到知识库接口"""
    try:
        # 检查是否有文件
        if 'files[]' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有文件被上传'
            }), 400
        
        files = request.files.getlist('files[]')
        
        # 检查文件是否为空
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 获取分块方式
        chunking_strategy = request.form.get('chunking_strategy', 'auto')
        custom_chunk_size = request.form.get('custom_chunk_size', None)
        
        if custom_chunk_size and custom_chunk_size.isdigit():
            custom_chunk_size = int(custom_chunk_size)
        else:
            custom_chunk_size = None
        
        processed_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # 安全地获取文件名
                original_filename = secure_filename(file.filename)
                file_id = str(uuid.uuid4())
                
                # 确保文件扩展名被正确保留
                name, ext = os.path.splitext(original_filename)
                if not ext and '.' in original_filename:
                    # 如果secure_filename处理后丢失了扩展名，尝试从原始文件名获取
                    ext = os.path.splitext(file.filename)[1].lower()
                
                # 如果仍然没有扩展名，检查文件类型并添加适当的扩展名
                if not ext:
                    content_type = file.content_type
                    print(f"[DEBUG] 文件内容类型: {content_type}")
                    if 'word' in content_type:
                        ext = '.docx'
                    elif 'text/plain' in content_type:
                        ext = '.txt'
                
                # 构建保存路径
                saved_filename = f"{file_id}{ext}"
                file_path = os.path.join('file/knowledge_base/documents', saved_filename)
                
                # 保存文件
                file.save(file_path)
                app_logger.info(f"文件保存成功: {file_path}")
                print(f"[DEBUG] 文件已保存: {file_path}, 原始文件名: {original_filename}, 扩展名: {ext}")
                
                # 处理文件并添加到知识库
                result = process_document(
                    file_path, 
                    chunking_strategy=chunking_strategy,
                    custom_chunk_size=custom_chunk_size
                )
                
                if result['success']:
                    processed_files.append({
                        'filename': original_filename,
                        'id': file_id,
                        'document_type': result['document_type'],
                        'chunks_count': result['chunks_count']
                    })
                else:
                    # 处理失败，删除已上传的文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    return jsonify({
                        'success': False,
                        'message': f"处理文件 {original_filename} 失败: {result['message']}"
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'message': f"不支持的文件类型: {file.filename}"
                }), 400
        
        return jsonify({
            'success': True,
            'message': f"成功处理 {len(processed_files)} 个文件",
            'files': processed_files
        })
    
    except Exception as e:
        app_logger.error(f"文件上传处理异常: {str(e)}")
        print(f"[DEBUG] 文件上传处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"处理上传文件时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/text', methods=['POST'])
def add_text():
    """添加文本到知识库接口"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', [])
        
        # 验证输入
        if not title:
            return jsonify({
                'success': False,
                'message': '标题不能为空'
            }), 400
        
        if not content:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400
        
        # 添加文本到知识库
        result = add_text_to_knowledge_base(title, content, tags)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '文本成功添加到知识库',
                'id': result['id']
            })
        else:
            return jsonify({
                'success': False,
                'message': f"添加文本到知识库失败: {result['message']}"
            }), 500
    
    except Exception as e:
        app_logger.error(f"添加文本到知识库异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"添加文本到知识库时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/search', methods=['GET'])
def search():
    """搜索知识库接口"""
    try:
        query = request.args.get('query', '').strip()
        filter_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 10)
        
        # 尝试将limit转换为整数
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # 验证输入
        if not query:
            return jsonify({
                'success': False,
                'message': '搜索查询不能为空'
            }), 400
        
        # 搜索知识库
        results = search_knowledge_base(query, filter_type, limit)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        app_logger.error(f"搜索知识库异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"搜索知识库时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/items', methods=['GET'])
def get_items():
    """获取知识库项目列表接口"""
    try:
        filter_type = request.args.get('type', 'all')
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 10)
        
        # 尝试将page和per_page转换为整数
        try:
            page = int(page)
            per_page = int(per_page)
        except ValueError:
            page = 1
            per_page = 10
        
        # 获取知识库项目
        items, total = get_knowledge_items(filter_type, page, per_page)
        
        return jsonify({
            'success': True,
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        app_logger.error(f"获取知识库项目列表异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取知识库项目列表时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/items/<item_id>', methods=['GET'])
def get_item(item_id):
    """获取单个知识库项目详情接口"""
    try:
        # 获取知识库项目详情
        item = get_knowledge_item_by_id(item_id)
        
        if item:
            return jsonify({
                'success': True,
                'item': item
            })
        else:
            return jsonify({
                'success': False,
                'message': '未找到指定的知识库项目'
            }), 404
    
    except Exception as e:
        app_logger.error(f"获取知识库项目详情异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取知识库项目详情时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """删除知识库项目接口"""
    try:
        # 删除知识库项目
        result = delete_knowledge_item(item_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '知识库项目已成功删除'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404 if 'not found' in result['message'].lower() else 500
    
    except Exception as e:
        app_logger.error(f"删除知识库项目异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"删除知识库项目时发生错误: {str(e)}"
        }), 500

@knowledge_base_api.route('/api/knowledge_base/chat', methods=['POST'])
def knowledge_base_chat():
    """
    使用大模型结合知识库回答用户问题
    请求参数:
    - message: 用户消息
    - history: 历史对话记录 (可选)
    - search_type: 搜索类型，可选 'semantic'(默认) 或 'keyword'
    - top_k: 检索的相关文档数量 (默认5)
    - max_tokens: 响应的最大token数 (默认1000)
    """
    try:
        # 获取并验证请求参数
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'message': '缺少必要的参数: message'}), 400
        
        message = data.get('message').strip()
        history = data.get('history', [])
        search_type = data.get('search_type', 'semantic')  # 仍然保留这个参数，但不传给search_knowledge_base
        top_k = int(data.get('top_k', 5))
        max_tokens = int(data.get('max_tokens', 1000))
        
        # 记录日志
        logger.info(f"知识库聊天请求: message={message}, search_type={search_type}, top_k={top_k}")
        
        if not message:
            return jsonify({'success': False, 'message': '消息不能为空'}), 400
        
        # 在知识库中搜索相关内容 - 移除search_type参数
        search_results = search_knowledge_base(message, limit=top_k)
        
        # 构建上下文信息
        context_docs = []
        sources = []
        
        for result in search_results:
            content = result.get('content', '')
            title = result.get('title', '')
            item_id = result.get('item_id', '')
            source_type = result.get('source_type', '')
            
            # 添加到上下文
            context_docs.append(content)
            
            # 准备来源信息
            source_info = {
                'id': item_id,
                'title': title,
                'source_type': source_type,
                'text': content[:200] + ('...' if len(content) > 200 else '')  # 限制长度
            }
            sources.append(source_info)
        
        # 构建提示
        context_text = "\n\n".join(context_docs)
        system_prompt = f"""你是一个专业的审计和法律助手，基于给定的知识库内容回答用户问题。
遵循以下规则：
1. 只基于提供的知识库内容回答问题，不要编造信息
2. 如果知识库内容不足以回答问题，坦诚告知用户
3. 回答要详细且结构化，使用markdown格式，可用适当的加粗和列表增强可读性
4. 专业地解释审计和法律术语，但要保持通俗易懂
5. 如有必要，引用具体的法规条款或审计标准
6. 回答必须使用中文，即使用户用英文提问，也请用中文回答

在知识库中找到的内容如下：
{context_text}

如果知识库中没有足够的信息，请明确告知用户"根据当前知识库内容，无法完整回答您的问题"，并建议用户如何调整问题或提供更多信息。"""
        
        # 准备对话历史
        chat_messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（除系统消息外）
        if history and len(history) > 0:
            # 跳过第一条系统消息，因为我们已经添加了自定义的系统消息
            user_assistant_messages = []
            for msg in history[1:] if history[0].get('role') == 'system' else history:
                role = msg.get('role')
                content = msg.get('content')
                
                # 只添加user和assistant角色的消息
                if role in ['user', 'assistant'] and content:
                    user_assistant_messages.append({"role": role, "content": content})
            
            # 限制历史消息数量，保留最近的消息
            MAX_HISTORY_MESSAGES = 10  # 最多保留10轮对话
            if len(user_assistant_messages) > MAX_HISTORY_MESSAGES:
                # 保留最近的消息
                app_logger.info(f"历史消息过多，裁剪为最近的{MAX_HISTORY_MESSAGES}条")
                user_assistant_messages = user_assistant_messages[-MAX_HISTORY_MESSAGES:]
            
            # 将保留的消息添加到chat_messages
            chat_messages.extend(user_assistant_messages)
        
        # 添加当前用户消息
        # 如果历史中已包含当前消息则不重复添加
        if not history or history[-1].get('content') != message:
            chat_messages.append({"role": "user", "content": message})
        
        # 调用模型生成回复
        try:
            # 获取默认模型信息
            default_model_info = modelConfigUtil.get_default_model_info()
            if not default_model_info:
                app_logger.error("没有找到默认模型配置")
                return jsonify({
                    'success': False,
                    'message': '没有找到默认模型配置，请先设置默认模型'
                }), 500
            
            # 获取模型服务提供商ID和模型ID
            provider_id = default_model_info.get('provider_id')
            model_id = default_model_info.get('model_id')
            
            # 获取模型名称，可能在model_details中
            if 'model_details' in default_model_info and default_model_info['model_details']:
                model_name = default_model_info['model_details'].get('name', '').lower()
            else:
                model_name = ''
            
            app_logger.info(f"使用默认模型回答知识库问题: 提供商 {provider_id}, 模型 {model_id}")
            
            # 判断是否为Qwen3模型，如果是则调整参数
            options = {
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": max_tokens
            }
            
            # 判断是否为Qwen3模型，如果是则添加/no_think指令
            if 'qwen3' in model_id.lower() or 'qwen3' in model_name:
                app_logger.info("检测到Qwen3模型，添加/no_think指令")
                # 修改最后一条用户消息
                if chat_messages[-1]['role'] == 'user':
                    chat_messages[-1]['content'] += " /no_think"
            
            # 调用模型生成回复
            response = model_chat_service.chat_completion(
                provider_id,
                model_id,
                chat_messages,
                options
            )
            
            # 检查是否有错误
            if "error" in response:
                app_logger.error(f"模型回答问题失败: {response.get('error')}")
                return jsonify({
                    'success': False,
                    'message': f'调用模型服务失败: {response.get("error")}'
                }), 500
            
            # 获取模型回复
            reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not reply:
                return jsonify({
                    'success': False, 
                    'message': '模型未返回有效回复'
                }), 500
            
            # 返回成功响应
            return jsonify({
                'success': True,
                'data': {
                    'reply': reply,
                    'sources': sources
                }
            })
            
        except Exception as e:
            logger.error(f"调用模型服务失败: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'message': f'调用模型服务失败: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"知识库聊天处理异常: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}'
        }), 500

@knowledge_base_api.route('/api/knowledge_base/check_model', methods=['GET'])
def check_model_status():
    """检查模型状态，返回可用的提供商和模型列表
    
    Returns:
        JSON: 包含所有提供商和模型状态的JSON对象
    """
    try:
        # model_service 已在文件顶部导入，不需要再导入
        
        # 替换为modelConfigUtil.get_all_providers()
        providers = modelConfigUtil.get_all_providers()
        result = {}
        
        # 遍历提供商检查状态
        for provider_id, provider in providers.items():
            provider_status = {
                'name': provider.get('name', provider_id),
                'available': False,
                'models': []
            }
            
            try:
                # 获取该提供商的所有模型（改用modelConfigUtil）
                models = modelConfigUtil.get_provider_models(provider_id)
                
                if models and len(models) > 0:
                    provider_status['available'] = True
                    provider_status['models'] = []
                    
                    for model in models:
                        model_id = model.get('id')
                        provider_status['models'].append({
                            'id': model_id,
                            'name': model.get('name', model_id)
                        })
            except Exception as e:
                logger.error(f"检查提供商 {provider_id} 状态失败: {str(e)}")
            
            result[provider_id] = provider_status
        
        # 返回所有提供商和模型状态
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"检查模型状态异常: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'检查模型状态时发生错误: {str(e)}'
        }), 500 