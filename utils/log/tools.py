import functools
from utils.log.logger import app_logger
from service.exception import AppException

def log_with_context(func=None, *, level='INFO', with_args=False, success_msg=None, error_msg=None):
    """
    日志记录装饰器，记录函数的调用、参数、返回值和异常
    
    Args:
        func: 被装饰的函数
        level: 日志级别，默认为INFO
        with_args: 是否记录函数参数，默认为False
        success_msg: 成功时的日志消息模板，可使用{result}引用返回值
        error_msg: 失败时的日志消息模板，可使用{error}引用异常
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            func_name = f"{fn.__module__}.{fn.__name__}"
            
            # 记录函数调用
            if with_args:
                arg_str = ', '.join([str(arg) for arg in args])
                kwarg_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
                params = f"args: [{arg_str}], kwargs: {{{kwarg_str}}}"
                app_logger.log(level, f"调用函数 {func_name} 开始，参数: {params}")
            else:
                app_logger.log(level, f"调用函数 {func_name} 开始")
            
            try:
                # 执行函数
                result = fn(*args, **kwargs)
                
                # 记录成功信息
                if success_msg:
                    app_logger.log(level, success_msg.format(result=result))
                else:
                    app_logger.log(level, f"函数 {func_name} 执行成功")
                
                return result
            
            except Exception as e:
                # 记录异常信息
                if error_msg:
                    app_logger.error(error_msg.format(error=str(e)), exc_info=True)
                else:
                    app_logger.error(f"函数 {func_name} 执行失败: {str(e)}", exc_info=True)
                
                # 重新抛出异常
                raise
        
        return wrapper
    
    # 处理直接调用和参数调用两种情况
    if func is None:
        return decorator
    return decorator(func)

def safe_db_operation(func):
    """
    数据库操作安全装饰器，捕获数据库异常并转换为统一的应用异常
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 这里可以根据具体的数据库类型捕获不同的异常
            # 例如 sqlalchemy.exc.SQLAlchemyError, pymysql.MySQLError 等
            app_logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
            raise AppException(f"数据库操作失败: {str(e)}", code=500)
    return wrapper

def validate_input(validation_func):
    """
    输入验证装饰器，验证输入参数是否合法
    
    Args:
        validation_func: 验证函数，接收和被装饰函数相同的参数，返回(is_valid, error_message)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 执行验证
            is_valid, error_message = validation_func(*args, **kwargs)
            if not is_valid:
                app_logger.warning(f"输入验证失败: {error_message}")
                raise AppException(error_message, code=400)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(func=None, *, fallback_value=None, reraise=True, log_level='ERROR'):
    """
    异常处理装饰器，捕获并记录异常，可选择返回默认值或重新抛出
    
    Args:
        func: 被装饰的函数
        fallback_value: 发生异常时返回的默认值
        reraise: 是否重新抛出异常，默认为True
        log_level: 日志级别，默认为ERROR
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                func_name = f"{fn.__module__}.{fn.__name__}"
                app_logger.log(log_level, f"函数 {func_name} 执行异常: {str(e)}", exc_info=True)
                
                if reraise:
                    if isinstance(e, AppException):
                        raise
                    else:
                        # 将普通异常转换为应用异常
                        raise AppException(str(e))
                else:
                    return fallback_value
        return wrapper
    
    # 处理直接调用和参数调用两种情况
    if func is None:
        return decorator
    return decorator(func) 