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
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService

# 创建蓝图
index_table_structure_bp = Blueprint('index_table_structure_api', __name__, url_prefix='/api/table_structure')

# 实例化数据库服务
db_service = DatabaseService()

# 实例化模板服务
template_service = PromptTemplateService()

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
        # 将索引从0开始调整为从1开始
        adjusted_index = column_index + 1
        
        # 移除非中英文字符
        clean_comment = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', comment)
        
        # 判断是否是空的
        if not clean_comment:
            # 如果注释为空或只包含特殊字符，使用默认名称
            return f"t_{adjusted_index}_field"
        
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
        return f"t_{adjusted_index}_{result}"
    except Exception as e:
        app_logger.error(f"生成字段名失败: {str(e)}")
        # 返回安全的默认名称
        return f"t_{adjusted_index}_field"

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
        sheet_id = data.get('sheetId')
        comment_row = int(data.get('commentRow', 1))
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not excel_path:
            return jsonify({"success": False, "message": "Excel文件路径不能为空"}), 400
            
        if not sheet_id:
            return jsonify({"success": False, "message": "工作表不能为空"}), 400
        
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 读取Excel文件中的字段注释行
        try:
            rows = ExcelUtil.read_excel_data(
                file_path=excel_path,
                sheet_name=sheet_id,
                start_row=comment_row - 1,  # 行号从0开始，需要减1
                row_limit=1
            )
            
            if not rows or len(rows) == 0:
                return jsonify({"success": False, "message": "Excel文件中未找到备注信息行"}), 400
                
            field_comments = rows[0]  # 获取字段注释行
            
            # 生成创建表的SQL
            columns = []
            
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
    """生成创建表的SQL，直接在后端拼接SQL而不调用AI模型"""
    app_logger.info("生成创建表SQL请求")
    
    try:
        # 1. 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        table_comment = data.get('tableComment', '')
        excel_path = data.get('excelPath')
        sheet_id = data.get('sheetId')
        comment_row = data.get('commentRow')
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 2. 读取Excel获取字段备注信息
        field_comments = []
        if excel_path and sheet_id and comment_row:
            try:
                # 将comment_row转为整数
                comment_row_num = int(comment_row)
                
                # 先解析sheet_id，获取正确的sheet_name和sheet_index
                sheet_name, sheet_index = ExcelUtil.parse_sheet_id(sheet_id)
                
                # 读取Excel中的字段备注行
                rows = ExcelUtil.read_excel_data(
                    file_path=excel_path,
                    sheet_name=sheet_name,
                    sheet_index=sheet_index,
                    start_row=comment_row_num - 1,  # 行号从0开始，需要减1
                    row_limit=1
                )
                
                if rows and len(rows) > 0:
                    # 过滤空值并获取字段备注
                    field_comments = [comment for comment in rows[0] if comment]
            except Exception as e:
                app_logger.error(f"读取Excel文件失败: {str(e)}")
                return jsonify({"success": False, "message": f"读取Excel文件失败: {str(e)}"}), 500
        
        # 3. 根据数据库类型直接拼接SQL
        sql = ""
        
        # 根据数据库类型选择不同的SQL语法
        if db_type == 'mysql':
            sql = generate_mysql_table_sql(table_name, table_comment, field_comments)
        elif db_type == 'sqlserver':
            sql = generate_sqlserver_table_sql(table_name, table_comment, field_comments)
        elif db_type == 'oracle':
            sql = generate_oracle_table_sql(table_name, table_comment, field_comments)
        else:
            # 默认使用MySQL语法
            sql = generate_mysql_table_sql(table_name, table_comment, field_comments)
        
        return jsonify({
            "success": True,
            "message": "生成SQL成功",
            "sql": sql
        })
    
    except Exception as e:
        app_logger.error(f"生成表SQL失败: {str(e)}")
        return jsonify({"success": False, "message": f"生成表SQL失败: {str(e)}"}), 500

