"""
AI聊天API路由

提供AI聊天相关的API接口
"""

from flask import Blueprint, jsonify, request, session
from service.log.logger import app_logger
from service.session_service import session_service
from chatai_config_util import ChatAIConfigUtil
import os
import uuid

# 创建AI聊天API蓝图
ai_chat_api = Blueprint('ai_chat_api', __name__, url_prefix='/api/ai_chat')

@ai_chat_api.route('/send_message', methods=['POST'])
def send_message():
    """发送消息到AI并获取回复"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        # 获取前端发送的消息
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            app_logger.warning(f"用户 {username} 发送了空消息")
            return jsonify({
                'code': 400,
                'message': '消息内容不能为空',
                'data': None
            })
        
        app_logger.info(f"用户 {username} 发送消息: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # 这里暂时返回固定回复，实际实现时会调用AI模型服务
        reply = f"您发送的消息是：{message}\n\n这只是一个示例回复，实际AI功能尚未实现。"
        
        return jsonify({
            'code': 200,
            'message': '成功',
            'data': {
                'reply': reply
            }
        })
    except Exception as e:
        app_logger.error(f"处理AI聊天消息异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

# ============= 工作区管理API =============

@ai_chat_api.route('/workspaces', methods=['GET'])
def get_workspaces():
    """获取所有工作区"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 获取工作区列表")
        
        workspaces = ChatAIConfigUtil.get_all_workspaces()
        return jsonify({
            "code": 200,
            "message": "获取工作区成功",
            "data": {
                "workspaces": workspaces
            }
        })
    except Exception as e:
        app_logger.error(f"获取工作区列表异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取工作区失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces', methods=['POST'])
def create_workspace():
    """创建新工作区"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'name' not in data:
            app_logger.warning(f"用户 {username} 创建工作区时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        workspace_name = data['name']
        app_logger.info(f"用户 {username} 创建工作区: {workspace_name}")
        
        workspace = ChatAIConfigUtil.create_workspace(workspace_name)
        
        return jsonify({
            "code": 200,
            "message": "创建工作区成功",
            "data": {
                "workspace": workspace
            }
        })
    except Exception as e:
        app_logger.error(f"创建工作区异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"创建工作区失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """获取指定工作区信息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 获取工作区信息: {workspace_id}")
        
        workspace = ChatAIConfigUtil.get_workspace(workspace_id)
        
        if not workspace:
            app_logger.warning(f"用户 {username} 尝试获取不存在的工作区: {workspace_id}")
            return jsonify({
                "code": 404,
                "message": "工作区不存在"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "获取工作区成功",
            "data": {
                "workspace": workspace
            }
        })
    except Exception as e:
        app_logger.error(f"获取工作区信息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取工作区失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    """更新工作区信息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'name' not in data:
            app_logger.warning(f"用户 {username} 更新工作区时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        new_name = data['name']
        app_logger.info(f"用户 {username} 重命名工作区 {workspace_id} 为: {new_name}")
        
        success = ChatAIConfigUtil.rename_workspace(workspace_id, new_name)
        
        if not success:
            app_logger.warning(f"用户 {username} 尝试重命名不存在的工作区: {workspace_id}")
            return jsonify({
                "code": 404,
                "message": "工作区不存在或更新失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "更新工作区成功"
        })
    except Exception as e:
        app_logger.error(f"更新工作区信息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新工作区失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """删除工作区"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 删除工作区: {workspace_id}")
        
        success = ChatAIConfigUtil.delete_workspace(workspace_id)
        
        if not success:
            app_logger.warning(f"用户 {username} 尝试删除不存在的工作区: {workspace_id}")
            return jsonify({
                "code": 404,
                "message": "工作区不存在或删除失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "删除工作区成功"
        })
    except Exception as e:
        app_logger.error(f"删除工作区异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除工作区失败: {str(e)}"
        }), 500

# ============= 会话管理API =============

@ai_chat_api.route('/workspaces/<workspace_id>/sessions', methods=['GET'])
def get_sessions(workspace_id):
    """获取工作区下的所有会话"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 获取工作区 {workspace_id} 的会话列表")
        
        sessions = ChatAIConfigUtil.get_sessions(workspace_id)
        
        return jsonify({
            "code": 200,
            "message": "获取会话列表成功",
            "data": {
                "sessions": sessions
            }
        })
    except Exception as e:
        app_logger.error(f"获取会话列表异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取会话列表失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>/sessions', methods=['POST'])
def create_session(workspace_id):
    """在工作区下创建新会话"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'name' not in data:
            app_logger.warning(f"用户 {username} 创建会话时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        session_name = data['name']
        app_logger.info(f"用户 {username} 在工作区 {workspace_id} 下创建会话: {session_name}")
        
        session = ChatAIConfigUtil.create_session(workspace_id, session_name)
        
        if not session:
            app_logger.warning(f"用户 {username} 尝试在不存在的工作区 {workspace_id} 下创建会话")
            return jsonify({
                "code": 404,
                "message": "工作区不存在或创建会话失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "创建会话成功",
            "data": {
                "session": session
            }
        })
    except Exception as e:
        app_logger.error(f"创建会话异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"创建会话失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>/sessions/<session_id>', methods=['GET'])
def get_session(workspace_id, session_id):
    """获取指定会话信息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 获取会话信息: {workspace_id}/{session_id}")
        
        session = ChatAIConfigUtil.get_session(workspace_id, session_id)
        
        if not session:
            app_logger.warning(f"用户 {username} 尝试获取不存在的会话: {workspace_id}/{session_id}")
            return jsonify({
                "code": 404,
                "message": "会话不存在"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "获取会话成功",
            "data": {
                "session": session
            }
        })
    except Exception as e:
        app_logger.error(f"获取会话信息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取会话失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>/sessions/<session_id>', methods=['PUT'])
def update_session(workspace_id, session_id):
    """更新会话信息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'name' not in data:
            app_logger.warning(f"用户 {username} 更新会话时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        new_name = data['name']
        app_logger.info(f"用户 {username} 重命名会话 {workspace_id}/{session_id} 为: {new_name}")
        
        success = ChatAIConfigUtil.rename_session(workspace_id, session_id, new_name)
        
        if not success:
            app_logger.warning(f"用户 {username} 尝试重命名不存在的会话: {workspace_id}/{session_id}")
            return jsonify({
                "code": 404,
                "message": "会话不存在或更新失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "更新会话成功"
        })
    except Exception as e:
        app_logger.error(f"更新会话信息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新会话失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>/sessions/<session_id>', methods=['DELETE'])
def delete_session(workspace_id, session_id):
    """删除会话"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 删除会话: {workspace_id}/{session_id}")
        
        success = ChatAIConfigUtil.delete_session(workspace_id, session_id)
        
        if not success:
            app_logger.warning(f"用户 {username} 尝试删除不存在的会话: {workspace_id}/{session_id}")
            return jsonify({
                "code": 404,
                "message": "会话不存在或删除失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "删除会话成功"
        })
    except Exception as e:
        app_logger.error(f"删除会话异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除会话失败: {str(e)}"
        }), 500

# ============= 消息管理API =============

@ai_chat_api.route('/workspaces/<workspace_id>/sessions/<session_id>/messages', methods=['GET'])
def get_messages(workspace_id, session_id):
    """获取会话中的消息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        app_logger.info(f"用户 {username} 获取会话消息: {workspace_id}/{session_id}")
        
        session = ChatAIConfigUtil.get_session(workspace_id, session_id)
        
        if not session:
            app_logger.warning(f"用户 {username} 尝试获取不存在会话的消息: {workspace_id}/{session_id}")
            return jsonify({
                "code": 404,
                "message": "会话不存在"
            }), 404
        
        # 读取会话文件内容并解析消息
        file_path = session.get("file_path")
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                "code": 200,
                "message": "获取消息成功",
                "data": {
                    "messages": []
                }
            })
        
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单解析会话文件中的消息
            # 跳过前两行（会话标题和创建时间）
            message_blocks = content.split("\n\n")[1:]
            
            for block in message_blocks:
                if not block.strip():
                    continue
                
                lines = block.strip().split("\n")
                if len(lines) >= 2:
                    header = lines[0]
                    if "[" in header and "]" in header:
                        timestamp = header.split("]")[0].strip("[")
                        sender = "user" if "用户" in header else "ai"
                        content = "\n".join(lines[1:])
                        
                        messages.append({
                            "id": str(uuid.uuid4()),
                            "sender": sender,
                            "content": content,
                            "timestamp": timestamp
                        })
        except Exception as e:
            app_logger.error(f"解析会话消息失败: {str(e)}")
        
        return jsonify({
            "code": 200,
            "message": "获取消息成功",
            "data": {
                "messages": messages
            }
        })
    except Exception as e:
        app_logger.error(f"获取会话消息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取消息失败: {str(e)}"
        }), 500

@ai_chat_api.route('/workspaces/<workspace_id>/sessions/<session_id>/messages', methods=['POST'])
def create_message(workspace_id, session_id):
    """在会话中创建新消息"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'content' not in data or 'sender' not in data:
            app_logger.warning(f"用户 {username} 创建消息时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        content = data['content']
        sender = data['sender']
        
        if sender not in ["user", "ai"]:
            app_logger.warning(f"用户 {username} 创建消息时发送者类型无效: {sender}")
            return jsonify({
                "code": 400,
                "message": "发送者类型无效"
            }), 400
        
        app_logger.info(f"用户 {username} 在会话 {workspace_id}/{session_id} 中创建 {sender} 消息")
        
        success = ChatAIConfigUtil.save_message_to_session(workspace_id, session_id, sender, content)
        
        if not success:
            app_logger.warning(f"用户 {username} 尝试在不存在的会话中创建消息: {workspace_id}/{session_id}")
            return jsonify({
                "code": 404,
                "message": "会话不存在或保存消息失败"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "保存消息成功"
        })
    except Exception as e:
        app_logger.error(f"保存消息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"保存消息失败: {str(e)}"
        }), 500

# ============= 文件上传API =============

@ai_chat_api.route('/upload_file', methods=['POST'])
def upload_file():
    """上传文件到工作区"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        if 'file' not in request.files:
            app_logger.warning(f"用户 {username} 上传文件时没有提供文件")
            return jsonify({
                "code": 400,
                "message": "没有文件上传"
            }), 400
        
        file = request.files['file']
        workspace_id = request.form.get('workspace_id')
        
        if not file or not workspace_id:
            app_logger.warning(f"用户 {username} 上传文件时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        app_logger.info(f"用户 {username} 上传文件 {file.filename} 到工作区 {workspace_id}")
        
        # 检查工作区是否存在
        workspace = ChatAIConfigUtil.get_workspace(workspace_id)
        if not workspace:
            app_logger.warning(f"用户 {username} 尝试上传文件到不存在的工作区: {workspace_id}")
            return jsonify({
                "code": 404,
                "message": "工作区不存在"
            }), 404
        
        # 保存文件到工作区目录
        workspace_dir = os.path.join(ChatAIConfigUtil.WORKSPACE_DIR_PATH, workspace_id)
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir, exist_ok=True)
        
        file_path = os.path.join(workspace_dir, file.filename)
        file.save(file_path)
        
        app_logger.info(f"用户 {username} 文件上传成功: {file_path}")
        
        return jsonify({
            "code": 200,
            "message": "文件上传成功",
            "data": {
                "file_path": file_path
            }
        })
    except Exception as e:
        app_logger.error(f"文件上传异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"文件上传失败: {str(e)}"
        }), 500

# ============= AI回复API =============

@ai_chat_api.route('/get_ai_reply', methods=['POST'])
def get_ai_reply():
    """获取AI回复"""
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username', '未登录用户')
        
        data = request.json
        if not data or 'message' not in data or 'workspace_id' not in data or 'session_id' not in data:
            app_logger.warning(f"用户 {username} 获取AI回复时缺少必要参数")
            return jsonify({
                "code": 400,
                "message": "缺少必要参数"
            }), 400
        
        user_message = data['message']
        workspace_id = data['workspace_id']
        session_id = data['session_id']
        
        app_logger.info(f"用户 {username} 在会话 {workspace_id}/{session_id} 中请求AI回复")
        
        # 这里应该调用AI模型获取回复
        # 简单模拟AI回复
        ai_reply = f"我收到了您的消息: {user_message}\n\n这是一个模拟的AI回复。在实际应用中，这里应该调用真实的AI模型来生成回复。"
        
        app_logger.info(f"AI回复生成成功，返回给用户 {username}")
        
        return jsonify({
            "code": 200,
            "message": "获取AI回复成功",
            "data": {
                "reply": ai_reply
            }
        })
    except Exception as e:
        app_logger.error(f"获取AI回复异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取AI回复失败: {str(e)}"
        }), 500 