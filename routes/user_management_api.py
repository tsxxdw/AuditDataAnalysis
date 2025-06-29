"""
用户管理API路由

提供用户管理相关的API，包括用户添加、权限设置等
"""

from flask import Blueprint, request, jsonify, session

import os
from service.log.logger import app_logger
from utils.user_util import UserUtil
from utils.index_util import IndexUtil
from service.session_service import session_service

# 创建用户管理API蓝图
user_management_api = Blueprint('user_management_api', __name__, url_prefix='/api/user')

@user_management_api.route('/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    try:
        user_info = session_service.get_user_info()
        
        if user_info:
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': user_info
            })
        else:
            return jsonify({
                'code': 401,
                'message': '用户未登录',
                'data': None
            })
    except Exception as e:
        app_logger.error(f"获取当前用户信息异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

@user_management_api.route('/list', methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        users_data = UserUtil.load_users()
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
        
        success, message = UserUtil.add_user(username, password, role)
        
        if success:
            # 获取当前登录用户名
            current_user_info = session_service.get_user_info()
            current_username = current_user_info.get('username', 'system')
            
            # 创建用户配置文件夹
            try:
                # 检查configuration_data文件夹是否存在，不存在则创建
                if not os.path.exists('configuration_data'):
                    os.makedirs('configuration_data')
                
                # 创建用户专属文件夹
                user_config_dir = os.path.join('configuration_data', username)
                if not os.path.exists(user_config_dir):
                    os.makedirs(user_config_dir)
                
                # 复制默认配置文件夹内容到新用户文件夹
                default_config_dir = os.path.join('configuration_data', 'default')
                if os.path.exists(default_config_dir):
                    from distutils.dir_util import copy_tree
                    copy_tree(default_config_dir, user_config_dir)
                    app_logger.info(f"已为用户 {username} 创建配置文件夹并复制默认配置 (操作者: {current_username})")
            except Exception as e:
                app_logger.error(f"创建用户配置文件夹失败: {str(e)}")
                # 配置文件夹创建失败不影响用户创建的结果
            
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
        
        success, message = UserUtil.delete_user(username)
        
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
        
        success, message = UserUtil.update_user_permissions(username, permissions)
        
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
        # 直接从index.json文件读取可用页面
        json_file_path = os.path.join('config', 'index.json')
        success, data = IndexUtil.read_json_file(json_file_path)
        
        if not success:
            app_logger.error(f"读取导航按钮配置失败: {data}")
            return jsonify({
                'code': 500,
                'message': f"读取导航按钮配置失败: {data}",
                'data': None
            })
        
        # 转换为权限设置需要的格式
        pages = []
        for item in data:
            if 'title' in item and 'url' in item:
                pages.append({
                    'path': item['url'],
                    'name': item['title']
                })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': pages
        })
    except Exception as e:
        app_logger.error(f"获取可用页面失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取可用页面失败: {str(e)}',
            'data': None
        }) 