def generate_mysql_table_sql(table_name, table_comment, field_comments):
    """生成MySQL表创建SQL
    
    Args:
        table_name (str): 表名
        table_comment (str): 表备注
        field_comments (list): 字段备注列表
        
    Returns:
        str: 生成的MySQL表创建SQL
    """
    # 生成创建表的SQL
    sql = f"CREATE TABLE {table_name} (\n"
    
    # 字段数量计数
    field_count = 0
    
    # 为每个字段备注生成对应的字段
    for i, comment in enumerate(field_comments):
        if comment:  # 只处理非空注释
            field_name = generate_field_name(i, comment)
            sql += f"  {field_name} VARCHAR(100) COMMENT '{comment}'"
            field_count += 1
            
            # 先添加逗号，后面可能还有补充字段
            sql += ",\n"
    
    # 添加5个补充字段，从字段数量+1开始
    start_index = field_count + 1
    for i in range(5):
        field_num = start_index + i
        field_name = f"t_{field_num}"
        field_comment = f"补充字段{field_num}"
        
        sql += f"  {field_name} VARCHAR(100) COMMENT '{field_comment}'"
        
        # 如果不是最后一个补充字段，添加逗号
        if i < 4:
            sql += ",\n"
        else:
            sql += "\n"
    
    # 结束表定义
    sql += f") COMMENT='{table_comment}';"
    
    return sql

def generate_sqlserver_table_sql(table_name, table_comment, field_comments):
    """生成SQL Server表创建SQL
    
    Args:
        table_name (str): 表名
        table_comment (str): 表备注
        field_comments (list): 字段备注列表
        
    Returns:
        str: 生成的SQL Server表创建SQL
    """
    # 生成创建表的SQL
    sql = f"CREATE TABLE {table_name} (\n"
    
    # 标志位，用于控制是否需要添加逗号
    first_field = True
    field_count = 0
    
    # 为每个字段备注生成对应的字段
    for i, comment in enumerate(field_comments):
        if comment:  # 只处理非空注释
            field_name = generate_field_name(i, comment)
            field_count += 1
            
            if first_field:
                sql += f"  {field_name} NVARCHAR(100)"
                first_field = False
            else:
                sql += f",\n  {field_name} NVARCHAR(100)"
    
    # 添加5个补充字段，从字段数量+1开始
    start_index = field_count + 1
    for i in range(5):
        field_num = start_index + i
        field_name = f"t_{field_num}"
        field_comment = f"补充字段{field_num}"
        
        sql += f",\n  {field_name} NVARCHAR(100)"
    
    # 结束表定义
    sql += "\n);\n"
    
    # 为表添加注释
    sql += f"EXEC sp_addextendedproperty 'MS_Description', '{table_comment}', 'schema', 'dbo', 'table', '{table_name}';\n"
    
    # 为字段添加注释
    for i, comment in enumerate(field_comments):
        if comment:
            field_name = generate_field_name(i, comment)
            sql += f"EXEC sp_addextendedproperty 'MS_Description', '{comment}', 'schema', 'dbo', 'table', '{table_name}', 'column', '{field_name}';\n"
    
    # 为补充字段添加注释
    start_index = field_count + 1
    for i in range(5):
        field_num = start_index + i
        field_name = f"t_{field_num}"
        field_comment = f"补充字段{field_num}"
        
        sql += f"EXEC sp_addextendedproperty 'MS_Description', '{field_comment}', 'schema', 'dbo', 'table', '{table_name}', 'column', '{field_name}';\n"
    
    return sql

