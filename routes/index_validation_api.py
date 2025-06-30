"""
数据校验 API

负责处理与数据校验相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService
from utils.database_config_util import DatabaseConfigUtil
from sqlalchemy import text
from service.database.database_service import DatabaseService
from service.common.model.model_chat_common_service import model_chat_service
from utils.settings.model_config_util import modelConfigUtil
from service.session_service import session_service

# 创建蓝图
index_validation_bp = Blueprint('index_validation_api', __name__, url_prefix='/api/validation')

# 创建提示词模板服务实例
template_service = PromptTemplateService()

# 创建数据库服务实例
db_service = DatabaseService()

@index_validation_bp.route('/tables', methods=['GET'])
def get_tables():
    """获取表列表"""
    app_logger.info("获取表列表")
    
    try:
        # 此处应该添加连接数据库并查询表列表的逻辑
        # 实际项目中，这里会查询数据库获取真实的表列表
        # 以下为模拟数据
        tables = [
            {"name": "table1", "comment": "用户表"},
            {"name": "table2", "comment": "订单表"},
            {"name": "table3", "comment": "产品表"}
        ]
        
        return jsonify({"message": "获取表列表成功", "success": True, "tables": tables})
    except Exception as e:
        app_logger.error(f"获取表列表失败: {str(e)}")
        return jsonify({"message": f"获取表列表失败: {str(e)}", "success": False, "tables": []}), 500

@index_validation_bp.route('/fields/<table_name>', methods=['GET'])
def get_fields(table_name):
    """获取表字段"""
    app_logger.info(f"获取表 {table_name} 的字段")
    
    try:
        # 此处应该添加连接数据库并查询表字段的逻辑
        # 实际项目中，这里会查询数据库获取真实的字段列表
        # 以下为模拟数据
        fields = []
        
        if table_name == "table1":
            fields = [
                {"name": "id", "type": "int", "comment": "ID"},
                {"name": "name", "type": "varchar", "comment": "姓名"},
                {"name": "id_card", "type": "varchar", "comment": "身份证号"},
                {"name": "birth_date", "type": "date", "comment": "出生日期"},
                {"name": "create_time", "type": "datetime", "comment": "创建时间"}
            ]
        elif table_name == "table2":
            fields = [
                {"name": "order_id", "type": "varchar", "comment": "订单ID"},
                {"name": "customer_id", "type": "int", "comment": "客户ID"},
                {"name": "order_date", "type": "date", "comment": "下单日期"},
                {"name": "ship_date", "type": "date", "comment": "发货日期"},
                {"name": "status", "type": "varchar", "comment": "订单状态"}
            ]
        elif table_name == "table3":
            fields = [
                {"name": "product_id", "type": "varchar", "comment": "产品ID"},
                {"name": "product_name", "type": "varchar", "comment": "产品名称"},
                {"name": "launch_date", "type": "date", "comment": "上市日期"},
                {"name": "producer_code", "type": "varchar", "comment": "生产商代码"},
                {"name": "price", "type": "decimal", "comment": "价格"}
            ]
        
        return jsonify({"message": f"获取表 {table_name} 字段成功", "success": True, "fields": fields})
    except Exception as e:
        app_logger.error(f"获取表 {table_name} 字段失败: {str(e)}")
        return jsonify({"message": f"获取表 {table_name} 字段失败: {str(e)}", "success": False, "fields": []}), 500

@index_validation_bp.route('/generate_sql', methods=['POST'])
def generate_sql():
    """生成校验SQL"""
    app_logger.info("生成校验SQL请求")
    
    try:
        # 获取请求参数
        data = request.json
        table_name = data.get('tableName')
        field_name = data.get('fieldName')
        validation_type = data.get('validationType')
        template_id = data.get('templateId')
        
        # 参数验证
        if not table_name:
            return jsonify({"success": False, "message": "表名不能为空"}), 400
        
        if not field_name:
            return jsonify({"success": False, "message": "字段名不能为空"}), 400
            
        if not validation_type:
            return jsonify({"success": False, "message": "校验类型不能为空"}), 400
            
        # 验证模板ID
        if not template_id:
            return jsonify({"success": False, "message": "提示词模板不能为空"}), 400
        
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username')

        # 获取当前数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type(username)
        
        # 调用默认模型服务生成SQL
        try:
            # 获取默认模型信息
            user_info = session_service.get_user_info()
            username = user_info.get('username')
            default_model_info = modelConfigUtil.get_default_model_info(username)
            if not default_model_info:
                app_logger.error("没有找到默认模型配置")
                raise Exception("没有找到默认模型配置，请先设置默认模型")
            
            # 获取模型服务提供商ID和模型ID
            provider_id = default_model_info.get('provider_id')
            model_id = default_model_info.get('model_id')
            
            # 获取模型名称，可能在model_details中
            if 'model_details' in default_model_info and default_model_info['model_details']:
                model_name = default_model_info['model_details'].get('name', '').lower()
            else:
                model_name = ''
            
            app_logger.info(f"使用默认模型生成校验SQL: 提供商 {provider_id}, 模型 {model_id}")
            
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
                    
                except Exception as e:
                    error_msg = f"获取提示词模板失败: {str(e)}"
                    app_logger.error(error_msg)
                    return jsonify({"success": False, "message": error_msg}), 500
            
            # 组装新的用户提示词
            base_prompt = f"{user_prompt_template}\n\n表名：{table_name}\n字段名：{field_name}\n校验类型：{validation_type}\n数据库类型：{db_type}"
            
            # 判断是否为Qwen3模型，如果是则添加/no_think
            if 'qwen3' in model_id.lower() or 'qwen3' in model_name:
                user_prompt = f"{base_prompt} /no_think"
                app_logger.info("检测到Qwen3模型，添加/no_think指令")
            else:
                user_prompt = base_prompt
                app_logger.info(f"非Qwen3模型({model_id})，不添加/no_think指令")
            
            # 如果系统提示词为空，使用默认系统提示词
            if not system_prompt:
                system_prompt = "你是一位专业的数据库专家，精通各种数据库系统（MySQL、SQL Server、Oracle等）的SQL语法。你的任务是生成用于数据校验的SQL查询语句，以识别出不符合要求的数据记录。请仅返回SQL代码，不要包含任何多余的解释。"
            
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
            result = model_chat_service.chat_completion(provider_id, model_id, messages, options)
            
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
            
            # 根据校验类型生成SQL
            sql = ""
            
            if validation_type == "idcard":
                sql = f"""-- 身份证号码校验SQL
