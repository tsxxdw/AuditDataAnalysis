"""
请求工具模块

提供处理HTTP请求的实用函数
"""

from flask import request

def is_local_request():
    """检查当前请求是否来自本地
    
    基于请求的Host头判断是否为localhost或127.0.0.1
    
    Returns:
        bool: 是否为本地请求
    """
    host = request.host.split(':')[0].lower()
    return host in ('localhost', '127.0.0.1') 