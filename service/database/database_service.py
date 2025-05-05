"""
数据库服务类

提供数据库操作的服务，包括测试连接、执行查询等
"""

from .db_pool_manager import DatabasePoolManager
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import safe_db_operation, handle_exceptions

class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        """初始化数据库服务"""
        self.pool_manager = DatabasePoolManager.get_instance()
    
    @safe_db_operation
    def test_connection(self, config):
        """测试数据库连接
        
        Args:
            config: 数据库配置字典
            
        Returns:
            bool: 连接是否成功
            
        Raises:
            AppException: 连接失败时抛出
        """
        try:
            app_logger.info(f"正在测试数据库连接: {config.get('type')} - {config.get('host', '')}")
            result = self.pool_manager.test_connection(config)
            app_logger.info(f"数据库连接测试成功: {config.get('type')} - {config.get('host', '')}")
            return result
        except Exception as e:
            app_logger.error(f"数据库连接测试失败: {str(e)}")
            # 转换为友好的错误消息
            error_message = self._get_friendly_error_message(e, config.get('type'))
            raise AppException(error_message, code=500, details={"original_error": str(e), "db_type": config.get('type')})
    
    @safe_db_operation
    def execute_query(self, db_type, config, query, params=None):
        """执行查询
        
        Args:
            db_type: 数据库类型
            config: 数据库配置
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            result: 查询结果
            
        Raises:
            AppException: 查询失败时抛出
        """
        try:
            connection = self.pool_manager.get_connection(db_type, config)
            result = connection.execute(query, params or {})
            return result
        except Exception as e:
            app_logger.error(f"执行查询失败: {str(e)}")
            raise AppException(f"执行查询失败: {str(e)}", code=500, details={"query": query, "db_type": db_type})
        finally:
            if 'connection' in locals() and connection:
                connection.close()
    
    @safe_db_operation
    def execute_sql(self, db_type, config, sql, params=None):
        """执行任意SQL语句
        
        Args:
            db_type: 数据库类型
            config: 数据库配置
            sql: 要执行的SQL语句（字符串或text对象）
            params: SQL参数
            
        Returns:
            result: 执行结果，对于查询语句返回查询结果，对于DML语句返回受影响的行数
            
        Raises:
            AppException: 执行失败时抛出
        """
        try:
            connection = self.pool_manager.get_connection(db_type, config)
            
            # 执行SQL语句
            result = connection.execute(sql, params or {})
            
            # 确保sql是字符串，用于检查操作类型
            sql_str = str(sql) if hasattr(sql, 'text') else sql
            
            # 检查是否为查询语句
            if sql_str.strip().upper().startswith('SELECT'):
                # 查询语句，返回结果集已包含在result中
                return {
                    'rows': result,
                    'affected_rows': 0,
                    'is_query': True
                }
            else:
                # 非查询语句，需要显式提交事务
                try:
                    if hasattr(connection, 'commit'):
                        connection.commit()
                    elif hasattr(connection, 'get_transaction'):
                        # 某些连接可能有不同的提交机制
                        transaction = connection.get_transaction()
                        if transaction and hasattr(transaction, 'commit'):
                            transaction.commit()
                    
                    app_logger.debug(f"事务提交成功: {sql_str[:100]}...")
                    
                    # 返回影响的行数
                    return {
                        'rows': [],
                        'affected_rows': result.rowcount if hasattr(result, 'rowcount') else 0,
                        'is_query': False
                    }
                except Exception as commit_error:
                    app_logger.error(f"事务提交失败: {str(commit_error)}")
                    raise
                
        except Exception as e:
            # 尝试回滚事务
            try:
                if 'connection' in locals() and connection:
                    if hasattr(connection, 'rollback'):
                        connection.rollback()
                    elif hasattr(connection, 'get_transaction'):
                        transaction = connection.get_transaction()
                        if transaction and hasattr(transaction, 'rollback'):
                            transaction.rollback()
            except Exception as rollback_error:
                app_logger.error(f"事务回滚失败: {str(rollback_error)}")
                
            app_logger.error(f"执行SQL失败: {str(e)}")
            raise AppException(f"执行SQL失败: {str(e)}", code=500, details={"sql": str(sql), "db_type": db_type})
        finally:
            if 'connection' in locals() and connection:
                connection.close()
    
    @handle_exceptions(fallback_value="未知错误", reraise=True)
    def _get_friendly_error_message(self, exception, db_type):
        """获取友好的错误消息
        
        Args:
            exception: 异常对象
            db_type: 数据库类型
            
        Returns:
            str: 友好的错误消息
        """
        error_str = str(exception).lower()
        
        # 共通错误
        if "timeout" in error_str:
            return "连接超时，请检查网络或服务器是否可达"
        elif "refused" in error_str or "could not connect" in error_str:
            return "连接被拒绝，请检查主机名和端口是否正确"
            
        # 特定数据库错误
        if db_type == 'mysql':
            if "access denied" in error_str:
                return "访问被拒绝，请检查用户名和密码"
            elif "unknown database" in error_str:
                return "数据库不存在，请检查数据库名称"
        elif db_type == 'sqlserver':
            if "login failed" in error_str:
                return "登录失败，请检查用户名和密码"
            elif "database" in error_str and "does not exist" in error_str:
                return "数据库不存在，请检查数据库名称"
            elif "named pipes provider" in error_str:
                return "无法连接到SQL Server，请检查服务器名称和实例名"
        elif db_type == 'oracle':
            if "invalid username" in error_str or "invalid password" in error_str or "ora-01017" in error_str:
                return "用户名或密码无效"
            elif "service" in error_str and "not found" in error_str or "ora-12514" in error_str:
                return "服务名无效，请检查服务名称"
            elif "tns" in error_str:
                return "TNS连接错误，请检查主机名和端口"
                
        # 默认错误
        return f"连接失败: {str(exception)}" 