#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import base64
from service.log.logger import app_logger
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 密钥文件路径
KEY_FILE = os.path.join('config', 'secure', '.encryption_key')

# 用于生成密钥的应用密钥短语（在生产环境中应从环境变量获取）
# 注意：这只是一个示例，实际应用中应该使用更安全的方式存储
APP_SECRET = "AuditDataAnalysisSecureKey_DoNotShare"

# 用于生成密钥的盐值
SALT = b'AuditDataAnalysisSalt2023'


def ensure_key_directory():
    """确保密钥目录存在"""
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)


def get_or_generate_key():
    """获取现有密钥或生成新密钥"""
    ensure_key_directory()
    
    # 尝试读取现有密钥
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        except Exception as e:
            app_logger.error(f"读取加密密钥失败: {str(e)}")
    
    # 如果密钥不存在或读取失败，生成新密钥
    try:
        # 使用PBKDF2派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(APP_SECRET.encode()))
        
        # 保存密钥
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        
        app_logger.info("已生成新的加密密钥")
        return key
    except Exception as e:
        app_logger.error(f"生成加密密钥失败: {str(e)}")
        # 返回一个备用密钥以保证功能可用
        # 注意：这是一个应急措施，生产环境中应该有更好的错误处理
        return Fernet.generate_key()


def encrypt_data(data):
    """加密敏感数据
    
    Args:
        data (str): 需要加密的敏感数据
        
    Returns:
        str: 加密后的数据（Base64编码字符串）
    """
    if not data:
        return ""
    
    try:
        key = get_or_generate_key()
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        app_logger.error(f"加密数据失败: {str(e)}")
        return ""


def decrypt_data(encrypted_data):
    """解密敏感数据
    
    Args:
        encrypted_data (str): 加密后的数据（Base64编码字符串）
        
    Returns:
        str: 解密后的原始数据
    """
    if not encrypted_data:
        return ""
    
    try:
        key = get_or_generate_key()
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode()
    except Exception as e:
        app_logger.error(f"解密数据失败: {str(e)}")
        return ""


def encrypt_api_key(api_key):
    """加密API密钥
    
    Args:
        api_key (str): 原始API密钥
        
    Returns:
        str: 加密后的API密钥
    """
    return encrypt_data(api_key)


def decrypt_api_key(encrypted_api_key):
    """解密API密钥
    
    Args:
        encrypted_api_key (str): 加密后的API密钥
        
    Returns:
        str: 解密后的原始API密钥
    """
    return decrypt_data(encrypted_api_key)


def is_encrypted(data):
    """检查数据是否已经被加密
    
    Args:
        data (str): 要检查的数据
        
    Returns:
        bool: 如果数据已加密返回True，否则返回False
    """
    if not data or not isinstance(data, str):
        return False
    
    # 检查是否是有效的Base64编码
    try:
        # 尝试Base64解码
        decoded = base64.urlsafe_b64decode(data)
        # 检查解码后的数据是否看起来像Fernet加密的数据
        return len(decoded) > 32
    except:
        return False 