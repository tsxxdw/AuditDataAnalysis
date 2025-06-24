"""
用户管理API路由

提供用户管理相关的API，包括用户添加、权限设置等
"""

from flask import Blueprint, request, jsonify, session
from utils.user_util import user_util
from service.log.logger import app_logger

# 创建用户管理API蓝图
user_management_api = Blueprint('user_management_api', __name__, url_prefix='/api/user')

@user_management_api.route('/list', methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        users_data = user_util.load_users()
        # 移除密码信息
        for user in users_data['users']:
            if 'password' in user:
                del user['password']
        
        return jsonify({
            'code': 200,
            'message': '获取用户列表成功',
            'data': users_data['users']
        })
    except Exception as e:
        app_logger.error(f"获取用户列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取用户列表失败: {str(e)}',
            'data': None
        })

@user_management_api.route('/add', methods=['POST'])
def add_user():
    """添加用户"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not all([username, password, role]):
            return jsonify({
                'code': 400,
                'message': '参数不完整',
                'data': None
            })
        
        success, message = user_util.add_user(username, password, role)
        
        if success:
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            return jsonify({
                'code': 400,
                'message': message,
                'data': None
            })
    except Exception as e:
        app_logger.error(f"添加用户失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加用户失败: {str(e)}',
            'data': None
        })

@user_management_api.route('/delete', methods=['POST'])
def delete_user():
    """删除用户"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({
                'code': 400,
                'message': '参数不完整',
                'data': None
            })
        
        success, message = user_util.delete_user(username)
        
        if success:
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            return jsonify({
                'code': 400,
                'message': message,
                'data': None
            })
    except Exception as e:
        app_logger.error(f"删除用户失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除用户失败: {str(e)}',
            'data': None
        })

@user_management_api.route('/update_permissions', methods=['POST'])
def update_permissions():
    """更新用户权限"""
    try:
        data = request.get_json()
        username = data.get('username')
        permissions = data.get('permissions', [])
        
        if not username:
            return jsonify({
                'code': 400,
                'message': '参数不完整',
                'data': None
            })
        
        success, message = user_util.update_user_permissions(username, permissions)
        
        if success:
            return jsonify({
                'code': 200,
                'message': message,
                'data': None
            })
        else:
            return jsonify({
                'code': 400,
                'message': message,
                'data': None
            })
    except Exception as e:
        app_logger.error(f"更新用户权限失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新用户权限失败: {str(e)}',
            'data': None
        })

@user_management_api.route('/available_pages', methods=['GET'])
def available_pages():
    """获取系统中所有可用页面"""
    try:
        pages = user_util.get_available_pages()
        
        return jsonify({
            'code': 200,
            'message': '获取页面列表成功',
            'data': pages
        })
    except Exception as e:
        app_logger.error(f"获取页面列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取页面列表失败: {str(e)}',
            'data': None
        }) 