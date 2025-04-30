from loguru import logger
import sys
import os
from datetime import timedelta
import uuid
import contextvars
from flask import request, g

# 创建日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 请求ID上下文变量
request_id_var = contextvars.ContextVar('request_id', default=None)

# 配置Loguru
logger.remove()  # 移除默认处理器

# 添加控制台输出
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <yellow>RequestID: {extra[request_id]}</yellow> | <level>{message}</level>",
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# 添加文件输出（按天轮换）
logger.add(
    os.path.join(LOG_DIR, "app_{time:YYYY-MM-DD}.log"),
    rotation="00:00",  # 每天午夜轮换
    retention=timedelta(days=30),  # 保留30天
    compression="zip",  # 压缩旧日志
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | RequestID: {extra[request_id]} | {message}",
    level="DEBUG",
    backtrace=True,
    diagnose=True,
    enqueue=True,  # 启用异步记录
)

# 添加错误日志文件
logger.add(
    os.path.join(LOG_DIR, "error_{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention=timedelta(days=60),  # 错误日志保留更长时间
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | RequestID: {extra[request_id]} | {message}",
    level="ERROR",
    backtrace=True,
    diagnose=True,
    enqueue=True,
)

def get_request_id():
    """获取当前请求ID，如果不存在则生成一个新的"""
    # 首先尝试从Flask g对象获取
    if hasattr(g, 'request_id'):
        return g.request_id
    
    # 然后尝试从contextvars获取
    req_id = request_id_var.get()
    if req_id is not None:
        return req_id
    
    # 如果都没有，生成一个新的
    return str(uuid.uuid4())

def set_request_id(req_id=None):
    """设置请求ID到上下文变量"""
    if req_id is None:
        req_id = str(uuid.uuid4())
    
    # 同时设置到Flask g对象和contextvars
    if hasattr(request, 'environ'):
        g.request_id = req_id
    
    request_id_var.set(req_id)
    return req_id

# 获得带请求ID上下文的logger
def get_logger():
    """返回一个带有请求ID的logger实例"""
    req_id = get_request_id()
    return logger.bind(request_id=req_id)

# 方便在其他模块中导入
app_logger = get_logger() 