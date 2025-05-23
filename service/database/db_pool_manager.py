"""
数据库连接池管理器

管理不同类型数据库的连接池，包括创建、获取、测试和关闭连接池
"""

import sys
import importlib
import time
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from config.database_config import DEFAULT_POOL_CONFIG, TEST_CONNECTION_CONFIG
from urllib.parse import quote_plus
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import safe_db_operation

# 数据库驱动配置
DB_DRIVERS = {
    'mysql': {
        'module': 'pymysql',
        'connection_prefix': 'mysql+pymysql'
    },
    'sqlserver': {
        'module': 'pyodbc',
        'connection_prefix': 'mssql+pyodbc'
    },
    'oracle': {
        'module': 'cx_Oracle',
        'connection_prefix': 'oracle+cx_oracle'
    }
}

class DatabasePoolManager:
    """数据库连接池管理器"""
    
    _instance = None  # 单例实例
    _pools = {}       # 连接池字典
    _drivers_loaded = {}  # 已加载的驱动
    
    @staticmethod
    def get_instance():
        """获取单例实例"""
        if DatabasePoolManager._instance is None:
            DatabasePoolManager._instance = DatabasePoolManager()
        return DatabasePoolManager._instance
    
    def __init__(self):
        """初始化连接池管理器"""
        self._drivers_loaded = {
            'mysql': False,
            'sqlserver': False,
            'oracle': False
        }
    
    def _load_driver(self, db_type):
        """加载特定数据库的驱动
        
        Args:
            db_type: 数据库类型
            
        Raises:
            AppException: 如果驱动加载失败
        """
        if self._drivers_loaded.get(db_type, False):
            return True
        
        driver_info = DB_DRIVERS.get(db_type)
        if not driver_info:
            raise AppException(f"不支持的数据库类型: {db_type}", code=400)
        
        module_name = driver_info['module']
        try:
            importlib.import_module(module_name)
            self._drivers_loaded[db_type] = True
            app_logger.info(f"已成功加载{db_type}数据库驱动: {module_name}")
            return True
        except ImportError as e:
            error_msg = f"无法加载{db_type}数据库驱动({module_name})，请确保已安装: pip install {module_name}"
            app_logger.error(f"{error_msg}. 错误: {str(e)}")
            raise AppException(error_msg, code=500, details={"original_error": str(e)})
    
    def get_pool(self, db_type, config):
        """获取或创建连接池"""
        # 加载驱动
        self._load_driver(db_type)
        
        pool_key = self._generate_pool_key(db_type, config)
        
        if pool_key not in self._pools:
            # 创建新连接池
            engine = self._create_engine(db_type, config)
            self._pools[pool_key] = engine
            app_logger.info(f"已创建新的{db_type}数据库连接池")
        
        return self._pools[pool_key]
    
    @safe_db_operation
    def get_connection(self, db_type, config):
        """获取数据库连接"""
        pool = self.get_pool(db_type, config)
        try:
            return pool.connect()
        except Exception as e:
            app_logger.error(f"获取{db_type}数据库连接失败: {str(e)}")
            raise AppException(f"获取数据库连接失败: {str(e)}", code=500)
    
    @safe_db_operation
    def test_connection(self, config):
        """测试数据库连接但不创建连接池"""
        db_type = config.get('type')
        
        if not db_type:
            raise AppException("未指定数据库类型", code=400)
        
        # 加载驱动
        self._load_driver(db_type)
        
        # 验证必要的连接参数
        self._validate_connection_config(db_type, config)
        
        # 创建临时引擎用于测试
        temp_engine = self._create_engine(db_type, config, for_test=True)
        
        try:
            # 尝试连接并执行简单查询
            with temp_engine.connect() as conn:
                test_query = self._get_test_query(db_type)
                result = conn.execute(text(test_query))
                result.close()
            return True
        except Exception as e:
            app_logger.error(f"数据库连接测试失败: {str(e)}")
            raise AppException(f"数据库连接测试失败: {str(e)}", code=500)
        finally:
            # 确保关闭临时引擎
            temp_engine.dispose()
    
    def _validate_connection_config(self, db_type, config):
        """验证连接配置参数的完整性
        
        Args:
            db_type: 数据库类型
            config: 连接配置
            
        Raises:
            AppException: 如果配置不完整
        """
        if db_type == 'mysql':
            required_fields = ['host', 'database']
            if not all(field in config for field in required_fields):
                raise AppException("MySQL连接配置不完整，必须包含: host, database", code=400)
        elif db_type == 'sqlserver':
            required_fields = ['host', 'database']
            if not all(field in config for field in required_fields):
                raise AppException("SQL Server连接配置不完整，必须包含: host, database", code=400)
        elif db_type == 'oracle':
            required_fields = ['host', 'service', 'username', 'password']
            if not all(field in config for field in required_fields):
                raise AppException("Oracle连接配置不完整，必须包含: host, service, username, password", code=400)
        else:
            raise AppException(f"不支持的数据库类型: {db_type}", code=400)
    
    @safe_db_operation
    def _create_engine(self, db_type, config, for_test=False):
        """创建数据库引擎"""
        # 构建连接字符串
        connection_string = self._build_connection_string(db_type, config)
        
        # 配置连接池参数
        pool_options = TEST_CONNECTION_CONFIG.copy() if for_test else {
            'pool_size': config.get('pool_size', DEFAULT_POOL_CONFIG['pool_size']),
            'max_overflow': config.get('max_overflow', DEFAULT_POOL_CONFIG['max_overflow']),
            'pool_timeout': config.get('pool_timeout', DEFAULT_POOL_CONFIG['pool_timeout']),
            'pool_recycle': config.get('pool_recycle', DEFAULT_POOL_CONFIG['pool_recycle']),
            'pool_pre_ping': True
        }
        
        # 添加数据库特定参数
        connect_args = {}
        if db_type == 'mysql' and 'mysql' in DEFAULT_POOL_CONFIG:
            connect_args.update(DEFAULT_POOL_CONFIG['mysql'])
        elif db_type == 'sqlserver' and 'sqlserver' in DEFAULT_POOL_CONFIG:
            connect_args.update(DEFAULT_POOL_CONFIG['sqlserver'])
        elif db_type == 'oracle' and 'oracle' in DEFAULT_POOL_CONFIG:
            connect_args.update(DEFAULT_POOL_CONFIG['oracle'])
        
        try:
            # 创建引擎
            return create_engine(
                connection_string,
                poolclass=QueuePool,
                connect_args=connect_args,
                **pool_options
            )
        except Exception as e:
            app_logger.error(f"创建数据库引擎失败: {str(e)}")
            raise AppException(f"创建数据库连接池失败: {str(e)}", code=500)
    
    def _build_connection_string(self, db_type, config):
        """构建连接字符串"""
        try:
            if db_type == 'mysql':
                # 安全处理密码，避免特殊字符问题
                password = quote_plus(config.get('password', ''))
                username = config.get('username', '')
                auth_part = f"{username}:{password}@" if username else ""
                return f"{DB_DRIVERS['mysql']['connection_prefix']}://{auth_part}{config.get('host', '')}:{config.get('port', '3306')}/{config.get('database', '')}"
            
            elif db_type == 'sqlserver':
                password = quote_plus(config.get('password', ''))
                instance = config.get('instance', '')
                host = config.get('host', '')
                db = config.get('database', '')
                
                # 构建服务器部分
                if instance:
                    server = f"{host}\\{instance}"
                else:
                    server = host
                
                # 尝试多种驱动程序选项
                # 如果配置中指定了驱动程序，使用配置的驱动
                driver = DEFAULT_POOL_CONFIG.get('sqlserver', {}).get('driver', '{ODBC Driver 17 for SQL Server}')
                
                # 构建连接字符串
                connection_prefix = DB_DRIVERS['sqlserver']['connection_prefix']
                
                # 处理不同的认证方式
                if config.get('auth_type') == 'windows':
                    # Windows认证 - 直接DSN-less连接
                    conn_str = f"{connection_prefix}:///?odbc_connect="
                    params = [
                        f"DRIVER={driver}",
                        f"SERVER={server}",
                        f"DATABASE={db}",
                        "Trusted_Connection=yes"
                    ]
                    
                    if config.get('port'):
                        params.append(f"PORT={config.get('port')}")
                    
                    return conn_str + quote_plus(';'.join(params))
                else:
                    # SQL Server认证 - 直接DSN-less连接
                    username = config.get('username', '')
                    conn_str = f"{connection_prefix}:///?odbc_connect="
                    params = [
                        f"DRIVER={driver}",
                        f"SERVER={server}",
                        f"DATABASE={db}"
                    ]
                    
                    if config.get('port'):
                        params.append(f"PORT={config.get('port')}")
                    
                    if username:
                        params.append(f"UID={username}")
                        params.append(f"PWD={password}")
                    
                    return conn_str + quote_plus(';'.join(params))
            
            elif db_type == 'oracle':
                password = quote_plus(config.get('password', ''))
                username = config.get('username', '')
                host = config.get('host', '')
                port = config.get('port', '1521')
                service = config.get('service', '')
                
                # 使用正确的SQLAlchemy cx_Oracle连接格式
                # 注意：service_name是作为查询参数而不是路径
                connection_string = f"{DB_DRIVERS['oracle']['connection_prefix']}://{username}:{password}@{host}:{port}/?service_name={service}"
                
                # 打印连接字符串(隐藏密码)
                masked_connection = f"{DB_DRIVERS['oracle']['connection_prefix']}://{username}:******@{host}:{port}/?service_name={service}"
                app_logger.info(f"Oracle连接字符串: {masked_connection}")
                
                # 尝试其他连接方式
                if host == 'localhost':
                    # 尝试方法1：使用127.0.0.1
                    app_logger.info("尝试连接方法1: 使用127.0.0.1替代localhost")
                    alt_connection_string1 = f"{DB_DRIVERS['oracle']['connection_prefix']}://{username}:{password}@127.0.0.1:{port}/?service_name={service}"
                    
                    # 尝试方法2：使用DSN方式
                    app_logger.info("尝试连接方法2: 使用DSN方式")
                    dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service})))"
                    alt_connection_string2 = f"{DB_DRIVERS['oracle']['connection_prefix']}://{username}:{password}@"
                    
                    # 尝试方法3：使用SID方式
                    app_logger.info("尝试连接方法3: 使用SID方式")
                    alt_connection_string3 = f"{DB_DRIVERS['oracle']['connection_prefix']}://{username}:{password}@{host}:{port}/{service}"
                    
                    # 先尝试原始方式
                    return connection_string
                
                return connection_string
            
            else:
                raise AppException(f"不支持的数据库类型: {db_type}", code=400)
        except Exception as e:
            app_logger.error(f"构建连接字符串失败: {str(e)}")
            raise AppException(f"构建数据库连接字符串失败: {str(e)}", code=500)
    
    def _get_test_query(self, db_type):
        """获取测试查询语句"""
        if db_type == 'oracle':
            return "SELECT 1 FROM DUAL"
        else:
            return "SELECT 1"
    
    def _generate_pool_key(self, db_type, config):
        """生成连接池键名"""
        try:
            if db_type == 'mysql':
                return f"mysql_{config.get('host', '')}_{config.get('port', '3306')}_{config.get('database', '')}"
            
            elif db_type == 'sqlserver':
                instance = config.get('instance', '')
                instance_part = f"_{instance}" if instance else ""
                return f"sqlserver_{config.get('host', '')}{instance_part}_{config.get('database', '')}"
            
            elif db_type == 'oracle':
                return f"oracle_{config.get('host', '')}_{config.get('port', '1521')}_{config.get('service', '')}"
            
            else:
                raise AppException(f"不支持的数据库类型: {db_type}", code=400)
        except Exception as e:
            app_logger.error(f"生成连接池键名失败: {str(e)}")
            raise AppException(f"生成连接池键名失败: {str(e)}", code=500)
    
    def shutdown(self):
        """关闭所有连接池"""
        for key, engine in list(self._pools.items()):
            try:
                app_logger.info(f"正在关闭连接池: {key}")
                engine.dispose()
                self._pools.pop(key, None)
            except Exception as e:
                app_logger.error(f"关闭连接池 {key} 失败: {str(e)}")
        self._pools.clear()