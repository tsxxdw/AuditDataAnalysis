"""
通用API模块

提供系统级别的通用API接口
"""

from flask import Blueprint, jsonify, request
from service.log.logger import app_logger
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
from sqlalchemy import text

# 创建通用API蓝图
common_api_bp = Blueprint('common_api', __name__, url_prefix='/api/common')
# 实例化数据库服务
db_service = DatabaseService()

@common_api_bp.route('/database_info', methods=['GET'])
def get_database_info():
    """获取当前数据库类型和名称"""
    app_logger.info("获取当前数据库信息")
    
    try:
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({
                "success": False, 
                "message": "获取数据库配置失败", 
                "db_type": "未知", 
                "db_name": "未知"
            }), 500
        
        db_name = db_config.get('database', '未知')
        
        return jsonify({
            "success": True,
            "message": "获取数据库信息成功", 
            "db_type": db_type,
            "db_name": db_name
        })
        
    except Exception as e:
        app_logger.error(f"获取数据库信息失败: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"获取数据库信息失败: {str(e)}", 
            "db_type": "未知", 
            "db_name": "未知"
        }), 500

@common_api_bp.route('/tables', methods=['GET'])
def get_tables():
    """获取表列表"""
    app_logger.info("获取表列表")
    
    try:
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败", "tables": []}), 500
        
        # 使用数据库服务获取表列表
        tables = db_service.get_database_tables(db_type, db_config)
        
        return jsonify({
            "success": True,
            "message": "获取表列表成功", 
            "tables": tables
        })
    except Exception as e:
        app_logger.error(f"获取表列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取表列表失败: {str(e)}",
            "tables": []
        }), 500

@common_api_bp.route('/fields/<table_name>', methods=['GET'])
def get_fields(table_name):
    """获取表字段"""
    app_logger.info(f"获取表 {table_name} 的字段")
    
    try:
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败", "fields": []}), 500
        
        # 使用数据库服务获取表字段
        fields = db_service.get_table_field_info(db_type, db_config, table_name)
        
        return jsonify({
            "success": True,
            "message": "获取表字段成功", 
            "fields": fields
        })
    except Exception as e:
        app_logger.error(f"获取表字段失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取表字段失败: {str(e)}",
            "fields": []
        }), 500

@common_api_bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    """执行SQL语句"""
    app_logger.info("执行SQL请求")
    
    try:
        # 获取请求参数
        data = request.json
        sql = data.get('sql')
        
        # 参数验证
        if not sql:
            return jsonify({"success": False, "message": "SQL语句不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 记录将要执行的SQL
        app_logger.info(f"将要执行的SQL: {sql}")
        
        # 实际执行SQL
        result = db_service.execute_sql(db_type, db_config, text(sql))
        
        # 根据结果类型返回不同的消息
        if result.get('is_query', False):
            # 查询语句，返回查询结果
            rows = result.get('rows', [])
            # 将行转换为列表
            data = []
            for row in rows:
                data.append(list(row))
            
            return jsonify({
                "success": True,
                "message": "SQL执行成功",
                "is_query": True,
                "data": data,
                "row_count": len(data)
            })
        else:
            # 非查询语句，返回影响的行数
            affected_rows = result.get('affected_rows', 0)
            
            return jsonify({
                "success": True,
                "message": "SQL执行成功",
                "is_query": False,
                "affected_rows": affected_rows
            })
    
    except Exception as e:
        app_logger.error(f"执行SQL失败: {str(e)}")
        return jsonify({"success": False, "message": f"执行SQL失败: {str(e)}"}), 500 