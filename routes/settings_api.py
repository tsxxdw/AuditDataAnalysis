"""
系统设置API路由

提供系统设置相关的API，包括菜单配置等
"""

from flask import Blueprint, jsonify, session, current_app
import os
from service.log.logger import app_logger
from utils.index_util import IndexUtil
from service.auth.auth_middleware import has_permission
from service.session_service import session_service

# 创建系统设置API蓝图
settings_api = Blueprint('settings_api', __name__, url_prefix='/api/settings')

@settings_api.route('/menu_config', methods=['GET'])
def get_menu_config():
    """获取设置菜单配置"""
    try:
        # 获取活动标签页，如果没有则默认为个人设置
        active_tab = session_service.get('active_settings_tab', 'personal-settings')
        
        # 获取用户信息
        user_info = session_service.get_user_info()
        user_role = user_info.get('role', '')
        user_permissions = user_info.get('permissions', [])
        
        # 获取配置文件路径
        config_file = os.path.join(current_app.root_path, 'config', 'index.json')
        
        # 读取配置文件
        success, data = IndexUtil.read_json_file(config_file)
        
        if not success:
            app_logger.error(f"读取菜单配置失败: {data}")
            return jsonify({
                'code': 500,
                'message': f'读取菜单配置失败: {data}',
                'data': None
            })
        
        # 从配置文件中筛选出设置页面的菜单项
        menu_items = [item for item in data if item.get('position') == 'settings' and item.get('id') is not None]
        
        # 根据用户权限过滤菜单项
        if user_role == '管理员':
            # 管理员可以看到所有菜单项
            filtered_menu_items = menu_items
        else:
            # 普通用户只能看到有权限的菜单项
            filtered_menu_items = []
            for item in menu_items:
                # 检查用户是否有权限访问该设置页面
                url = item.get('url', '')
                if url and (url in user_permissions or has_permission(url)):
                    filtered_menu_items.append(item)
        
        # 设置活动状态
        for item in filtered_menu_items:
            item['active'] = item.get('id') == active_tab
        
        return jsonify({
            'code': 200,
            'message': '获取菜单配置成功',
            'data': filtered_menu_items
        })
    except Exception as e:
        app_logger.error(f"获取菜单配置异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        })

@settings_api.route('/set_active_tab', methods=['POST'])
def set_active_tab():
    """设置活动标签页"""
    from flask import request
    try:
        data = request.get_json()
        tab_id = data.get('tab_id')
        
        if not tab_id:
            return jsonify({
                'code': 400,
                'message': '参数不完整',
                'data': None
            })
        
        # 保存活动标签页到会话
        session_service.set('active_settings_tab', tab_id)
        
        return jsonify({
            'code': 200,
            'message': '设置活动标签页成功',
            'data': None
        })
    except Exception as e:
        app_logger.error(f"设置活动标签页异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }) 