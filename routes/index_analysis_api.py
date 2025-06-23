"""
数据分析 API

负责处理与数据分析相关的API请求
"""

import os
import json
from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService
from sqlalchemy import text
from service.exception import AppException

# 从通用数据库API模块导入相关函数
from routes.common.common_database_api import get_fields as common_get_fields
from routes.common.common_database_api import get_tables as common_get_tables
from routes.common.common_database_api import db_service as common_db_service

# 导入模型服务
from service.common.model_common_service import model_service
from service.common.model.model_chat_common_service import model_chat_service
from utils.settings.model_config_util import modelConfigUtil  # 添加导入

# 创建蓝图
index_analysis_bp = Blueprint('index_analysis_api', __name__, url_prefix='/api/analysis')

# 实例化数据库服务
db_service = DatabaseService()

# 实例化模板服务
template_service = PromptTemplateService()

@index_analysis_bp.route('/get_tables', methods=['GET'])
def get_tables():
    """获取数据库中的表列表 - 直接使用通用数据库API模块的功能"""
    app_logger.info("请求获取数据库表列表")
    # 调用通用数据库API模块的获取表函数
    return common_get_tables()

@index_analysis_bp.route('/get_table_fields', methods=['GET'])
def get_table_fields():
    """获取表的字段列表 - 间接使用通用数据库API模块的功能"""
    app_logger.info("请求获取表字段列表")

    try:
        # 获取请求参数
        table_name = request.args.get('table_name')

        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
            
        # 调用通用数据库API模块的获取字段函数
        # 创建一个仿造的请求对象来传递table_name参数
        class MockRequest:
            def __init__(self, table_name):
                self.view_args = {'table_name': table_name}
                
        # 临时保存原始请求
        original_request = request
        
        # 模拟请求对象
        mock_request = MockRequest(table_name)
        
        # 手动调用get_fields函数
        from flask import g
        g.request = mock_request
        result = common_get_fields(table_name)
        g.request = original_request
        
        return result
        
    except Exception as e:
        app_logger.error(f"获取字段列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取字段列表失败: {str(e)}"
        }), 500

@index_analysis_bp.route('/database_types', methods=['GET'])
def get_database_types():
    """获取数据库类型列表"""
    app_logger.info("获取数据库类型列表")
    # 此处添加获取数据库类型列表的逻辑
    return jsonify({"message": "获取数据库类型列表成功", "types": ["MySQL", "SQL Server", "Oracle"]})

@index_analysis_bp.route('/sql_templates', methods=['GET'])
def get_sql_templates():
    """获取SQL模板列表"""
    app_logger.info("获取SQL模板列表")
    # 此处添加获取SQL模板列表的逻辑
    return jsonify({"message": "获取SQL模板列表成功", "templates": []})

@index_analysis_bp.route('/add_template', methods=['POST'])
def add_template():
    """添加SQL模板"""
    app_logger.info("添加SQL模板")
    # 此处添加添加SQL模板的逻辑
    return jsonify({"message": "添加SQL模板成功", "template_id": ""})

