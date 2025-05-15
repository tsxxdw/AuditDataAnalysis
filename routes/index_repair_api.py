"""
数据修复 API

负责处理与数据修复相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService
from utils.database_config_util import DatabaseConfigUtil
from service.database.database_service import DatabaseService
import json

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
    - template_id: 模板ID
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
        
        if 'template_id' not in data or not data['template_id']:
            return jsonify({'success': False, 'message': '模板ID不能为空'}), 400

        # 参数准备
        table_name = data['table_name']
        reference_field = data['reference_field']
        target_field = data.get('target_field', '')
        operation_type = data.get('operation_type', '')
        template_id = data['template_id']
        
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
            
            app_logger.info(f"使用默认模型生成修复SQL: 提供商 {provider_id}, 模型 {model_id}")
            
            # 获取提示词模板
            system_prompt = ""
            user_prompt_template = ""
            
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
                
            except Exception as e:
                error_msg = f"获取提示词模板失败: {str(e)}"
                app_logger.error(error_msg)
                return jsonify({"success": False, "message": error_msg}), 500
            
            # 组装新的用户提示词
            base_prompt = f"{user_prompt_template}\n\n表名：{table_name}\n参考字段：{reference_field}\n数据库类型：{db_type}"
            
            # 添加可选参数
            if target_field:
                base_prompt += f"\n目标字段：{target_field}"
            if operation_type:
                base_prompt += f"\n操作类型：{operation_type}"
            
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
            
            # 尝试使用预定义的SQL作为后备方案
            app_logger.info("使用预定义SQL作为后备方案")
            basic_sql = generate_basic_sql(table_name, reference_field, target_field, operation_type)
            
            return jsonify({
                'success': True,
                'sql': basic_sql,
                'from_llm': False,
                'fallback_reason': str(e)
            })

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
        
        # 执行SQL
        from sqlalchemy import text
        result = db_service.execute_sql(db_type, db_config, text(sql))
        
        # 判断操作类型
        operation_type = ""
        if "日期" in sql or "date" in sql.lower():
            operation_type = "repair_date"
        elif "身份证" in sql or "idcard" in sql.lower():
            operation_type = "repair_idcard"
        
        # 构造执行结果
        if result.get('is_query', False):
            # 查询语句，使用实际查询结果
            rows = result.get('rows', [])
            # 将行转换为列表
            data = []
            for row in rows:
                data.append(list(row))
            
            app_logger.info(f"查询结果行数: {len(data)}")
            
            # 获取表头
            headers = result.get('headers', [])
            
            # 返回查询结果
            return jsonify({
                'success': True,
                'is_query': True,
                'headers': headers,
                'rows': data,
                'row_count': len(data),
                'execution_time': result.get('execution_time', '')
            })
        else:
            # 非查询语句，返回影响行数
            affected_rows = result.get('affected_rows', 0)
            
            return jsonify({
                'success': True,
                'is_query': False,
                'affected_rows': affected_rows,
                'message': f'操作成功完成，影响了 {affected_rows} 行数据',
                'operation_type': operation_type,
                'execution_time': result.get('execution_time', '')
            })
    except Exception as e:
        app_logger.error(f"执行SQL失败: {e}")
        return jsonify({'success': False, 'message': f'执行SQL失败: {str(e)}'}), 500

def generate_basic_sql(table_name, reference_field, target_field, operation_type):
    """
    根据参数生成基本的SQL语句（当大模型调用失败时使用）
    """
    sql = ''
    
    if operation_type == 'repair_date':
        sql = f"-- 日期类型修复\n"
        sql += f"UPDATE {table_name} SET {reference_field} = \n"
        sql += f"  CASE \n"
        sql += f"    WHEN LENGTH({reference_field}) = 8 THEN \n"
        sql += f"      SUBSTR({reference_field}, 1, 4) || '-' || SUBSTR({reference_field}, 5, 2) || '-' || SUBSTR({reference_field}, 7, 2) \n"
        sql += f"    WHEN LENGTH({reference_field}) = 10 AND INSTR({reference_field}, '/') > 0 THEN \n"
        sql += f"      REPLACE({reference_field}, '/', '-') \n"
        sql += f"    ELSE {reference_field} \n"
        sql += f"  END \n"
        sql += f"WHERE {reference_field} IS NOT NULL;"
    elif operation_type == 'repair_idcard':
        sql = f"-- 身份证修复\n"
        sql += f"UPDATE {table_name} SET {reference_field} = \n"
        sql += f"  CASE \n"
        sql += f"    WHEN LENGTH({reference_field}) = 15 THEN \n"
        sql += f"      -- 15位转18位身份证算法\n"
        sql += f"      CONCAT(SUBSTR({reference_field}, 1, 6), '19', SUBSTR({reference_field}, 7, 9)) \n"
        sql += f"    WHEN LENGTH({reference_field}) = 18 THEN {reference_field} \n"
        sql += f"    ELSE {reference_field} \n"
        sql += f"  END \n"
        sql += f"WHERE {reference_field} IS NOT NULL;"
    else:
        # 默认生成一个查询sql
        sql = f"SELECT * FROM {table_name} WHERE {reference_field} IS NOT NULL LIMIT 10;"
    
    return sql 