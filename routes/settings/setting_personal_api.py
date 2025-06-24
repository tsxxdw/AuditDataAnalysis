"""
个人设置API路由

提供个人设置相关的API，包括账号信息查询、密码修改等
"""

from flask import Blueprint, request, jsonify, session
from utils.user_util import user_util
from service.log.logger import app_logger

# 创建个人设置API蓝图
setting_personal_api = Blueprint('setting_personal_api', __name__, url_prefix='/api/settings/personal')

@setting_personal_api.route('/info', methods=['GET'])
def get_personal_info():
    """获取当前登录用户的个人信息"""
    try:
        # 获取当前登录用户
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({
                'code': 401,
                'message': '用户未登录',
                'data': None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user_info
        })
    except Exception as e:
        app_logger.error(f"获取个人信息异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

@setting_personal_api.route('/change_password', methods=['POST'])
def change_password():
    """修改用户密码"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not all([current_password, new_password]):
            return jsonify({
                'code': 400,
                'message': '参数不完整',
                'data': None
            })
        
        # 获取当前登录用户
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({
                'code': 401,
                'message': '用户未登录',
                'data': None
            })
        
        username = user_info.get('username')
        
        # 修改密码
        success, message = user_util.change_password(username, current_password, new_password)
        
        if success:
            app_logger.info(f"用户 {username} 密码修改成功")
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            app_logger.warning(f"用户 {username} 密码修改失败: {message}")
            return jsonify({
                'code': 400,
                'message': message,
                'data': None
            })
    except Exception as e:
        app_logger.error(f"修改密码异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }) 