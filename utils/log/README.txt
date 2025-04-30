====================================
日志系统使用说明
====================================

一、导入方法
------------------------------------

1. 基本日志记录器:
   ```python
   from utils.log.logger import app_logger

   # 使用示例
   app_logger.info("这是一条信息")
   app_logger.error("这是一条错误")
   app_logger.debug("这是一条调试信息")
   app_logger.warning("这是一条警告")
   app_logger.critical("这是一条严重错误")
   ```

2. 日志装饰器:
   ```python
   from utils.log.tools import log_with_context, safe_db_operation, handle_exceptions

   # 函数调用日志装饰器
   @log_with_context(level="INFO", with_args=True)
   def your_function(param1, param2):
       # 函数代码...
       pass

   # 数据库操作安全装饰器
   @safe_db_operation
   def db_query():
       # 数据库操作代码...
       pass

   # 异常处理装饰器
   @handle_exceptions(fallback_value=None, reraise=True)
   def risky_function():
       # 可能抛出异常的代码...
       pass
   ```

3. 异常处理:
   ```python
   from utils.log.exceptions import AppException, DatabaseException, ValidationException

   # 抛出自定义异常
   raise DatabaseException("数据库连接失败")
   raise ValidationException("输入参数无效")
   ```

4. 输入验证装饰器:
   ```python
   from utils.log.tools import validate_input

   def check_user_input(username, password):
       if not username or len(username) < 3:
           return False, "用户名不能为空且长度不能小于3位"
       if not password or len(password) < 6:
           return False, "密码不能为空且长度不能小于6位"
       return True, ""

   @validate_input(check_user_input)
   def login(username, password):
       # 登录逻辑
       pass
   ```

二、日志级别说明
------------------------------------
- DEBUG: 调试信息，详细的系统运行状态
- INFO: 普通信息，记录常规操作
- WARNING: 警告信息，可能的问题但不影响运行
- ERROR: 错误信息，影响功能但系统仍可运行
- CRITICAL: 严重错误，导致系统无法继续运行

三、日志文件存储位置
------------------------------------
日志文件保存在项目根目录下的 logs 文件夹中:

- 应用日志: logs/app_YYYY-MM-DD.log (每天一个文件)
- 错误日志: logs/error_YYYY-MM-DD.log (每天一个文件)

日志特点:
- 自动按天轮换
- 旧日志自动压缩为zip格式
- 应用日志保留30天
- 错误日志保留60天
- 包含详细的上下文信息和请求ID

四、请求ID跟踪
------------------------------------
系统会自动为每个HTTP请求分配唯一的请求ID，可用于跟踪整个请求生命周期中的所有日志。
请求ID会在响应头中返回(X-Request-ID)，方便前端或API调用方进行问题排查。

五、错误页面
------------------------------------
系统在发生异常时会自动渲染统一的错误页面(templates/log/error.html)，
显示错误代码、错误消息和请求ID，便于用户反馈问题。

六、常见问题
------------------------------------
1. 如何修改日志级别?
   在utils/log/logger.py中修改logger.add()方法的level参数。

2. 如何调整日志保留时间?
   在utils/log/logger.py中修改retention参数，例如timedelta(days=60)。

3. 如何在异常捕获后继续执行而不中断程序?
   使用handle_exceptions装饰器并设置reraise=False和fallback_value。 