def generate_oracle_table_sql(table_name, table_comment, field_comments):
    """生成Oracle表创建SQL
    
    Args:
        table_name (str): 表名
        table_comment (str): 表备注
        field_comments (list): 字段备注列表
        
    Returns:
        str: 生成的Oracle表创建SQL
    """
    # 生成创建表的SQL
    sql = f"CREATE TABLE {table_name} (\n"
    
    # 标志位，用于控制是否需要添加逗号
    first_field = True
    field_count = 0
    
    # 为每个字段备注生成对应的字段
    for i, comment in enumerate(field_comments):
        if comment:  # 只处理非空注释
            field_name = generate_field_name(i, comment)
            field_count += 1
            
            if first_field:
                sql += f"  {field_name} VARCHAR2(100)"
                first_field = False
            else:
                sql += f",\n  {field_name} VARCHAR2(100)"
    
    # 添加5个补充字段，从字段数量+1开始
    start_index = field_count + 1
    for i in range(5):
        field_num = start_index + i
        field_name = f"t_{field_num}"
        field_comment = f"补充字段{field_num}"
        
        sql += f",\n  {field_name} VARCHAR2(100)"
    
    # 结束表定义
    sql += "\n);\n"
    
    # 为表添加注释
    sql += f"COMMENT ON TABLE {table_name} IS '{table_comment}';\n"
    
    # 为字段添加注释
    for i, comment in enumerate(field_comments):
        if comment:
            field_name = generate_field_name(i, comment)
            sql += f"COMMENT ON COLUMN {table_name}.{field_name} IS '{comment}';\n"
    
    # 为补充字段添加注释
    start_index = field_count + 1
    for i in range(5):
        field_num = start_index + i
        field_name = f"t_{field_num}"
        field_comment = f"补充字段{field_num}"
        
        sql += f"COMMENT ON COLUMN {table_name}.{field_name} IS '{field_comment}';\n"
    
    return sql

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
        template_id = data.get('templateId')  # 新增模板ID参数
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not field_name:
            return jsonify({"success": False, "message": "字段名不能为空"}), 400
            
        if not operation_type:
            return jsonify({"success": False, "message": "操作类型不能为空"}), 400
            
        # 验证模板ID
        if not template_id:
            return jsonify({"success": False, "message": "提示词模板不能为空"}), 400
        
        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 调用默认模型服务生成SQL
        try:
            # 导入模型服务
            from service.common.model_common_service import model_service
            
            # 获取默认模型信息
            default_model = model_service.get_default_model()
            if not default_model:
                app_logger.error("没有找到默认模型配置")
                raise Exception("没有找到默认模型配置，请先设置默认模型")
            
            # 获取模型服务提供商ID和模型ID
            provider_id = default_model.get('provider_id')
            model_id = default_model.get('id')
            model_name = default_model.get('name', '').lower()
            
            app_logger.info(f"使用默认模型生成索引SQL: 提供商 {provider_id}, 模型 {model_id}")
            
            # 3. 获取提示词模板
            system_prompt = ""
            user_prompt_template = ""
            
            if template_id:
                try:
                    # 使用模板服务获取模板内容
                    template = template_service.load_template_from_file(template_id)
                    
                    if not template:
                        error_msg = f"未找到ID为 {template_id} 的模板"
                        app_logger.error(error_msg)
                        return jsonify({"success": False, "message": error_msg}), 404
                    
                    # 解析模板内容
                    import json
                    template_content = json.loads(template.get('content', '{}'))
                    
                    system_prompt = template_content.get('system', '')
                    user_prompt_template = template_content.get('user', '')
                    
                    # 如果模板中没有包含必要的提示词，则使用默认提示词
                    if not user_prompt_template:
                        app_logger.warning("所选模板未包含用户提示词，使用默认提示词")
                        user_prompt_template = """请生成为数据库表创建或删除索引的SQL语句。
                        
表名：{table_name}
字段名：{field_name}
操作类型：{operation_type}（create表示创建索引，delete表示删除索引）
数据库类型：{db_type}

请仅返回SQL语句，不要包含任何其他文字说明。"""
                        
                except Exception as e:
                    error_msg = f"获取提示词模板失败: {str(e)}"
                    app_logger.error(error_msg)
                    return jsonify({"success": False, "message": error_msg}), 500
            
            # 组装新的用户提示词
            base_prompt = f"{user_prompt_template}\n\n表名：{table_name}\n字段名：{field_name}\n操作类型：{operation_type}\n数据库类型：{db_type}"
            
            # 判断是否为Qwen3模型，如果是则添加/no_think
            if 'qwen3' in model_id.lower() or 'qwen3' in model_name:
                user_prompt = f"{base_prompt} /no_think"
                app_logger.info("检测到Qwen3模型，添加/no_think指令")
            else:
                user_prompt = base_prompt
                app_logger.info(f"非Qwen3模型({model_id})，不添加/no_think指令")
            
            # 如果系统提示词为空，使用默认系统提示词
            if not system_prompt:
                system_prompt = "你是一位专业的数据库专家，精通各种数据库系统（MySQL、SQL Server、Oracle等）的SQL语法。请根据用户的需求生成准确无误的SQL语句，仅返回SQL代码，不要包含任何多余的解释。"
            
            # 准备消息格式
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 参数
            options = {
                "temperature": 0.1
            }
            
            # 调用模型
            result = model_service.chat_completion(provider_id, model_id, messages, options)
            
            # 检查是否有错误
            if "error" in result:
                app_logger.error(f"模型生成SQL失败: {result.get('error')}")
                raise Exception(f"模型生成SQL失败: {result.get('error')}")
            
            # 提取生成的内容
            generated_sql = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if generated_sql:
                return jsonify({
                    "success": True,
                    "message": "生成SQL成功",
                    "sql": generated_sql,
                    "from_llm": True
                })
            else:
                app_logger.error("模型返回的SQL内容为空")
                raise Exception("模型返回的SQL内容为空")
                
        except Exception as e:
            app_logger.error(f"调用默认模型失败: {str(e)}")
            # 直接返回错误，不使用后备方案
            return jsonify({
                "success": False,
                "message": f"生成索引SQL失败: {str(e)}"
            }), 500
    
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

