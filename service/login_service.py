"""
登录服务模块

提供登录、权限验证等核心业务逻辑
"""

import os
from flask import session

from service.log.logger import app_logger
from utils.user_util import UserUtil
from utils.index_util import IndexUtil

class LoginService:
    def verify_user(self, username, password):
        try:
            if not all([username, password]):
                return False, {
                    'code': 400,
                    'message': '用户名和密码不能为空',
                    'data': None
                }
            success, result = UserUtil.verify_user(username, password)
            
            if success:
                return True, result
            else:
                app_logger.warning(f"用户 {username} 登录失败: {result}")
                return False, {
                    'code': 401,
                    'message': result,
                    'data': None
                }
        except Exception as e:
            app_logger.error(f"用户验证异常: {str(e)}")
            return False, {
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }
    
    def authorize_user(self, user_data):
        """
        用户授权，设置session和权限
        
        Args:
            user_data: 用户数据
            
        Returns:
            tuple: (成功状态, 结果数据或错误信息)
        """
        try:
            # 获取权限对应的标题
            permission_titles = self.get_permission_titles()
            
            # 登录成功，将用户信息存入session
            user_info = {
                'username': user_data['username'],
                'role': user_data['role'],
                'permissions': user_data.get('permissions', []),
                'permission_titles': permission_titles  # 添加权限标题映射
            }
            session['user_info'] = user_info
            
            app_logger.info(f"用户 {user_data['username']} 登录成功")
            
            return True, {
                'code': 200,
                'message': '登录成功',
                'data': user_info
            }
        except Exception as e:
            app_logger.error(f"用户授权异常: {str(e)}")
            return False, {
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }
    
    def get_permission_titles(self):
        """
        获取权限对应的标题
        
        Returns:
            dict: 权限URL到标题的映射
        """
        permission_titles = {}
        json_file_path = os.path.join('config', 'index.json')
        json_read_success, index_data = IndexUtil.read_json_file(json_file_path)
        
        if json_read_success:
            # 创建URL到title的映射
            for item in index_data:
                if 'url' in item and 'title' in item:
                    permission_titles[item['url']] = item['title']
        
        return permission_titles
    
    def logout(self):
        """
        用户退出登录
        
        Returns:
            tuple: (成功状态, 结果数据或错误信息)
        """
        try:
            # 清除session中的用户信息
            username = None
            if 'user_info' in session:
                username = session['user_info'].get('username')
                session.pop('user_info', None)
                app_logger.info(f"用户 {username} 退出登录")
            
            return True, {
                'code': 200,
                'message': '退出成功',
                'data': None
            }
        except Exception as e:
            app_logger.error(f"退出登录异常: {str(e)}")
            return False, {
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            } 