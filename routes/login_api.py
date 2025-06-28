"""
登录API路由

提供登录、退出登录等用户认证相关功能
"""

from flask import Blueprint, request, jsonify
from service import login_service  # 导入全局服务实例

# 创建登录API蓝图
login_api = Blueprint('login_api', __name__, url_prefix='/api')

@login_api.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 步骤1: 验证用户
        verify_success, verify_result = login_service.verify_user(username, password)
        
        if not verify_success:
            return jsonify(verify_result)
        
        # 步骤2: 授权用户
        auth_success, auth_result = login_service.authorize_user(verify_result)
        
        return jsonify(auth_result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

@login_api.route('/login/logout', methods=['POST'])
def logout():
    """用户退出登录"""
    try:
        # 调用登出服务
        success, result = login_service.logout()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }) 