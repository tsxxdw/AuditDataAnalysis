"""
统一异常处理模块 - 异常处理器
"""
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
import traceback
from datetime import datetime
from utils.log.logger import app_logger
from .app_exception import AppException

def register_error_handlers(app):
    """
    注册全局异常处理器
    
    Args:
        app: Flask应用实例
    """
    
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
        
        # 返回统一格式的响应
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