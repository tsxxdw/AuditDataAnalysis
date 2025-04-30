"""
统一异常处理模块 - 异常类
"""
from datetime import datetime
from flask import request

class AppException(Exception):
    """应用自定义异常基类 - 所有系统异常继承此类"""
    
    def __init__(self, message, code=500, details=None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            code: HTTP状态码
            details: 详细错误信息（可选）
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self):
        """将异常转换为字典格式，便于JSON序列化"""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'timestamp': datetime.now().isoformat(),
            'request_id': getattr(request, 'request_id', None)
        } 