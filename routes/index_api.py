"""
首页API路由

提供首页导航按钮等功能
"""

import os
from flask import Blueprint, jsonify, session

from service.log.logger import app_logger
from utils.index_util import IndexUtil

# 创建首页API蓝图
index_api = Blueprint('index_api', __name__, url_prefix='/api')

@index_api.route('/get_navigation_buttons', methods=['GET'])
def get_navigation_buttons():
    """获取导航按钮列表（根据用户权限过滤）"""
    try:
        # 获取当前用户信息
        user_info = session.get('user_info', {})
        user_role = user_info.get('role', '')
        user_permissions = user_info.get('permissions', [])
        
        # 读取导航按钮配置
        json_file_path = os.path.join('config', 'index.json')
        success, data = IndexUtil.read_json_file(json_file_path)
        
        if not success:
            app_logger.error(f"读取导航按钮配置失败: {data}")
            return jsonify({
                'code': 500,
                'message': f"读取导航按钮配置失败: {data}",
                'data': None
            })
        
        # 过滤按钮数据
        filtered_buttons = []
        
        # 如果是管理员，显示所有按钮
        if user_role == "管理员":
            filtered_buttons = [item for item in data if item.get('position') == 'index']
        else:
            # 根据用户权限过滤
            for item in data:
                # 只处理首页位置的按钮
                if item.get('position') != 'index':
                    continue
                    
                button_url = item.get('url', '')
                # 如果该按钮对应的页面在用户权限列表中，则显示
                if button_url in user_permissions or not button_url:
                    filtered_buttons.append(item)
        
        app_logger.info(f"用户 {user_info.get('username', '未登录')} 获取导航按钮, 共 {len(filtered_buttons)} 个")
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': filtered_buttons
        })
    except Exception as e:
        app_logger.error(f"获取导航按钮异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }) 