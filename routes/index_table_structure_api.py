"""
表结构管理 API

负责处理与表结构管理相关的API请求
"""

import re
import os
from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
from pypinyin import lazy_pinyin
from utils.excel_util import ExcelUtil
from service.exception import AppException
from sqlalchemy import text

# 创建蓝图
index_table_structure_bp = Blueprint('index_table_structure_api', __name__, url_prefix='/api/table_structure')

# 实例化数据库服务
db_service = DatabaseService()

def generate_field_name(column_index, comment):
    """
    根据列索引和注释内容生成字段名
    
    Args:
        column_index (int): 列索引
        comment (str): 注释内容
        
    Returns:
        str: 生成的字段名，格式为 t_列索引_名称
    """
    try:
        # 移除非中英文字符
        clean_comment = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', comment)
        
        # 判断是否是空的
        if not clean_comment:
            # 如果注释为空或只包含特殊字符，使用默认名称
            return f"t_{column_index}_field"
        
        # 分离中文和英文
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        english_pattern = re.compile(r'[a-zA-Z]+')
        
        chinese_chars = ''.join(chinese_pattern.findall(clean_comment))
        english_chars = ''.join(english_pattern.findall(clean_comment))
        
        # 处理中文字符（转拼音首字母）
        pinyin_chars = ''
        if chinese_chars:
            pinyin_list = lazy_pinyin(chinese_chars)
            pinyin_chars = ''.join([word[0] for word in pinyin_list if word])
        
        # 合并英文和拼音首字母
        result = (english_chars + pinyin_chars).lower()
        
        # 截取前5位
        result = result[:5]
        
        # 加上前缀
        return f"t_{column_index}_{result}"
    except Exception as e:
        app_logger.error(f"生成字段名失败: {str(e)}")
        # 返回安全的默认名称
        return f"t_{column_index}_field"

@index_table_structure_bp.route('/tables', methods=['GET'])
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

