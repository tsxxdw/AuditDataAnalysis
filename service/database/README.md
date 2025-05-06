# 数据库连接池使用说明

## 概述

本模块提供了统一的数据库连接池管理功能，支持MySQL、SQL Server和Oracle三种数据库。使用连接池可以大幅提高数据库连接的效率和稳定性。

## 依赖安装

在使用本模块前，需要安装相关依赖：

```bash
# 安装主要依赖
pip install -r requirements.txt

# 或者单独安装数据库驱动
pip install SQLAlchemy sqlalchemy-utils
pip install pymysql  # MySQL驱动
pip install pyodbc   # SQL Server驱动
pip install cx-Oracle  # Oracle驱动
```

### 系统依赖

某些数据库驱动需要额外的系统依赖：

1. **SQL Server (pyodbc)**:
   - Windows: 安装[Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - Linux: 参考[Linux安装指南](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

2. **Oracle (cx_Oracle)**:
   - 安装[Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - 设置环境变量`LD_LIBRARY_PATH`(Linux)或`PATH`(Windows)指向Oracle客户端库

## 基本使用

### 测试数据库连接

```python
from service.database import DatabaseService

# 创建数据库服务实例
db_service = DatabaseService()

# 测试MySQL连接
mysql_config = {
    'type': 'mysql',
    'host': 'localhost',
    'port': '3306',
    'database': 'mydb',
    'username': 'user',
    'password': 'password'
}
try:
    db_service.test_connection(mysql_config)
    print("MySQL连接成功!")
except Exception as e:
    print(f"连接失败: {str(e)}")

# 测试SQL Server连接
sqlserver_config = {
    'type': 'sqlserver',
    'host': 'localhost',
    'port': '1433',
    'database': 'mydb',
    'auth_type': 'sql',  # 'sql'或'windows'
    'username': 'user',
    'password': 'password',
    'instance': ''  # 实例名(可选)
}
db_service.test_connection(sqlserver_config)

# 测试Oracle连接
oracle_config = {
    'type': 'oracle',
    'host': 'localhost',
    'port': '1521',
    'service': 'XE',  # 服务名
    'username': 'user',
    'password': 'password'
}
db_service.test_connection(oracle_config)
```

### 执行SQL查询

```python
from service.database import DatabaseService

db_service = DatabaseService()

# 配置连接
config = {
    'type': 'mysql',
    'host': 'localhost',
    'port': '3306',
    'database': 'mydb',
    'username': 'user',
    'password': 'password'
}

# 执行查询
result = db_service.execute_sql(
    'mysql', 
    config, 
    "SELECT * FROM users WHERE age > :age", 
    {'age': 18}
)

# 处理结果
for row in result['rows']:
    print(row)
```

## 连接池配置

连接池配置在`config/database_config.py`中定义：

```python
# 默认连接池配置
DEFAULT_POOL_CONFIG = {
    # 通用配置
    'pool_size': 10,          # 初始连接数
    'max_overflow': 20,       # 最大额外连接数
    'pool_timeout': 30,       # 获取连接超时(秒)
    'pool_recycle': 1800,     # 连接回收时间(秒)
    
    # 数据库特定配置
    'mysql': { ... },
    'sqlserver': { ... },
    'oracle': { ... }
}
```

## 异常处理

本模块使用统一的异常处理机制（AppException），所有数据库相关错误都会转换为友好的错误消息。

```python
try:
    db_service.test_connection(config)
except AppException as e:
    print(f"错误: {e.message}")
    print(f"错误详情: {e.details}")
```

## 多线程安全

连接池管理器采用线程安全设计，可以在多线程环境中安全使用。

## 性能优化建议

1. 根据应用负载调整连接池大小
   - 高并发场景: 增加`pool_size`和`max_overflow`
   - 低并发场景: 减小连接池大小节省资源

2. 设置合理的`pool_recycle`值
   - 某些数据库有连接超时设置(如MySQL默认8小时)
   - 建议设置小于数据库超时设置的值(如3600秒)

3. 在应用结束时关闭连接池
   - 应用程序退出前调用`shutdown_db_pools()`

## 故障排查

1. **驱动安装问题**：如遇到"无法加载数据库驱动"错误，检查是否正确安装了相应驱动
2. **网络连接问题**：检查防火墙设置，确保数据库端口开放
3. **认证问题**：验证用户名和密码是否正确
4. **系统依赖问题**：对于SQL Server和Oracle，检查系统客户端库是否正确安装 