"""
AI聊天API路由

提供AI聊天相关的API接口
"""

from flask import Blueprint, jsonify, request, session
from service.log.logger import app_logger
from service.session_service import session_service

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