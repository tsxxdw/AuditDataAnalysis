"""
会话服务模块

提供统一的会话（session）管理功能，包括会话数据的存取、清除等操作。
用于集中管理应用程序中的会话数据，避免直接操作 Flask session 对象。
"""

from flask import session
from service.log.logger import app_logger


class SessionService:
    """
    会话服务类，提供统一的会话管理功能。
    所有与 session 相关的操作都应通过该类进行，而非直接操作 Flask 的 session 对象。
    """
    
    def set(self, key, value):
        """
        设置会话数据
        
        Args:
            key (str): 会话键名
            value (any): 会话数据值
            
        Returns:
            bool: 操作是否成功
        """
        try:
            session[key] = value
            return True
        except Exception as e:
            app_logger.error(f"设置会话数据失败: {key}, 错误: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """
        获取会话数据
        
        Args:
            key (str): 会话键名
            default: 未找到时返回的默认值
            
        Returns:
            any: 会话数据值或默认值
        """
        try:
            return session.get(key, default)
        except Exception as e:
            app_logger.error(f"获取会话数据失败: {key}, 错误: {str(e)}")
            return default
    
    def pop(self, key, default=None):
        """
        获取并删除会话数据
        
        Args:
            key (str): 会话键名
            default: 未找到时返回的默认值
            
        Returns:
            any: 会话数据值或默认值
        """
        try:
            return session.pop(key, default)
        except Exception as e:
            app_logger.error(f"删除会话数据失败: {key}, 错误: {str(e)}")
            return default
    
    def delete(self, key):
        """
        删除会话数据
        
        Args:
            key (str): 会话键名
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if key in session:
                session.pop(key)
            return True
        except Exception as e:
            app_logger.error(f"删除会话数据失败: {key}, 错误: {str(e)}")
            return False
    
    def clear(self):
        """
        清除所有会话数据
        
        Returns:
            bool: 操作是否成功
        """
        try:
            session.clear()
            return True
        except Exception as e:
            app_logger.error(f"清除会话数据失败: 错误: {str(e)}")
            return False
    
    def has_key(self, key):
        """
        检查会话是否包含指定键名
        
        Args:
            key (str): 会话键名
            
        Returns:
            bool: 是否存在该键名
        """
        return key in session
    
    # 用户相关的会话方法
    def get_user_info(self):
        """
        获取当前登录用户信息
        
        Returns:
            dict: 用户信息字典，未登录时为空字典
        """
        return self.get('user_info', {})
    
    def is_logged_in(self):
        """
        检查用户是否已登录
        
        Returns:
            bool: 是否已登录
        """
        return 'user_info' in session and session['user_info'] is not None
    
    def get_permissions(self):
        """
        获取当前用户权限列表
        
        Returns:
            list: 权限列表，未登录时为空列表
        """
        user_info = self.get_user_info()
        return user_info.get('permissions', [])
    
    def is_admin(self):
        """
        检查当前用户是否为管理员
        
        Returns:
            bool: 是否为管理员
        """
        user_info = self.get_user_info()
        return user_info.get('role') == '管理员'

# 创建单例实例，方便导入使用
session_service = SessionService()
print("session_service 生成了")
