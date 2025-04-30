from loguru import logger
import sys
import os
import json
from datetime import timedelta
import uuid
import contextvars
from flask import request, g, has_request_context

# 获取日志配置
def get_log_config():
    """获取日志配置文件中的设置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'config', 'settings', 'log_config.json')
    
    # 默认配置
    default_config = {
        "log_path": "logs"
    }
    
    # 如果配置文件存在，读取配置
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception:
            # 如果读取失败，使用默认配置
            return default_config
    else:
        # 如果文件不存在，使用默认配置
        return default_config

# 获取日志目录
log_config = get_log_config()
LOG_DIR = os.path.abspath(log_config.get('log_path', 'logs'))
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
    # 首先检查是否在请求上下文中
    if has_request_context():
        # 在请求上下文中，尝试从Flask g对象获取
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
    if has_request_context():
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

# 提供重置日志配置的方法
def reload_log_config():
    """重新加载日志配置"""
    global LOG_DIR
    
    # 获取当前的请求ID
    req_id = get_request_id()
    log_instance = logger.bind(request_id=req_id)
    
    # 移除原有的处理器
    for handler_id in list(logger._core.handlers.keys()):
        if handler_id != 0:  # ID 0是默认的stderr处理器
            logger.remove(handler_id)
    
    # 重新获取日志配置
    log_config = get_log_config()
    LOG_DIR = os.path.abspath(log_config.get('log_path', 'logs'))
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 重新添加处理器
    logger.add(
        os.path.join(LOG_DIR, "app_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention=timedelta(days=30),
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | RequestID: {extra[request_id]} | {message}",
        level="DEBUG",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    
    logger.add(
        os.path.join(LOG_DIR, "error_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention=timedelta(days=60),
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | RequestID: {extra[request_id]} | {message}",
        level="ERROR",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    
    # 使用带有请求ID的logger实例记录日志
    log_instance.info(f"日志配置已重新加载，日志保存路径: {LOG_DIR}") 