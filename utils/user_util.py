"""
用户管理工具类

提供用户管理相关功能，包括用户添加、身份验证、权限管理等
"""

import json
import os
import hashlib
import shutil
from flask import current_app
import re

class UserUtil:
    users_file = os.path.join('config', 'user_management.json')
    
    @staticmethod
    def load_users():
        try:
            with open(UserUtil.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f"加载用户信息失败: {str(e)}")
            return {"users": []}
    
    @staticmethod
    def save_users(users_data):
        """保存用户信息"""
        try:
            with open(UserUtil.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            current_app.logger.error(f"保存用户信息失败: {str(e)}")
            return False
    
    @staticmethod
    def add_user(username, password, role):
        """添加新用户"""
        users_data = UserUtil.load_users()
        
        # 检查用户名是否已存在
        for user in users_data['users']:
            if user['username'] == username:
                return False, "用户名已存在"
        
        # 检查用户名是否只包含字母和数字
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return False, "用户名只能包含字母和数字"
        
        # 创建新用户
        new_user = {
            "username": username,
            "password": UserUtil._hash_password(password),
            "role": role,
            "permissions": []
        }
        
        # 如果是管理员，不需要设置权限列表
        if role == "管理员":
            new_user["permissions"] = []
        
        users_data['users'].append(new_user)
        success = UserUtil.save_users(users_data)
        
        if success:
            return True, "用户添加成功"
        else:
            return False, "用户添加失败"
    
    @staticmethod
    def get_user(username):
        """获取指定用户信息"""
        users_data = UserUtil.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                return user
        
        return None
    
    @staticmethod
    def verify_user(username, password):
        """验证用户身份"""
        user = UserUtil.get_user(username)
        
        if not user:
            return False, "用户不存在"
        
        if user['password'] == UserUtil._hash_password(password):
            return True, user
        else:
            return False, "密码错误"
    
    @staticmethod
    def update_user_permissions(username, permissions):
        """更新用户权限"""
        users_data = UserUtil.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                # 如果是管理员，不允许修改权限
                if user['role'] == "管理员":
                    return False, "管理员权限不可修改"
                
                user['permissions'] = permissions
                success = UserUtil.save_users(users_data)
                
                if success:
                    return True, "权限更新成功"
                else:
                    return False, "权限更新失败"
        
        return False, "用户不存在"
    
    @staticmethod
    def change_password(username, current_password, new_password):
        """修改用户密码"""
        # 首先验证当前密码是否正确
        verify_result, message = UserUtil.verify_user(username, current_password)
        
        if not verify_result:
            return False, "当前密码错误"
        
        users_data = UserUtil.load_users()
        
        for user in users_data['users']:
            if user['username'] == username:
                # 更新密码
                user['password'] = UserUtil._hash_password(new_password)
                success = UserUtil.save_users(users_data)
                
                if success:
                    return True, "密码修改成功"
                else:
                    return False, "密码修改失败"
        
        return False, "用户不存在"
    
    @staticmethod
    def delete_user(username):
        """删除用户"""
        users_data = UserUtil.load_users()
        
        for i, user in enumerate(users_data['users']):
            if user['username'] == username:
                # 不允许删除最后一个管理员
                if user['role'] == "管理员":
                    admin_count = sum(1 for u in users_data['users'] if u['role'] == "管理员")
                    if admin_count <= 1:
                        return False, "系统至少需要一个管理员账户"
                
                # 删除用户数据记录
                users_data['users'].pop(i)
                success = UserUtil.save_users(users_data)
                
                # 删除用户文件夹
                folders_to_delete = [
                    os.path.join('file', username),
                    os.path.join('configuration_data', username)
                ]
                
                for folder in folders_to_delete:
                    try:
                        if os.path.exists(folder):
                            shutil.rmtree(folder)
                            current_app.logger.info(f"已删除用户文件夹: {folder}")
                        else:
                            current_app.logger.warning(f"用户文件夹不存在: {folder}")
                    except Exception as e:
                        current_app.logger.error(f"删除用户文件夹失败: {folder}, 错误: {str(e)}")
                        # 即使文件夹删除失败，也认为用户删除成功，但记录错误日志
                
                if success:
                    return True, "用户删除成功"
                else:
                    return False, "用户删除失败"
        
        return False, "用户不存在"
    
    @staticmethod
    def _hash_password(password):
        """对密码进行哈希处理"""
        return hashlib.md5(password.encode()).hexdigest() 