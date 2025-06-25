"""
登录API路由

提供登录、退出登录等用户认证相关功能
"""

from flask import Blueprint, request, jsonify, session
import os

from service.log.logger import app_logger
from utils.user_util import UserUtil
from utils.index_util import IndexUtil

# 创建登录API蓝图
login_api = Blueprint('login_api', __name__, url_prefix='/api')

@login_api.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空',
                'data': None
            })
        
        success, result = UserUtil.verify_user(username, password)
        
        if success:
            # 获取权限对应的标题
            permission_titles = {}
            json_file_path = os.path.join('config', 'index.json')
            json_read_success, index_data = IndexUtil.read_json_file(json_file_path)
            
            if json_read_success:
                # 创建URL到title的映射
                for item in index_data:
                    if 'url' in item and 'title' in item:
                        permission_titles[item['url']] = item['title']
            
            # 登录成功，将用户信息存入session
            user_info = {
                'username': result['username'],
                'role': result['role'],
                'permissions': result.get('permissions', []),
                'permission_titles': permission_titles  # 添加权限标题映射
            }
            session['user_info'] = user_info
            
            app_logger.info(f"用户 {username} 登录成功")
            
            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': user_info
            })
        else:
            app_logger.warning(f"用户 {username} 登录失败: {result}")
            
            return jsonify({
                'code': 401,
                'message': result,
                'data': None
            })
    except Exception as e:
        app_logger.error(f"登录异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

@login_api.route('/login/logout', methods=['POST'])
def logout():
    """用户退出登录"""
    try:
        # 清除session中的用户信息
        if 'user_info' in session:
            username = session['user_info'].get('username')
            session.pop('user_info', None)
            app_logger.info(f"用户 {username} 退出登录")
        
        return jsonify({
            'code': 200,
            'message': '退出成功',
            'data': None
        })
    except Exception as e:
        app_logger.error(f"退出登录异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }) 