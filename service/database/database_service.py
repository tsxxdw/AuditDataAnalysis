"""
数据库服务类

提供数据库操作的服务，包括测试连接、执行查询等
"""

from .db_pool_manager import DatabasePoolManager
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import safe_db_operation, handle_exceptions
from sqlalchemy import text

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
    
    @safe_db_operation
    def get_database_tables(self, db_type, db_config):
        """获取数据库表列表，包含表名和表备注信息
        
        Args:
            db_type: 数据库类型
            db_config: 数据库配置
            
        Returns:
            list: 表信息列表，每个表包含id、name和comment
            
        Raises:
            AppException: 获取失败时抛出
        """
        try:
            # 获取数据库名
            database = db_config.get('database', '')
            
            if not database:
                raise AppException("数据库名称为空", 400)
            
            # 根据数据库类型处理查询
            if db_type == 'mysql':
                # MySQL需要先选择数据库，然后查询表
                connection = self.pool_manager.get_connection(db_type, db_config)
                try:
                    # 执行USE语句选择数据库
                    connection.execute(text(f"USE `{database}`"))
                    
                    # 查询所有表及其备注
                    result = connection.execute(text("""
                        SELECT 
                            TABLE_NAME, 
                            TABLE_COMMENT 
                        FROM 
                            INFORMATION_SCHEMA.TABLES 
                        WHERE 
                            TABLE_SCHEMA = :database 
                            AND TABLE_TYPE = 'BASE TABLE'
                    """), {"database": database})
                    
                    # 提取表名和备注
                    tables = []
                    for row in result:
                        table_name = row[0]
                        table_comment = row[1] if len(row) > 1 and row[1] else ''
                        tables.append({
                            'id': table_name,
                            'name': table_name,
                            'comment': table_comment
                        })
                    
                    # 按表名排序
                    tables.sort(key=lambda x: x['name'])
                    return tables
                finally:
                    connection.close()
            elif db_type == 'sqlserver':
                # SQL Server查询表及备注
                query = """
                    SELECT 
                        t.name as TABLE_NAME, 
                        CAST(ISNULL(p.value, '') as NVARCHAR(MAX)) as TABLE_COMMENT 
                    FROM 
                        sys.tables t 
                    LEFT JOIN 
                        sys.extended_properties p 
                    ON 
                        p.major_id = t.object_id 
                        AND p.minor_id = 0 
                        AND p.name = 'MS_Description'
                    WHERE 
                        SCHEMA_NAME(t.schema_id) = :schema
                    ORDER BY 
                        t.name
                """
                # 默认使用dbo架构，除非另有指定
                schema = db_config.get('schema', 'dbo')
                result = self.execute_query(db_type, db_config, text(query), {"schema": schema})
                
                # 提取表名和备注
                tables = []
                for row in result:
                    table_name = row[0]
                    table_comment = row[1] if len(row) > 1 and row[1] else ''
                    tables.append({
                        'id': table_name,
                        'name': table_name,
                        'comment': table_comment
                    })
                
                return tables
            elif db_type == 'oracle':
                # Oracle查询表及备注
                query = """
                    SELECT 
                        t.TABLE_NAME, 
                        c.COMMENTS 
                    FROM 
                        ALL_TABLES t 
                    LEFT JOIN 
                        ALL_TAB_COMMENTS c 
                    ON 
                        t.OWNER = c.OWNER 
                        AND t.TABLE_NAME = c.TABLE_NAME 
                    WHERE 
                        t.OWNER = UPPER(:owner)
                    ORDER BY 
                        t.TABLE_NAME
                """
                result = self.execute_query(db_type, db_config, text(query), {"owner": database})
                
                # 提取表名和备注
                tables = []
                for row in result:
                    table_name = row[0]
                    table_comment = row[1] if len(row) > 1 and row[1] else ''
                    tables.append({
                        'id': table_name,
                        'name': table_name,
                        'comment': table_comment
                    })
                
                return tables
            else:
                raise AppException(f"不支持的数据库类型: {db_type}", 400)
        except Exception as e:
            app_logger.error(f"获取表列表失败: {str(e)}")
            raise AppException(f"获取表列表失败: {str(e)}", 500)
    
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

    @safe_db_operation
    def get_table_field_info(self, db_type, db_config, table_name):
        """获取数据库表的字段信息
        
        Args:
            db_type: 数据库类型
            db_config: 数据库配置
            table_name: 表名
            
        Returns:
            list: 字段信息列表，每个元素包含字段名、类型等信息
            
        Raises:
            AppException: 获取失败时抛出
        """
        try:
            # 获取数据库名
            database = db_config.get('database', '')
            
            if not database:
                raise AppException("数据库名称为空", 400)
            
            if db_type == 'mysql':
                # 使用MySQL信息模式查询表结构
                connection = self.pool_manager.get_connection(db_type, db_config)
                try:
                    # 选择数据库
                    connection.execute(text(f"USE `{database}`"))
                    
                    # 查询表字段信息
                    result = connection.execute(text(f"""
                        SELECT 
                            COLUMN_NAME, 
                            DATA_TYPE,
                            COLUMN_COMMENT,
                            ORDINAL_POSITION
                        FROM 
                            INFORMATION_SCHEMA.COLUMNS 
                        WHERE 
                            TABLE_SCHEMA = :database 
                            AND TABLE_NAME = :table_name
                        ORDER BY 
                            ORDINAL_POSITION
                    """), {"database": database, "table_name": table_name})
                    
                    # 提取字段信息
                    fields = []
                    for row in result:
                        fields.append({
                            "name": row[0],
                            "type": row[1],
                            "comment": row[2] if row[2] else '',
                            "position": row[3]
                        })
                    
                    return fields
                finally:
                    connection.close()
            elif db_type == 'sqlserver':
                # SQL Server表字段查询
                query = """
                    SELECT 
                        c.name AS COLUMN_NAME,
                        t.name AS DATA_TYPE,
                        ep.value AS COLUMN_COMMENT,
                        c.column_id AS ORDINAL_POSITION
                    FROM 
                        sys.columns c
                    INNER JOIN 
                        sys.types t ON c.user_type_id = t.user_type_id
                    LEFT JOIN 
                        sys.extended_properties ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description'
                    WHERE 
                        c.object_id = OBJECT_ID(:table_name)
                    ORDER BY 
                        c.column_id
                """
                result = self.execute_query(db_type, db_config, text(query), {"table_name": table_name})
                
                fields = []
                for row in result:
                    fields.append({
                        "name": row[0],
                        "type": row[1],
                        "comment": row[2] if row[2] else '',
                        "position": row[3]
                    })
                
                return fields
            elif db_type == 'oracle':
                # Oracle表字段查询
                query = """
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        COLUMN_ID
                    FROM 
                        ALL_TAB_COLUMNS
                    WHERE 
                        OWNER = UPPER(:owner)
                        AND TABLE_NAME = UPPER(:table_name)
                    ORDER BY 
                        COLUMN_ID
                """
                result = self.execute_query(db_type, db_config, text(query), {"owner": database, "table_name": table_name})
                
                fields = []
                for row in result:
                    fields.append({
                        "name": row[0],
                        "type": row[1],
                        "comment": '',
                        "position": row[2]
                    })
                
                return fields
            else:
                raise AppException(f"不支持的数据库类型: {db_type}", 400)
        except Exception as e:
            app_logger.error(f"获取表字段信息失败: {str(e)}")
            raise AppException(f"获取表字段信息失败: {str(e)}", 500) 