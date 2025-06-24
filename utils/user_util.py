"""
用户管理工具类

提供用户管理相关功能，包括用户添加、身份验证、权限管理等
"""

import json
import os
import hashlib
from flask import current_app
import glob

class UserUtil:
    def __init__(self):
        self.users_file = os.path.join('config', 'users.json')
        
    def load_users(self):
        """加载所有用户信息"""
        if not os.path.exists(self.users_file):
            # 如果文件不存在，创建默认文件
            default_users = {
                "users": [
                    {
                        "username": "admin",
                        "password": self._hash_password("admin123"),
                        "role": "管理员",
                        "permissions": []
                    }
                ]
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, ensure_ascii=False, indent=4)
            return default_users
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f"加载用户信息失败: {str(e)}")
            return {"users": []}
    
    def save_users(self, users_data):
        """保存用户信息"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            current_app.logger.error(f"保存用户信息失败: {str(e)}")
            return False
    
    def add_user(self, username, password, role):
        """添加新用户"""
        users_data = self.load_users()
        
        # 检查用户名是否已存在
        for user in users_data['users']:
            if user['username'] == username:
                return False, "用户名已存在"
        
        # 创建新用户
        new_user = {
            "username": username,
            "password": self._hash_password(password),
            "role": role,
            "permissions": []
        }
        
        # 如果是管理员，不需要设置权限列表
        if role == "管理员":
            new_user["permissions"] = []
        
        users_data['users'].append(new_user)
        success = self.save_users(users_data)
        
        if success:
            return True, "用户添加成功"
        else:
            return False, "用户添加失败"
    
    def get_user(self, username):
        """获取指定用户信息"""
        users_data = self.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                return user
        
        return None
    
    def verify_user(self, username, password):
        """验证用户身份"""
        user = self.get_user(username)
        
        if not user:
            return False, "用户不存在"
        
        if user['password'] == self._hash_password(password):
            return True, user
        else:
            return False, "密码错误"
    
    def update_user_permissions(self, username, permissions):
        """更新用户权限"""
        users_data = self.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                # 如果是管理员，不允许修改权限
                if user['role'] == "管理员":
                    return False, "管理员权限不可修改"
                
                user['permissions'] = permissions
                success = self.save_users(users_data)
                
                if success:
                    return True, "权限更新成功"
                else:
                    return False, "权限更新失败"
        
        return False, "用户不存在"
    
    def change_password(self, username, current_password, new_password):
        """修改用户密码"""
        # 首先验证当前密码是否正确
        verify_result, message = self.verify_user(username, current_password)
        
        if not verify_result:
            return False, "当前密码错误"
        
        users_data = self.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                # 更新密码
                user['password'] = self._hash_password(new_password)
                success = self.save_users(users_data)
                
                if success:
                    return True, "密码修改成功"
                else:
                    return False, "密码修改失败"
        
        return False, "用户不存在"
    
    def delete_user(self, username):
        """删除用户"""
        users_data = self.load_users()
        
        for i, user in enumerate(users_data['users']):
            if user['username'] == username:
                # 不允许删除最后一个管理员
                if user['role'] == "管理员":
                    admin_count = sum(1 for u in users_data['users'] if u['role'] == "管理员")
                    if admin_count <= 1:
                        return False, "系统至少需要一个管理员账户"
                
                users_data['users'].pop(i)
                success = self.save_users(users_data)
                
                if success:
                    return True, "用户删除成功"
                else:
                    return False, "用户删除失败"
        
        return False, "用户不存在"
    
    def get_available_pages(self):
        """获取系统中所有可用的页面"""
        pages = []
        
        # 搜索templates目录下的所有HTML文件
        templates_dir = os.path.join('templates')
        html_files = glob.glob(os.path.join(templates_dir, '*.html'))
        
        for html_file in html_files:
            file_name = os.path.basename(html_file)
            # 排除一些特殊页面
            if file_name not in ['index.html', 'login.html', 'components']:
                pages.append({
                    'path': file_name,
                    'name': os.path.splitext(file_name)[0]
                })
        
        # 搜索templates/settings目录下的所有HTML文件
        settings_dir = os.path.join('templates', 'settings')
        if os.path.exists(settings_dir):
            settings_files = glob.glob(os.path.join(settings_dir, '*.html'))
            
            for html_file in settings_files:
                file_name = os.path.basename(html_file)
                pages.append({
                    'path': 'settings/' + file_name,
                    'name': 'settings_' + os.path.splitext(file_name)[0]
                })
        
        return pages
    
    def _hash_password(self, password):
        """对密码进行哈希处理"""
        return hashlib.md5(password.encode()).hexdigest()

# 创建工具类实例
user_util = UserUtil() 