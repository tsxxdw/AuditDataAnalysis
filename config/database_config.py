"""
数据库连接池配置

本模块定义了三种数据库（MySQL、SQL Server和Oracle）的连接池配置参数
"""

# 默认连接池配置
DEFAULT_POOL_CONFIG = {
    # 通用配置
    'pool_size': 10,          # 初始连接数
    'max_overflow': 20,       # 最大额外连接数
    'pool_timeout': 30,       # 获取连接超时(秒)
    'pool_recycle': 1800,     # 连接回收时间(秒)
    
    # MySQL特定配置
    'mysql': {
        'charset': 'utf8mb4',
        'connect_timeout': 10
    },
    
    # SQL Server特定配置
    'sqlserver': {
        'timeout': 30,
        'driver': '{ODBC Driver 17 for SQL Server}'
    },
    
    # Oracle特定配置
    'oracle': {
        'encoding': 'UTF-8',
        'nencoding': 'UTF-8'
    }
}

# 测试连接配置（不创建连接池）
TEST_CONNECTION_CONFIG = {
    'pool_size': 1,
    'max_overflow': 0,
    'pool_timeout': 10,
    'pool_recycle': 300
} 