@index_table_structure_bp.route('/read_excel_row', methods=['GET'])
def read_excel_row():
    """读取Excel文件的指定行
    
    Query Parameters:
        file_path: Excel文件路径
        sheet_name: 工作表名称或ID
        row_index: 要读取的行索引（从0开始）
        
    Returns:
        JSON: 包含行数据的JSON对象
    """
    app_logger.info("请求读取Excel文件行数据")
    
    try:
        # 获取请求参数
        file_path = request.args.get('file_path')
        sheet_name = request.args.get('sheet_name')
        row_index = request.args.get('row_index')
        
        # 参数验证
        if not file_path:
            return jsonify({"success": False, "message": "未指定Excel文件路径"}), 400
        
        if row_index is None:
            return jsonify({"success": False, "message": "未指定行索引"}), 400
        
        # 转换行索引为整数
        row_index = int(row_index)
        
        # 验证Excel文件路径
        if not ExcelUtil.validate_excel_path(file_path):
            return jsonify({"success": False, "message": f"无效的Excel文件路径: {file_path}"}), 400
        
        # 解析sheet_id，可能是"name:index"或仅索引
        sheet_name_parsed, sheet_index = ExcelUtil.parse_sheet_id(sheet_name)
        
        # 读取指定行的数据
        rows = ExcelUtil.read_excel_data(
            file_path=file_path,
            sheet_name=sheet_name_parsed,
            sheet_index=sheet_index,
            start_row=row_index,
            row_limit=1
        )
        
        if not rows or len(rows) == 0:
            return jsonify({
                "success": False,
                "message": f"指定的行 {row_index} 不存在或为空"
            }), 404
        
        # 返回行数据
        return jsonify({
            "success": True,
            "data": rows[0]
        })
        
    except Exception as e:
        app_logger.error(f"读取Excel行数据失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"读取Excel行数据失败: {str(e)}"
        }), 500 