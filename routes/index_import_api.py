"""
数据导入页面API

提供数据导入相关的API，包括获取数据库类型、获取数据库表、获取表字段等
"""

from flask import Blueprint, jsonify, request
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
from service.database.db_pool_manager import DatabasePoolManager
from service.log.logger import app_logger
from service.exception import AppException
from sqlalchemy import text

# 创建蓝图
import_api_bp = Blueprint('import_api', __name__)

# 数据库服务实例
db_service = DatabaseService()

@import_api_bp.route('/api/import/db_types', methods=['GET'])
def get_db_types():
    """获取所有可用的数据库类型
    
    Returns:
        JSON: 包含所有可用数据库类型的列表
    """
    try:
        db_types = DatabaseConfigUtil.get_all_database_types()
        default_type = DatabaseConfigUtil.get_default_db_type()
        
        result = []
        for db_type in db_types:
            result.append({
                'id': db_type,
                'name': get_db_display_name(db_type),
                'isDefault': db_type == default_type
            })
        
        return jsonify(result)
    except Exception as e:
        app_logger.error(f"获取数据库类型列表失败: {str(e)}")
        raise AppException("获取数据库类型列表失败", 500, details={"error": str(e)})

@import_api_bp.route('/api/import/tables', methods=['GET'])
def get_tables():
    """获取指定数据库的所有表
    
    Query Parameters:
        db_type: 数据库类型
        
    Returns:
        JSON: 包含所有表名的列表
    """
    db_type = request.args.get('db_type')
    if not db_type:
        return jsonify({"error": "未指定数据库类型"}), 400
    
    try:
        # 获取数据库配置
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        if not db_config:
            return jsonify({"error": f"找不到数据库类型 '{db_type}' 的配置"}), 404
        
        # 获取所有表名
        tables = get_database_tables(db_type, db_config)
        
        # 返回结果
        return jsonify(tables)
    except Exception as e:
        app_logger.error(f"获取数据库表列表失败: {str(e)}")
        return jsonify({"error": f"获取表列表失败: {str(e)}"}), 500

def get_database_tables(db_type, db_config):
    """根据数据库类型获取表列表
    
    Args:
        db_type: 数据库类型
        db_config: 数据库配置
        
    Returns:
        list: 表信息列表，每个表包含id和name
    """
    try:
        # 获取数据库名
        database = db_config.get('database', '')
        
        if not database:
            raise AppException("数据库名称为空", 400)
        
        # 根据数据库类型处理查询
        if db_type == 'mysql':
            # MySQL需要先选择数据库，然后查询表
            # 首先获取连接
            connection = db_service.pool_manager.get_connection(db_type, db_config)
            try:
                # 执行USE语句选择数据库
                connection.execute(text(f"USE `{database}`"))
                # 查询所有表
                result = connection.execute(text("SHOW TABLES"))
                
                # 提取表名
                tables = []
                for row in result:
                    table_name = row[0]
                    tables.append({
                        'id': table_name,
                        'name': table_name
                    })
                
                # 按表名排序
                tables.sort(key=lambda x: x['name'])
                return tables
            finally:
                connection.close()
        else:
            # 其他数据库使用统一的查询方法
            query, params = get_tables_query(db_type, database)
            result = db_service.execute_query(db_type, db_config, text(query), params)
            
            # 提取表名
            tables = []
            for row in result:
                table_name = row[0]
                tables.append({
                    'id': table_name,
                    'name': table_name
                })
            
            # 按表名排序
            tables.sort(key=lambda x: x['name'])
            return tables
    except Exception as e:
        app_logger.error(f"获取表列表失败: {str(e)}")
        raise AppException(f"获取表列表失败: {str(e)}", 500)

def get_tables_query(db_type, database):
    """根据数据库类型构建获取表列表的SQL查询
    
    Args:
        db_type: 数据库类型
        database: 数据库名称
        
    Returns:
        tuple: (SQL查询语句, 参数字典)
    """
    if db_type == 'mysql':
        # MySQL查询返回不带参数的查询
        return f"SHOW TABLES", {}
    elif db_type == 'sqlserver':
        return "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog = :database", {"database": database}
    elif db_type == 'oracle':
        return "SELECT table_name FROM all_tables WHERE owner = UPPER(:database)", {"database": database}
    else:
        raise AppException(f"不支持的数据库类型: {db_type}", 400)

def get_db_display_name(db_type):
    """获取数据库类型的显示名称
    
    Args:
        db_type: 数据库类型标识符
        
    Returns:
        str: 数据库类型的显示名称
    """
    display_names = {
        'mysql': 'MySQL',
        'sqlserver': 'SQL Server',
        'oracle': 'Oracle'
    }
    return display_names.get(db_type, db_type)

def register_routes(app):
    """注册路由
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(import_api_bp) 