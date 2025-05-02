"""
数据导入页面API

提供数据导入相关的API，包括获取数据库类型、获取数据库表、获取表字段等
"""

from flask import Blueprint, jsonify, request
from utils.database_config_util import DatabaseConfigUtil
from utils.excel_util import ExcelUtil
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

@import_api_bp.route('/api/import/excel/sheets', methods=['GET'])
def get_excel_sheets():
    """获取Excel文件的工作表信息
    
    Query Parameters:
        file_path: Excel文件路径
        
    Returns:
        JSON: 包含Excel工作表列表的JSON对象
    """
    file_path = request.args.get('file_path')
    if not file_path:
        return jsonify({"error": "未指定Excel文件路径"}), 400
    
    try:
        # 验证Excel文件路径
        if not ExcelUtil.validate_excel_path(file_path):
            return jsonify({"error": f"无效的Excel文件路径: {file_path}"}), 400
        
        # 获取Excel工作表信息
        sheets = ExcelUtil.get_sheets_info(file_path)
        
        return jsonify({
            "success": True,
            "file_path": file_path,
            "sheets": sheets
        })
    except Exception as e:
        app_logger.error(f"获取Excel工作表列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取Excel工作表列表失败: {str(e)}"
        }), 500

@import_api_bp.route('/api/import/excel/selected-files', methods=['POST'])
def process_selected_excel_files():
    """处理用户选择的Excel文件列表
    
    Request Body:
        file_paths: Excel文件路径列表
        
    Returns:
        JSON: 包含所有Excel文件及其工作表信息的JSON对象
    """
    data = request.get_json()
    if not data or 'file_paths' not in data:
        return jsonify({"error": "未提供Excel文件路径列表"}), 400
    
    file_paths = data['file_paths']
    if not isinstance(file_paths, list) or len(file_paths) == 0:
        return jsonify({"error": "文件路径列表为空或格式错误"}), 400
    
    try:
        result = []
        for file_path in file_paths:
            # 验证Excel文件路径
            if not ExcelUtil.validate_excel_path(file_path):
                app_logger.warning(f"跳过无效的Excel文件路径: {file_path}")
                continue
            
            # 获取文件名
            file_name = file_path.split('/')[-1].split('\\')[-1]
            
            # 获取Excel工作表信息
            try:
                sheets = ExcelUtil.get_sheets_info(file_path)
                result.append({
                    "path": file_path,
                    "name": file_name,
                    "sheets": sheets
                })
            except Exception as e:
                app_logger.warning(f"处理Excel文件失败: {file_path}, 错误: {str(e)}")
        
        return jsonify({
            "success": True,
            "files": result
        })
    except Exception as e:
        app_logger.error(f"处理选择的Excel文件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"处理选择的Excel文件失败: {str(e)}"
        }), 500

@import_api_bp.route('/api/import/tables/fields', methods=['GET'])
def get_table_fields():
    """获取指定数据库表的字段信息
    
    Query Parameters:
        db_type: 数据库类型
        table_name: 表名
        
    Returns:
        JSON: 包含表字段信息的列表
    """
    db_type = request.args.get('db_type')
    table_name = request.args.get('table_name')
    
    if not db_type:
        return jsonify({"error": "未指定数据库类型"}), 400
    
    if not table_name:
        return jsonify({"error": "未指定表名"}), 400
    
    try:
        # 获取数据库配置
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        if not db_config:
            return jsonify({"error": f"找不到数据库类型 '{db_type}' 的配置"}), 404
        
        # 获取表字段信息
        fields = get_table_field_info(db_type, db_config, table_name)
        
        return jsonify({
            "success": True,
            "table": table_name,
            "fields": fields
        })
    except Exception as e:
        app_logger.error(f"获取表字段信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取表字段信息失败: {str(e)}"
        }), 500

