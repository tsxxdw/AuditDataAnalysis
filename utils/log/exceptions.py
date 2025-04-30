from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
import traceback
from datetime import datetime
from utils.log.logger import app_logger

class AppException(Exception):
    """应用自定义异常基类"""
    
    def __init__(self, message, code=500, details=None):
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

# 常见业务异常类型
class DatabaseException(AppException):
    """数据库操作异常"""
    def __init__(self, message, details=None):
        super().__init__(message, code=500, details=details)

class ValidationException(AppException):
    """数据验证异常"""
    def __init__(self, message, details=None):
        super().__init__(message, code=400, details=details)

class ResourceNotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message, details=None):
        super().__init__(message, code=404, details=details)

class AuthorizationException(AppException):
    """授权异常"""
    def __init__(self, message, details=None):
        super().__init__(message, code=403, details=details)

def register_error_handlers(app):
    """注册全局异常处理器"""
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """处理自定义应用异常"""
        app_logger.error(f"应用异常: {error.message}", exc_info=True)
        
        # 判断请求类型，API请求返回JSON，页面请求返回错误页面
        if request.path.startswith('/api') or request.headers.get('Accept') == 'application/json':
            response = jsonify(error.to_dict())
            response.status_code = error.code
            return response
        else:
            # 页面请求返回错误页面
            return render_template(
                'log/error.html',
                error_code=error.code,
                error_message=error.message,
                page_title='错误',
                request_id=getattr(request, 'request_id', None)
            ), error.code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理HTTP异常"""
        app_logger.error(f"HTTP异常: {error}", exc_info=True)
        
        if request.path.startswith('/api') or request.headers.get('Accept') == 'application/json':
            response = jsonify({
                'code': error.code,
                'message': error.description,
                'timestamp': datetime.now().isoformat(),
                'request_id': getattr(request, 'request_id', None)
            })
            response.status_code = error.code
            return response
        else:
            return render_template(
                'log/error.html',
                error_code=error.code,
                error_message=error.description,
                page_title='错误',
                request_id=getattr(request, 'request_id', None)
            ), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理所有未捕获的异常"""
        app_logger.critical(f"未处理的异常: {error}", exc_info=True)
        
        # 获取详细的错误信息，仅在开发环境中返回
        error_details = traceback.format_exc() if app.debug else None
        
        if request.path.startswith('/api') or request.headers.get('Accept') == 'application/json':
            response = jsonify({
                'code': 500,
                'message': '服务器内部错误',
                'details': error_details,
                'timestamp': datetime.now().isoformat(),
                'request_id': getattr(request, 'request_id', None)
            })
            response.status_code = 500
            return response
        else:
            return render_template(
                'log/error.html',
                error_code=500,
                error_message='服务器内部错误',
                error_details=error_details,
                page_title='错误',
                request_id=getattr(request, 'request_id', None)
            ), 500 