"""
数据修复 API

负责处理与数据修复相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
from service.common.dify_common_service import dify_service

# 创建蓝图
index_repair_bp = Blueprint('index_repair_api', __name__, url_prefix='/api/repair')

# 创建提示词模板服务实例
template_service = PromptTemplateService()

# 创建数据库服务实例
db_service = DatabaseService()

@index_repair_bp.route('/tables', methods=['GET'])
def get_tables():
    """获取表列表"""
    app_logger.info("获取表列表")
    # 此处添加获取表列表的逻辑
    return jsonify({"message": "获取表列表成功", "tables": []})

@index_repair_bp.route('/fields/<table_name>', methods=['GET'])
def get_fields(table_name):
    """获取表字段"""
    app_logger.info(f"获取表 {table_name} 的字段")
    # 此处添加获取表字段的逻辑
    return jsonify({"message": f"获取表 {table_name} 字段成功", "fields": []})

@index_repair_bp.route('/generate_sql', methods=['POST'])
def generate_sql():
    """
    生成数据修复SQL
    请求体参数:
    - table_name: 表名
    - reference_field: 参考字段
    - target_field: 目标字段 (可选)
    - operation_type: 操作类型 (可选)
    - template_id: 模板ID (不再需要)
    """
    try:
        # 获取请求参数
        data = request.json
        app_logger.info(f"接收到数据修复SQL生成请求: {data}")

        # 参数验证
        if 'table_name' not in data or not data['table_name']:
            return jsonify({'success': False, 'message': '表名不能为空'}), 400
        
        if 'reference_field' not in data or not data['reference_field']:
            return jsonify({'success': False, 'message': '参考字段不能为空'}), 400
        
        # 参数准备
        table_name = data['table_name']
        reference_field = data['reference_field']
        target_field = data.get('target_field', '')
        operation_type = data.get('operation_type', '')
        target_comment = data.get('target_comment', '')
        
        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()

        # 调用dify服务生成SQL
        try:
            # 准备dify服务的参数
            dify_params = {
                'operation_type': operation_type,
                'table_name': table_name,
                'reference_field': reference_field,
                'target_field': target_field,
                'database_type': db_type,
                'target_field_remark': target_comment
            }
            
            app_logger.info(f"调用dify服务生成修复SQL: {dify_params}")
            
            # 根据用户请求参数选择不同的生成方法
            if data.get('use_api', True):  # 默认使用API方式
                # 使用API方式生成SQL
                app_logger.info("使用API方式生成SQL")
                result = dify_service.generate_repair_sql_via_api(dify_params)
                
                # API调用失败时直接返回错误，不使用本地生成作为备选
                if not result.get('success'):
                    app_logger.error(f"DIFY API调用失败: {result.get('message')}")
                    return jsonify({
                        'success': False,
                        'message': f"DIFY API调用失败: {result.get('message')}",
                    }), 500
            else:
                # 使用本地方式生成SQL
                app_logger.info("使用本地方式生成SQL")
                result = dify_service.generate_repair_sql(dify_params)
            
            # 检查是否有错误
            if not result.get('success'):
                app_logger.error(f"dify服务生成SQL失败: {result.get('message')}")
                return jsonify({
                    'success': False,
                    'message': f"生成SQL失败: {result.get('message')}",
                }), 500
            
            # 提取生成的内容
            generated_sql = result.get('sql', '')
            
            if generated_sql:
                return jsonify({
                    "success": True,
                    "message": "生成SQL成功",
                    "sql": generated_sql,
                    "from_llm": False  # 不再是从大模型生成
                })
            else:
                app_logger.error("dify服务返回的SQL内容为空")
                return jsonify({
                    'success': False,
                    'message': "生成的SQL内容为空",
                }), 500
                
        except Exception as e:
            app_logger.error(f"调用dify服务失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"调用dify服务失败: {str(e)}",
            }), 500

    except Exception as e:
        app_logger.error(f"生成数据修复SQL失败: {e}")
        return jsonify({'success': False, 'message': f'生成SQL失败: {str(e)}'}), 500

@index_repair_bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    """
    执行SQL语句并返回结果
    请求体参数:
    - sql: 要执行的SQL语句
    """
    app_logger.info("执行修复SQL")
    
    # 获取请求参数
    data = request.get_json()
    sql = data.get('sql')
    
    if not sql:
        return jsonify({"message": "SQL语句不能为空", "success": False}), 400
    
    try:
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 分割多条SQL语句（以分号作为分隔符，忽略注释中的分号）
        sql_statements = split_sql_statements(sql)
        app_logger.info(f"SQL语句拆分为 {len(sql_statements)} 条语句")
        
        # 逐条执行SQL语句
        executed_count = 0
        total_count = len(sql_statements)
        total_affected_rows = 0
        last_result = None
        error_message = None
        
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if not statement:  # 跳过空语句
                continue
                
            app_logger.info(f"执行第 {i+1}/{total_count} 条SQL语句: {statement[:100]}...")
            
            try:
                # 执行单条SQL
                from sqlalchemy import text
                result = db_service.execute_sql(db_type, db_config, text(statement))
                
                # 更新统计信息
                executed_count += 1
                if not result.get('is_query', False):
                    total_affected_rows += result.get('affected_rows', 0)
                
                # 保存最后一条执行成功的结果
                last_result = result
                
            except Exception as e:
                # 记录错误并停止执行
                error_message = f"执行第 {i+1} 条SQL语句时出错: {str(e)}"
                app_logger.error(error_message)
                break
        
        # 判断操作类型
        operation_type = ""
        if "日期" in sql or "date" in sql.lower():
            operation_type = "repair_date"
        elif "身份证" in sql or "idcard" in sql.lower():
            operation_type = "repair_idcard"
        
        # 构造执行结果
        if error_message:
            # 有错误发生
            return jsonify({
                'success': False,
                'message': error_message,
                'executed_count': executed_count,
                'total_count': total_count,
                'total_affected_rows': total_affected_rows
            }), 500
        elif last_result and last_result.get('is_query', False):
            # 最后执行的是查询语句，返回查询结果
            rows = last_result.get('rows', [])
            data = []
            for row in rows:
                data.append(list(row))
            
            app_logger.info(f"查询结果行数: {len(data)}")
            
            return jsonify({
                'success': True,
                'is_query': True,
                'headers': last_result.get('headers', []),
                'rows': data,
                'row_count': len(data),
                'execution_time': last_result.get('execution_time', ''),
                'executed_count': executed_count,
                'total_count': total_count
            })
        else:
            # 非查询语句，或混合语句，返回影响行数
            return jsonify({
                'success': True,
                'is_query': False,
                'affected_rows': total_affected_rows,
                'message': f'操作成功完成，执行了 {executed_count}/{total_count} 条SQL语句，影响了 {total_affected_rows} 行数据',
                'operation_type': operation_type,
                'execution_time': last_result.get('execution_time', '') if last_result else '',
                'executed_count': executed_count,
                'total_count': total_count
            })
    except Exception as e:
        app_logger.error(f"执行SQL失败: {e}")
        return jsonify({'success': False, 'message': f'执行SQL失败: {str(e)}'}), 500

def split_sql_statements(sql_text):
    """
    将包含多个SQL语句的文本拆分为单独的SQL语句列表
    处理SQL中的注释和字符串，避免错误拆分
    
    Args:
        sql_text: 包含一个或多个SQL语句的文本
        
    Returns:
        list: SQL语句列表
    """
    if not sql_text:
        return []
    
    # 简单的SQL拆分，以分号为界
    # 注意：这个实现比较简单，无法处理所有特殊情况（如字符串中的分号、存储过程等）
    # 如果需要更复杂的处理，应考虑使用专业的SQL解析器
    
    statements = []
    current_statement = ""
    in_single_quote = False
    in_double_quote = False
    in_comment = False
    i = 0
    
    while i < len(sql_text):
        char = sql_text[i]
        next_char = sql_text[i+1] if i+1 < len(sql_text) else ""
        
        # 处理注释
        if char == '-' and next_char == '-' and not in_single_quote and not in_double_quote:
            in_comment = True
            current_statement += char
            i += 1
            continue
        
        # 处理行注释结束
        if in_comment and (char == '\n' or char == '\r'):
            in_comment = False
            current_statement += char
            i += 1
            continue
        
        # 处理引号
        if char == "'" and not in_comment and not in_double_quote:
            in_single_quote = not in_single_quote
            current_statement += char
            i += 1
            continue
            
        if char == '"' and not in_comment and not in_single_quote:
            in_double_quote = not in_double_quote
            current_statement += char
            i += 1
            continue
        
        # 处理分号 - 只有在不在引号和注释中时才视为分隔符
        if char == ';' and not in_single_quote and not in_double_quote and not in_comment:
            current_statement += char
            statements.append(current_statement.strip())
            current_statement = ""
            i += 1
            continue
        
        # 添加当前字符
        current_statement += char
        i += 1
    
    # 处理最后一个语句（如果没有分号结尾）
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    return statements 