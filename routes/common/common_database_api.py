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
    """执行SQL语句，支持多条SQL（以分号分隔）"""
    app_logger.info("执行SQL请求")
    
    try:
        # 获取请求参数
        data = request.json
        sql_input = data.get('sql')
        
        # 参数验证
        if not sql_input:
            return jsonify({"success": False, "message": "SQL语句不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 分割多条SQL语句（排除空行和纯注释行）
        sql_statements = []
        for sql in sql_input.split(';'):
            sql = sql.strip()
            if sql and not sql.startswith('--') and not sql.startswith('#'):
                sql_statements.append(sql)
        
        # 如果没有有效的SQL语句
        if not sql_statements:
            return jsonify({"success": False, "message": "未发现有效的SQL语句"}), 400
            
        # 存储每条SQL的执行结果
        results = []
        any_success = False
        error_occurred = False
        
        # 逐条执行SQL语句
        for i, sql in enumerate(sql_statements):
            sql_index = i + 1
            app_logger.info(f"执行SQL #{sql_index}: {sql}")
            
            # 如果已经发生错误，将剩余SQL标记为未执行
            if error_occurred:
                app_logger.info(f"SQL #{sql_index} 未执行，因为前面的SQL执行失败")
                results.append({
                    "sql_index": sql_index,
                    "sql": sql,
                    "success": False,
                    "is_query": False,
                    "message": "SQL未执行，因为前面的SQL执行失败",
                    "not_executed": True
                })
                continue
            
            try:
                # 执行当前SQL
                result = db_service.execute_sql(db_type, db_config, text(sql))
                
                # 构建基础结果信息
                sql_result = {
                    "sql_index": sql_index,
                    "sql": sql,
                    "success": True,
                    "message": "SQL执行成功"
                }
                
                # 根据结果类型添加不同信息
                if result.get('is_query', False):
                    # 查询语句，返回查询结果（限制最多1000条）
                    rows = result.get('rows', [])
                    # 将结果转换为列表，以便计算总行数
                    all_rows = list(rows)
                    # 将行转换为列表（最多1000条）
                    data = []
                    for idx, row in enumerate(all_rows):
                        if idx >= 1000:  # 限制最多1000条数据
                            break
                        data.append(list(row))
                    
                    # 添加查询结果信息
                    sql_result.update({
                        "is_query": True,
                        "data": data,
                        "row_count": len(data),
                        "total_count": len(all_rows),
                        "limited": len(all_rows) > 1000
                    })
                else:
                    # 非查询语句，返回影响的行数
                    affected_rows = result.get('affected_rows', 0)
                    sql_result.update({
                        "is_query": False,
                        "affected_rows": affected_rows
                    })
                
                # 添加到结果集
                results.append(sql_result)
                any_success = True
                
            except Exception as e:
                error_message = str(e)
                app_logger.error(f"执行SQL #{sql_index} 失败: {error_message}")
                
                # 添加错误信息到结果集
                results.append({
                    "sql_index": sql_index,
                    "sql": sql,
                    "success": False,
                    "is_query": False,
                    "message": f"SQL执行失败: {error_message}",
                    "error_detail": error_message
                })
                
                # 标记错误发生，后续SQL不会执行但会添加到结果中
                error_occurred = True
        
        # 返回所有SQL的执行结果
        return jsonify({
            "success": any_success,  # 只要有一条SQL执行成功，就算整体成功
            "message": "SQL执行完成" if not error_occurred else "部分SQL执行失败",
            "error_occurred": error_occurred,
            "results": results
        })
    
    except Exception as e:
        error_message = str(e)
        app_logger.error(f"执行SQL失败: {error_message}")
        return jsonify({
            "success": False, 
            "message": f"执行SQL失败: {error_message}",
            "error_detail": error_message
        }), 500 