@index_analysis_bp.route('/generate_sql', methods=['POST'])
def generate_sql():
    """生成SQL查询语句"""
    app_logger.info("请求生成SQL查询语句")
    
    try:
        # 获取请求参数
        data = request.json
        template_id = data.get('template_id')
        tables = data.get('tables', [])
        date_compare_type = data.get('date_compare_type', 'year')  # 获取日期对比方式，默认为'year'
        
        # 参数验证
        if not template_id:
            return jsonify({"success": False, "message": "模板ID不能为空"}), 400
        
        if not tables or len(tables) == 0:
            return jsonify({"success": False, "message": "至少需要选择一个表和字段"}), 400
        
        # 获取默认数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 获取数据库连接信息
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        if not db_config:
            return jsonify({"success": False, "message": f"获取{db_type}数据库配置失败"}), 500
        
        # 调用默认模型服务生成SQL
        try:
            # 获取模型服务提供商ID和模型ID
            default_model_info = modelConfigUtil.get_default_model_info()
            if not default_model_info:
                app_logger.error("没有找到默认模型配置")
                raise Exception("没有找到默认模型配置，请先设置默认模型")
            
            provider_id = default_model_info.get('provider_id')
            model_id = default_model_info.get('model_id')
            
            # 获取模型名称，可能在model_details中
            if 'model_details' in default_model_info and default_model_info['model_details']:
                model_name = default_model_info['model_details'].get('name', '').lower()
            else:
                model_name = ''
            
            app_logger.info(f"使用默认模型生成分析SQL: 提供商 {provider_id}, 模型 {model_id}")
            
            # 获取提示词模板
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
                        user_prompt_template = """请基于下面提供的表和字段信息生成SQL查询语句。

请仅返回SQL语句，不要包含任何其他文字说明。
                        """
                        
                except Exception as e:
                    error_msg = f"获取提示词模板失败: {str(e)}"
                    app_logger.error(error_msg)
                    return jsonify({"success": False, "message": error_msg}), 500
            
            # 构建提示词中的表和字段信息
            tables_info = []
            for i, table in enumerate(tables):
                table_name = table.get('name', '')
                fields = table.get('fields', [])
                
                if table_name and fields:
                    fields_info = []
                    for field in fields:
                        field_name = field.get('name', '')
                        field_type = field.get('type', '').lower()
                        field_comment = field.get('comment', '')
                        
                        if field_name:
                            # 包含字段名、类型和注释信息
                            field_info = f"{field_name} ({field_type})"
                            if field_comment:
                                field_info += f" - {field_comment}"
                            fields_info.append(field_info)
                    
                    tables_info.append(f"表{i+1}: {table_name}\n字段: {', '.join(fields_info)}")
            
            tables_info_text = "\n".join(tables_info)
            
            # 组装用户提示词
            base_prompt = f"{user_prompt_template}\n\n数据库类型: {db_type}\n日期对比方式: {date_compare_type}\n\n选择的表和字段:\n{tables_info_text}"
            
            # 判断是否为Qwen3模型，如果是则添加/no_think
            if 'qwen3' in model_id.lower() or 'qwen3' in model_name:
                user_prompt = f"{base_prompt} /no_think"
                app_logger.info("检测到Qwen3模型，添加/no_think指令")
            else:
                user_prompt = base_prompt
                app_logger.info(f"非Qwen3模型({model_id})，不添加/no_think指令")
            
            # 准备消息格式
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 参数
            options = {
                "temperature": 0.2
            }
            
            # 调用模型
            result = model_chat_service.chat_completion(provider_id, model_id, messages, options)
            
            # 检查是否有错误
            if "error" in result:
                app_logger.error(f"模型生成SQL失败: {result.get('error')}")
                raise Exception(f"模型生成SQL失败: {result.get('error')}")
            
            # 提取生成的内容
            generated_sql = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if generated_sql:
                # 返回生成的SQL
                return jsonify({
                    "success": True,
                    "message": "SQL生成成功",
                    "sql": generated_sql,
                    "from_llm": True
                })
            else:
                app_logger.error("模型返回的SQL内容为空")
                raise Exception("模型返回的SQL内容为空")
                
        except Exception as e:
            app_logger.error(f"调用默认模型生成SQL失败: {str(e)}")
            # 如果调用模型失败，使用备用方式生成SQL
            app_logger.info("使用备用方式生成SQL")
            
            # 获取模板信息
            template_info = template_service.load_template_from_file(template_id)
            if not template_info:
                return jsonify({"success": False, "message": "获取模板信息失败"}), 500
            
            # 构建生成SQL的上下文
            context = {
                "database_type": db_type,
                "tables": tables,
                "date_compare_type": date_compare_type,
                "template": template_info
            }
            
            # 使用模板生成SQL
            sql = generate_sample_sql(context)
            
            # 返回生成的SQL
            return jsonify({
                "success": True,
                "message": "SQL生成成功（备用方式）",
                "sql": sql,
                "from_llm": False
            })
            
    except Exception as e:
        app_logger.error(f"生成SQL失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"生成SQL失败: {str(e)}"
        }), 500

@index_analysis_bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    """执行SQL查询"""
    app_logger.info("请求执行SQL查询")
    
    try:
        # 获取请求参数
        data = request.json
        sql = data.get('sql')
        
        # 参数验证
        if not sql or not sql.strip():
            return jsonify({"success": False, "message": "SQL语句不能为空"}), 400
        
        # 获取默认数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 获取数据库连接信息
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        if not db_config:
            return jsonify({"success": False, "message": f"获取{db_type}数据库配置失败"}), 500
        
        # 使用数据库服务执行SQL
        engine = db_service.get_database_engine(db_type, db_config)
        
        try:
            with engine.connect() as connection:
                # 执行SQL并获取结果
                result = connection.execute(text(sql))
                
                # 获取列名
                columns = result.keys()
                
                # 获取所有行
                rows = result.fetchall()
                
                # 转换为二维数组
                result_data = {
                    "columns": list(columns),
                    "rows": [list(row) for row in rows]
                }
                
                return jsonify({
                    "success": True,
                    "message": "SQL执行成功",
                    "data": result_data
                })
        except Exception as e:
            app_logger.error(f"执行SQL错误: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"执行SQL错误: {str(e)}"
            }), 400
    except Exception as e:
        app_logger.error(f"执行SQL请求失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"执行SQL请求失败: {str(e)}"
        }), 500