SELECT * FROM {table_name} WHERE {field_name} IS NOT NULL AND (
  -- 长度不是15位或18位
  LENGTH({field_name}) NOT IN (15, 18)
  -- 或者18位身份证格式不正确（最后一位校验码错误）
  OR (LENGTH({field_name}) = 18 AND 
      NOT REGEXP_LIKE({field_name}, '^[1-9]\\d{{5}}(19|20)\\d{{2}}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{{3}}[0-9X]$')
     )
  -- 或者15位身份证格式不正确
  OR (LENGTH({field_name}) = 15 AND 
      NOT REGEXP_LIKE({field_name}, '^[1-9]\\d{{5}}\\d{{2}}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{{3}}$')
     )
);"""
            elif validation_type == "date":
                sql = f"""-- 日期格式校验SQL
SELECT * FROM {table_name} WHERE {field_name} IS NOT NULL AND (
  -- 不符合YYYY-MM-DD格式
  NOT REGEXP_LIKE({field_name}, '^\\d{{4}}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$')
  -- 或者不符合YYYY/MM/DD格式
  AND NOT REGEXP_LIKE({field_name}, '^\\d{{4}}/(0[1-9]|1[0-2])/(0[1-9]|[12]\\d|3[01])$')
  -- 或者不符合YYYYMMDD格式
  AND NOT REGEXP_LIKE({field_name}, '^\\d{{4}}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])$')
);"""
            else:
                return jsonify({"success": False, "message": "不支持的校验类型"}), 400
            
            return jsonify({
                "success": True,
                "message": "生成SQL成功 (使用预定义SQL)",
                "sql": sql,
                "from_llm": False
            })
            
    except Exception as e:
        app_logger.error(f"生成校验SQL失败: {str(e)}")
        return jsonify({"success": False, "message": f"生成校验SQL失败: {str(e)}"}), 500

@index_validation_bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    """执行校验SQL"""
    app_logger.info("执行校验SQL")
    
    # 获取请求参数
    data = request.get_json()
    sql = data.get('sql')
    
    if not sql:
        return jsonify({"message": "SQL语句不能为空", "success": False}), 400
    
    try:
        # 获取当前用户信息
        user_info = session_service.get_user_info()
        username = user_info.get('username')
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type(username)
        db_config = DatabaseConfigUtil.get_database_config(username, db_type)
        
        if not db_config:
            return jsonify({"success": False, "message": "获取数据库配置失败"}), 500
        
        # 实际执行SQL
        result = db_service.execute_sql(db_type, db_config, text(sql))
        
        # 获取前端表单中的校验类型
        validation_type = ""
        if "身份证" in sql or "idcard" in sql.lower():
            validation_type = "idcard"
        elif "日期" in sql or "date" in sql.lower():
            validation_type = "date"
        
        # 构造校验结果
        if result.get('is_query', False):
            # 查询语句，使用实际查询结果
            rows = result.get('rows', [])
            # 将行转换为列表
            data = []
            for row in rows:
                data.append(list(row))
            
            app_logger.info(f"查询结果行数: {len(data)}")
            
            # 统一处理所有类型的查询结果
            details = []
            
            # 错误总数
            total_count = len(data)
            
            # 计算错误率
            error_rate = f"{(total_count / 1000) * 100:.1f}%" if total_count > 0 else "0%"
            
            # 错误类型描述
            error_type = "数据校验错误"
            if validation_type == "idcard":
                error_type = "身份证格式错误"
            elif validation_type == "date":
                error_type = "日期格式错误"
            
            # 示例数据 - 显示所有数据，但最多1万条
            examples = ""
            if total_count > 0:
                try:
                    # 限制最多显示1万条
                    max_records = min(total_count, 10000)
                    show_data = data[:max_records]
                    
                    # 获取第一列所有数据作为示例
                    values = []
                    for row in show_data:
                        if row and len(row) > 0:
                            values.append(str(row[0]))
                    
                    examples = ", ".join(values)
                    
                    # 如果数据被截断，添加提示
                    if total_count > 10000:
                        examples += f" (仅显示前10000条，共{total_count}条)"
                        
                except Exception as e:
                    app_logger.error(f"处理示例数据时出错: {str(e)}")
                    examples = "数据格式错误"
            
            # 添加校验结果
            if total_count > 0:
                details.append({
                    "error_type": error_type,
                    "count": total_count,
                    "error_rate": error_rate,
                    "examples": examples
                })
            else:
                details = [{"error_type": "未发现错误", "count": 0, "error_rate": "0%", "examples": ""}]
            
            return jsonify({
                "success": True,
                "message": "执行校验SQL成功",
                "results": {
                    "validation_type": validation_type,
                    "execution_time": result.get('execution_time', ''),
                    "details": details
                }
            })
        else:
            # 非查询语句，返回简单结果
            return jsonify({
                "success": True,
                "message": "执行SQL成功",
                "results": {
                    "validation_type": validation_type,
                    "execution_time": result.get('execution_time', ''),
                    "details": []
                }
            })
    except Exception as e:
        app_logger.error(f"执行校验SQL失败: {str(e)}")
        return jsonify({"message": f"执行校验SQL失败: {str(e)}", "success": False}), 500 