@import_api_bp.route('/api/import/excel/preview', methods=['POST'])
def preview_excel_data():
    """获取Excel文件的数据预览
    
    Request Body:
        file_path: Excel文件路径
        sheet_id: 工作表ID
        start_row: 开始行
        row_limit: 读取行数(可选)
        
    Returns:
        JSON: 包含Excel预览数据的JSON对象
    """
    try:
        # 记录请求参数
        app_logger.info("接收到Excel预览请求")
        
        # 解析请求数据
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "未提供请求数据"}), 400
        
        # 记录请求内容
        app_logger.info(f"Excel预览请求参数: {data}")
        
        file_path = data.get('file_path')
        sheet_id = data.get('sheet_id')
        start_row = data.get('start_row', 1)
        row_limit = data.get('row_limit', 10)
        
        # 验证参数
        if not file_path:
            return jsonify({"success": False, "error": "未指定Excel文件路径"}), 400
        
        if not sheet_id:
            return jsonify({"success": False, "error": "未指定工作表ID"}), 400
        
        # 将start_row转换为整数
        try:
            start_row = int(start_row) - 1  # 转换为0-based索引
            if start_row < 0:
                start_row = 0
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": f"无效的行号: {data.get('start_row')}"}), 400
        
        # 解析sheet_id获取sheet名称和索引
        try:
            sheet_name, sheet_index = ExcelUtil.parse_sheet_id(sheet_id)
        except Exception as e:
            app_logger.error(f"解析sheet_id失败: {str(e)}")
            return jsonify({"success": False, "error": f"无效的工作表ID: {sheet_id}"}), 400
        
        # 获取Excel数据预览
        try:
            preview_data = ExcelUtil.get_sheet_data_preview(
                file_path=file_path,
                sheet_name=sheet_name,
                sheet_index=sheet_index,
                start_row=start_row,
                row_count=row_limit
            )
            
            app_logger.info(f"成功获取Excel预览数据，行数: {len(preview_data['rows'])}")
            
            return jsonify({
                "success": True,
                "file_path": file_path,
                "sheet_id": sheet_id,
                "start_row": start_row + 1,  # 转换回1-based索引
                "data": preview_data
            })
        except Exception as e:
            app_logger.error(f"获取Excel数据预览失败: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"获取Excel数据预览失败: {str(e)}"
            }), 500
            
    except Exception as e:
        app_logger.error(f"Excel预览处理出现未捕获的异常: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

def get_table_field_info(db_type, db_config, table_name):
    """获取数据库表的字段信息
    
    Args:
        db_type: 数据库类型
        db_config: 数据库配置
        table_name: 表名
        
    Returns:
        list: 字段信息列表，每个元素包含字段名、类型等信息
    """
    try:
        # 获取数据库名
        database = db_config.get('database', '')
        
        if not database:
            raise AppException("数据库名称为空", 400)
        
        if db_type == 'mysql':
            # 使用MySQL信息模式查询表结构
            connection = db_service.pool_manager.get_connection(db_type, db_config)
            try:
                # 选择数据库
                connection.execute(text(f"USE `{database}`"))
                
                # 查询表字段信息
                result = connection.execute(text(f"""
                    SELECT 
                        COLUMN_NAME, 
                        DATA_TYPE,
                        COLUMN_COMMENT,
                        ORDINAL_POSITION
                    FROM 
                        INFORMATION_SCHEMA.COLUMNS 
                    WHERE 
                        TABLE_SCHEMA = :database 
                        AND TABLE_NAME = :table_name
                    ORDER BY 
                        ORDINAL_POSITION
                """), {"database": database, "table_name": table_name})
                
                # 提取字段信息
                fields = []
                for row in result:
                    fields.append({
                        "name": row[0],
                        "type": row[1],
                        "comment": row[2] if row[2] else row[0],
                        "position": row[3]
                    })
                
                return fields
            finally:
                connection.close()
        elif db_type == 'sqlserver':
            # SQL Server表字段查询
            query = """
                SELECT 
                    c.name AS COLUMN_NAME,
                    t.name AS DATA_TYPE,
                    ep.value AS COLUMN_COMMENT,
                    c.column_id AS ORDINAL_POSITION
                FROM 
                    sys.columns c
                INNER JOIN 
                    sys.types t ON c.user_type_id = t.user_type_id
                LEFT JOIN 
                    sys.extended_properties ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description'
                WHERE 
                    c.object_id = OBJECT_ID(:table_name)
                ORDER BY 
                    c.column_id
            """
            result = db_service.execute_query(db_type, db_config, text(query), {"table_name": table_name})
            
            fields = []
            for row in result:
                fields.append({
                    "name": row[0],
                    "type": row[1],
                    "comment": row[2] if row[2] else row[0],
                    "position": row[3]
                })
            
            return fields
        elif db_type == 'oracle':
            # Oracle表字段查询
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    COLUMN_ID
                FROM 
                    ALL_TAB_COLUMNS
                WHERE 
                    OWNER = UPPER(:owner)
                    AND TABLE_NAME = UPPER(:table_name)
                ORDER BY 
                    COLUMN_ID
            """
            result = db_service.execute_query(db_type, db_config, text(query), {"owner": database, "table_name": table_name})
            
            fields = []
            for row in result:
                fields.append({
                    "name": row[0],
                    "type": row[1],
                    "comment": row[0],
                    "position": row[2]
                })
            
            return fields
        else:
            raise AppException(f"不支持的数据库类型: {db_type}", 400)
    except Exception as e:
        app_logger.error(f"获取表字段信息失败: {str(e)}")
        raise AppException(f"获取表字段信息失败: {str(e)}", 500) 