def generate_sample_sql(context):
    """
    生成示例SQL（实际项目中可替换为AI生成或更复杂的逻辑）
    
    Args:
        context (dict): 生成SQL的上下文信息
        
    Returns:
        str: 生成的SQL语句
    """
    db_type = context.get('database_type', 'mysql')
    tables = context.get('tables', [])
    date_compare_type = context.get('date_compare_type', 'year')  # 获取日期对比方式
    
    if not tables:
        return "-- 未选择表和字段"
    
    # 获取第一个表和字段
    main_table = tables[0]
    table_name = main_table.get('name', '')
    fields = main_table.get('fields', [])
    
    if not fields:
        return f"-- 表 {table_name} 未选择字段"
    
    # 构建字段列表
    field_list = []
    date_fields = []  # 用于保存日期类型字段
    for field in fields:
        field_name = field.get('name', '')
        field_type = field.get('type', '').lower()
        
        if field_name:
            field_list.append(f"{table_name}.{field_name}")
            
            # 识别日期类型字段用于示例
            if 'date' in field_type or 'time' in field_type:
                date_fields.append(field_name)
    
    field_str = ", ".join(field_list) if field_list else "*"
    
    # 添加日期对比方式相关的注释
    date_format_comment = f"-- 使用的日期对比方式: {date_compare_type}\n"
    
    # 根据日期对比方式添加示例SQL注释，优先使用实际的日期字段
    date_example = ""
    date_column = date_fields[0] if date_fields else "date_column"
    
    if date_compare_type == '年':
        date_example = f"-- 例如: YEAR({table_name}.{date_column}) = 2023"
    elif date_compare_type == '年月':
        date_example = f"-- 例如: DATE_FORMAT({table_name}.{date_column}, '%Y-%m') = '2023-06'"
    elif date_compare_type == '年月日':
        date_example = f"-- 例如: DATE({table_name}.{date_column}) = '2023-06-15'"
    
    # 根据表的数量生成不同类型的SQL
    if len(tables) == 1:
        # 单表查询
        sql = f"{date_format_comment}{date_example}\n\nSELECT {field_str}\nFROM {table_name}"
        
        # 添加适当的LIMIT语句
        if db_type == 'mysql':
            sql += "\nLIMIT 100"
        elif db_type == 'sqlserver':
            sql = f"SELECT TOP 100 {field_str}\nFROM {table_name}"
        elif db_type == 'oracle':
            sql = f"SELECT {field_str}\nFROM {table_name}\nWHERE ROWNUM <= 100"
    else:
        # 多表关联查询
        sql = f"SELECT {field_str}"
        
        # 添加第一个表
        sql += f"\nFROM {table_name}"
        
        # 处理其他表的关联
        for i in range(1, len(tables)):
            join_table = tables[i]
            join_table_name = join_table.get('name', '')
            join_fields = join_table.get('fields', [])
            
            if join_table_name and join_fields:
                # 简单假设表之间通过id字段关联
                sql += f"\nLEFT JOIN {join_table_name} ON {table_name}.id = {join_table_name}.id"
                
                # 添加选择的字段
                for field in join_fields:
                    field_name = field.get('name', '')
                    if field_name:
                        field_list.append(f"{join_table_name}.{field_name}")
        
        # 重新构建字段列表字符串
        field_str = ", ".join(field_list)
        
        # 更新SELECT语句中的字段列表
        sql = sql.replace(sql.split('\n')[0], f"SELECT {field_str}")
        
        # 添加适当的LIMIT语句
        if db_type == 'mysql':
            sql += "\nLIMIT 100"
        elif db_type == 'sqlserver':
            # 对于SQL Server，需要重写整个查询
            new_field_str = field_str
            from_part = sql.split('\nFROM')[1]
            sql = f"SELECT TOP 100 {new_field_str}\nFROM{from_part}"
        elif db_type == 'oracle':
            sql += "\nAND ROWNUM <= 100"
    
    return sql 