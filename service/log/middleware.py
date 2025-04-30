from flask import request, g
import time
from functools import wraps
from service.log.logger import set_request_id, app_logger

class RequestIdMiddleware:
    """为每个请求分配唯一ID的中间件"""

    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

    def before_request(self):
        """在请求开始前设置请求ID"""
        # 首先检查请求头中是否已有请求ID
        req_id = request.headers.get('X-Request-ID')
        # 如果没有，生成一个新的
        g.request_id = set_request_id(req_id)
        # 记录请求开始
        g.request_start_time = time.time()
        app_logger.info(f"开始处理请求: {request.method} {request.path}")

    def after_request(self, response):
        """在请求结束后记录请求信息"""
        # 添加请求ID到响应头
        response.headers['X-Request-ID'] = g.request_id
        
        # 计算请求处理时间
        if hasattr(g, 'request_start_time'):
            elapsed = time.time() - g.request_start_time
            app_logger.info(f"请求处理完成: {request.method} {request.path} - 状态码: {response.status_code} - 耗时: {elapsed:.4f}秒")
        
        return response

def init_log_middleware(app):
    """初始化日志相关中间件"""
    RequestIdMiddleware(app)
    return app

def log_function_call(func):
    """函数调用日志装饰器，用于记录关键业务函数的调用"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        app_logger.debug(f"调用函数 {func_name} 开始")
        try:
            result = func(*args, **kwargs)
            app_logger.debug(f"调用函数 {func_name} 成功完成")
            return result
        except Exception as e:
            app_logger.error(f"调用函数 {func_name} 失败: {str(e)}")
            raise
    return wrapper 