@index_table_structure_bp.route('/create_table', methods=['POST'])
def create_table():
    """创建表"""
    app_logger.info("创建表请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        table_comment = data.get('tableComment', '')
        excel_path = data.get('excelPath')
        comment_row = int(data.get('commentRow', 1))
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not excel_path:
            return jsonify({"success": False, "message": "Excel文件路径不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 读取Excel文件中的字段注释行
        try:
            rows = ExcelUtil.read_excel_data(
                file_path=excel_path,
                start_row=comment_row - 1,  # 行号从0开始，需要减1
                row_limit=1
            )
            
            if not rows or len(rows) == 0:
                return jsonify({"success": False, "message": "Excel文件中未找到字段注释行"}), 400
                
            field_comments = rows[0]  # 获取字段注释行
            
            # 生成创建表的SQL
            columns = []
            
            # 先添加id字段
            columns.append("id INT NOT NULL AUTO_INCREMENT")
            
            # 为每个注释生成对应的字段
            for i, comment in enumerate(field_comments):
                if comment:  # 只处理非空注释
                    field_name = generate_field_name(i, comment)
                    
                    # 根据数据库类型选择合适的字段类型
                    if db_type == 'mysql':
                        column_def = f"{field_name} VARCHAR(255) COMMENT '{comment}'"
                    elif db_type == 'sqlserver':
                        column_def = f"{field_name} NVARCHAR(255)"
                    elif db_type == 'oracle':
                        column_def = f"{field_name} VARCHAR2(255)"
                    else:
                        column_def = f"{field_name} VARCHAR(255)"
                    
                    columns.append(column_def)
            
            # 添加create_time和update_time字段
            if db_type == 'mysql':
                columns.append("create_time DATETIME DEFAULT CURRENT_TIMESTAMP")
                columns.append("update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            elif db_type == 'sqlserver':
                columns.append("create_time DATETIME DEFAULT GETDATE()")
                columns.append("update_time DATETIME DEFAULT GETDATE()")
            elif db_type == 'oracle':
                columns.append("create_time TIMESTAMP DEFAULT SYSTIMESTAMP")
                columns.append("update_time TIMESTAMP DEFAULT SYSTIMESTAMP")
            
            # 添加主键
            if db_type == 'mysql' or db_type == 'sqlserver':
                columns.append("PRIMARY KEY (id)")
            elif db_type == 'oracle':
                columns.append(f"CONSTRAINT {table_name}_pk PRIMARY KEY (id)")
            
            # 生成最终的SQL语句
            sql = f"CREATE TABLE {table_name} (\n"
            sql += ",\n".join(f"  {col}" for col in columns)
            sql += "\n)"
            
            # 为表添加注释
            if db_type == 'mysql':
                sql += f" COMMENT='{table_comment}';"
            elif db_type == 'sqlserver':
                sql += ";"
                sql += f"\nEXEC sp_addextendedproperty 'MS_Description', '{table_comment}', 'schema', 'dbo', 'table', '{table_name}';"
            elif db_type == 'oracle':
                sql += ";"
                sql += f"\nCOMMENT ON TABLE {table_name} IS '{table_comment}';"
            
            # 为字段添加注释（SQL Server和Oracle需要单独添加）
            if db_type == 'sqlserver':
                for i, comment in enumerate(field_comments):
                    if comment:
                        field_name = generate_field_name(i, comment)
                        sql += f"\nEXEC sp_addextendedproperty 'MS_Description', '{comment}', 'schema', 'dbo', 'table', '{table_name}', 'column', '{field_name}';"
            elif db_type == 'oracle':
                for i, comment in enumerate(field_comments):
                    if comment:
                        field_name = generate_field_name(i, comment)
                        sql += f"\nCOMMENT ON COLUMN {table_name}.{field_name} IS '{comment}';"
            
            # 执行SQL创建表
            result = db_service.execute_sql(db_type, db_config, text(sql))
            
            return jsonify({
                "success": True,
                "message": "创建表成功",
                "sql": sql,
                "result": "成功创建表及字段"
            })
            
        except Exception as e:
            app_logger.error(f"读取Excel文件失败: {str(e)}")
            return jsonify({"success": False, "message": f"读取Excel文件失败: {str(e)}"}), 500
            
    except Exception as e:
        app_logger.error(f"创建表失败: {str(e)}")
        return jsonify({"success": False, "message": f"创建表失败: {str(e)}"}), 500

@index_table_structure_bp.route('/fields/<table_name>', methods=['GET'])
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
            "message": f"获取表 {table_name} 字段成功", 
            "fields": fields
        })
    except Exception as e:
        app_logger.error(f"获取表字段失败: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"获取表 {table_name} 字段失败: {str(e)}", 
            "fields": []
        }), 500

@index_table_structure_bp.route('/create_index', methods=['POST'])
def create_index():
    """创建索引"""
    app_logger.info("创建索引请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        field_name = data.get('fieldName')
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not field_name:
            return jsonify({"success": False, "message": "字段名不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 生成索引名称
        index_name = f"idx_{table_name}_{field_name}"
        
        # 生成创建索引的SQL
        sql = f"CREATE INDEX {index_name} ON {table_name}({field_name});"
        
        # 执行SQL创建索引
        result = db_service.execute_sql(db_type, db_config, text(sql))
        
        return jsonify({
            "success": True,
            "message": "创建索引成功",
            "sql": sql
        })
        
    except Exception as e:
        app_logger.error(f"创建索引失败: {str(e)}")
        return jsonify({"success": False, "message": f"创建索引失败: {str(e)}"}), 500

@index_table_structure_bp.route('/delete_index', methods=['POST'])
def delete_index():
    """删除索引"""
    app_logger.info("删除索引请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        field_name = data.get('fieldName')
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not field_name:
            return jsonify({"success": False, "message": "字段名不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 生成索引名称
        index_name = f"idx_{table_name}_{field_name}"
        
        # 根据数据库类型生成删除索引的SQL
        if db_type == 'mysql':
            sql = f"DROP INDEX {index_name} ON {table_name};"
        elif db_type == 'sqlserver':
            sql = f"DROP INDEX {table_name}.{index_name};"
        elif db_type == 'oracle':
            sql = f"DROP INDEX {index_name};"
        else:
            sql = f"DROP INDEX {index_name};"
        
        # 执行SQL删除索引
        result = db_service.execute_sql(db_type, db_config, text(sql))
        
        return jsonify({
            "success": True,
            "message": "删除索引成功",
            "sql": sql
        })
        
    except Exception as e:
        app_logger.error(f"删除索引失败: {str(e)}")
        return jsonify({"success": False, "message": f"删除索引失败: {str(e)}"}), 500

@index_table_structure_bp.route('/generate_table_sql', methods=['POST'])
def generate_table_sql():
    """生成创建表的SQL"""
    app_logger.info("生成创建表SQL请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        table_comment = data.get('tableComment', '')
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 根据数据库类型生成不同的SQL
        sql = ''
        if db_type == 'mysql':
            sql = f"CREATE TABLE {table_name} (\n"
            sql += f"  id INT NOT NULL AUTO_INCREMENT,\n"
            sql += f"  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,\n"
            sql += f"  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n"
            sql += f"  PRIMARY KEY (id)\n"
            sql += f") COMMENT='{table_comment}';"
        elif db_type == 'sqlserver':
            sql = f"CREATE TABLE {table_name} (\n"
            sql += f"  id INT IDENTITY(1,1) NOT NULL,\n"
            sql += f"  create_time DATETIME DEFAULT GETDATE(),\n"
            sql += f"  update_time DATETIME DEFAULT GETDATE(),\n"
            sql += f"  PRIMARY KEY (id)\n"
            sql += f");\n"
            sql += f"EXEC sp_addextendedproperty 'MS_Description', '{table_comment}', 'schema', 'dbo', 'table', '{table_name}';"
        elif db_type == 'oracle':
            sql = f"CREATE TABLE {table_name} (\n"
            sql += f"  id NUMBER GENERATED ALWAYS AS IDENTITY,\n"
            sql += f"  create_time TIMESTAMP DEFAULT SYSTIMESTAMP,\n"
            sql += f"  update_time TIMESTAMP DEFAULT SYSTIMESTAMP,\n"
            sql += f"  CONSTRAINT {table_name}_pk PRIMARY KEY (id)\n"
            sql += f");\n"
            sql += f"COMMENT ON TABLE {table_name} IS '{table_comment}';"
        else:
            return jsonify({"success": False, "message": f"不支持的数据库类型: {db_type}"}), 400
        
        return jsonify({
            "success": True,
            "message": "生成SQL成功",
            "sql": sql
        })
    
    except Exception as e:
        app_logger.error(f"生成表SQL失败: {str(e)}")
        return jsonify({"success": False, "message": f"生成表SQL失败: {str(e)}"}), 500

@index_table_structure_bp.route('/generate_index_sql', methods=['POST'])
def generate_index_sql():
    """生成索引操作的SQL"""
    app_logger.info("生成索引SQL请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        field_name = data.get('fieldName')
        operation_type = data.get('operationType')  # create 或 delete
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not field_name:
            return jsonify({"success": False, "message": "字段名不能为空"}), 400
            
        if not operation_type:
            return jsonify({"success": False, "message": "操作类型不能为空"}), 400
        
        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 生成索引名称
        index_name = f"idx_{table_name}_{field_name}"
        
        # 根据操作类型和数据库类型生成SQL
        sql = ''
        if operation_type == 'create':
            sql = f"CREATE INDEX {index_name} ON {table_name}({field_name});"
        elif operation_type == 'delete':
            if db_type == 'mysql':
                sql = f"DROP INDEX {index_name} ON {table_name};"
            elif db_type == 'sqlserver':
                sql = f"DROP INDEX {table_name}.{index_name};"
            elif db_type == 'oracle':
                sql = f"DROP INDEX {index_name};"
            else:
                sql = f"DROP INDEX {index_name};"
        else:
            return jsonify({"success": False, "message": "不支持的操作类型"}), 400
        
        return jsonify({
            "success": True,
            "message": "生成SQL成功",
            "sql": sql
        })
    
    except Exception as e:
        app_logger.error(f"生成索引SQL失败: {str(e)}")
        return jsonify({"success": False, "message": f"生成索引SQL失败: {str(e)}"}), 500

@index_table_structure_bp.route('/execute_sql', methods=['POST'])
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
        
        # 暂时仅打印SQL，模拟执行
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

# 获取当前数据库信息的API
@index_table_structure_bp.route('/current_info', methods=['GET'])
def get_current_database_info():
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