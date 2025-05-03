"""
数据导入页面API

提供数据导入相关的API，包括获取数据库类型、获取数据库表、获取表字段等
"""

from flask import Blueprint, jsonify, request, current_app, send_file, send_from_directory
from utils.database_config_util import DatabaseConfigUtil
from utils.excel_util import ExcelUtil
from config.global_config import get_project_root, get_export_dir
from service.database.database_service import DatabaseService
from service.database.db_pool_manager import DatabasePoolManager
from service.log.logger import app_logger
from service.exception import AppException
from sqlalchemy import text
import os
import time
import datetime
from werkzeug.utils import secure_filename
import uuid

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
        skipped_files = []
        error_files = []
        
        app_logger.info(f"处理选择的Excel文件，共{len(file_paths)}个文件")
        
        for file_path in file_paths:
            # 验证Excel文件路径
            if not ExcelUtil.validate_excel_path(file_path):
                app_logger.warning(f"跳过无效的Excel文件路径: {file_path}")
                skipped_files.append({
                    "path": file_path,
                    "reason": "文件路径无效"
                })
                continue
            
            # 获取文件名和扩展名
            file_name = file_path.split('/')[-1].split('\\')[-1]
            ext = os.path.splitext(file_path)[1].lower()
            
            # 获取Excel工作表信息
            try:
                sheets = ExcelUtil.get_sheets_info(file_path)
                result.append({
                    "path": file_path,
                    "name": file_name,
                    "extension": ext,
                    "sheets": sheets
                })
                app_logger.info(f"成功处理Excel文件: {file_name}, 格式: {ext}, 工作表数量: {len(sheets)}")
            except Exception as e:
                app_logger.warning(f"处理Excel文件失败: {file_path}, 错误: {str(e)}")
                error_files.append({
                    "path": file_path,
                    "name": file_name,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "files": result,
            "skipped_files": skipped_files,
            "error_files": error_files
        })
    except Exception as e:
        app_logger.error(f"处理选择的Excel文件失败: {str(e)}", exc_info=True)
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

@import_api_bp.route('/api/import/excel/open', methods=['POST'])
def open_excel_file():
    """打开指定的Excel文件
    
    此功能仅在Windows环境和本地部署的服务器上有效
    
    Request Body:
        file_path: Excel文件路径
        sheet_id: 工作表ID
        
    Returns:
        JSON: 包含操作结果的JSON对象
    """
    try:
        # 检查是否为本地请求
        is_local = _is_local_request()
        app_logger.info(f"打开Excel请求 - 是否本地请求: {is_local}, Host: {request.host}")
        
        if not is_local:
            app_logger.warning(f"非本地请求尝试打开Excel文件, Host: {request.host}")
            return jsonify({
                "success": False,
                "message": "此功能仅支持本地访问",
                "is_local": False
            }), 403
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "未提供请求数据",
                "is_local": True
            }), 400
        
        # 获取文件路径和工作表ID
        file_path = data.get('file_path')
        sheet_id = data.get('sheet_id')
        
        app_logger.info(f"尝试打开Excel文件: {file_path}, sheet_id: {sheet_id}")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "未指定Excel文件路径",
                "is_local": True
            }), 400
        
        # 验证文件路径是否在允许范围内
        app_logger.info(f"验证文件路径: {file_path}")
        if not _is_safe_file_path(file_path):
            app_logger.warning(f"文件路径安全检查失败: {file_path}")
            return jsonify({
                "success": False,
                "message": "不允许访问指定的文件路径",
                "is_local": True,
                "details": "文件必须位于static/uploads目录或其子目录下，且必须是Excel文件(.xls或.xlsx)"
            }), 403
        
        # 调用Excel工具类打开文件
        app_logger.info(f"开始打开Excel文件: {file_path}")
        result = ExcelUtil.open_excel_file(file_path, sheet_id)
        app_logger.info(f"打开Excel文件结果: {result}")
        
        # 将is_local信息添加到结果中
        result["is_local"] = True
        
        # 记录使用的是哪种Office软件
        if result.get("success") and result.get("using_wps") is not None:
            is_wps = result.get("using_wps")
            app_logger.info(f"使用{'WPS' if is_wps else 'Microsoft Excel'}打开文件: {file_path}")
        
        return jsonify(result)
        
    except Exception as e:
        app_logger.error(f"打开Excel文件失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"打开Excel文件失败: {str(e)}",
            "is_local": _is_local_request()
        }), 500

def _is_local_request():
    """检查当前请求是否来自本地
    
    基于请求的Host头判断是否为localhost或127.0.0.1
    
    Returns:
        bool: 是否为本地请求
    """
    host = request.host.split(':')[0].lower()
    return host in ('localhost', '127.0.0.1')

def _is_safe_file_path(file_path):
    """判断文件路径是否在允许的范围内
    
    防止任意文件访问，确保只能访问static/uploads目录及其子目录下的Excel文件
    
    Args:
        file_path: 要检查的文件路径
        
    Returns:
        bool: 文件路径是否安全
    """
    try:
        # 规范化路径，处理路径分隔符差异
        abs_path = os.path.abspath(file_path)
        
        # 尝试获取应用的根目录和uploads目录
        root_dir = current_app.root_path
        
        # 处理多种可能的uploads目录结构
        possible_upload_dirs = [
            os.path.abspath(os.path.join(root_dir, 'static', 'uploads')),  # /app/static/uploads
            os.path.abspath(os.path.join(root_dir, '..', 'static', 'uploads')),  # /static/uploads (相对于app)
            os.path.abspath('./static/uploads')  # 当前工作目录下的static/uploads
        ]
        
        # 检查文件是否存在
        if not os.path.exists(abs_path):
            app_logger.warning(f"文件不存在: {abs_path}")
            return False
        
        # 检查是否为Excel文件
        if not abs_path.lower().endswith(('.xlsx', '.xls')):
            app_logger.warning(f"不是Excel文件: {abs_path}")
            return False
        
        # 检查文件是否在允许的uploads目录下
        is_in_uploads = False
        for uploads_dir in possible_upload_dirs:
            # 记录路径信息用于调试
            app_logger.debug(f"检查路径是否在uploads目录下: {abs_path} vs {uploads_dir}")
            
            if os.path.exists(uploads_dir) and abs_path.startswith(uploads_dir):
                is_in_uploads = True
                break
        
        if not is_in_uploads:
            app_logger.warning(f"文件路径不在允许的目录范围内: {abs_path}")
            
            # 输出所有尝试的目录路径，帮助调试
            app_logger.warning(f"允许的目录: {possible_upload_dirs}")
            
            return False
        
        return True
        
    except Exception as e:
        app_logger.error(f"文件路径安全检查失败: {str(e)}", exc_info=True)
        return False

@import_api_bp.route('/api/import/export-logs', methods=['POST'])
def export_logs():
    """导出日志到文件并提供下载
    
    Request Body:
        logs: 日志条目列表
        title: 日志标题(可选)
        
    Returns:
        JSON: 包含下载链接的JSON对象
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'logs' not in data:
            return jsonify({
                "success": False,
                "message": "未提供日志内容"
            }), 400
        
        logs = data.get('logs', [])
        title = data.get('title', '操作日志')
        
        if not logs or not isinstance(logs, list):
            return jsonify({
                "success": False,
                "message": "日志内容格式无效"
            }), 400
        
        # 使用全局配置的导出目录
        export_dir = get_export_dir()
        app_logger.info(f"使用全局配置的导出目录: {export_dir}")
        
        # 生成唯一文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"import_log_{timestamp}_{unique_id}.txt"
        file_path = os.path.join(export_dir, filename)
        
        # 写入日志内容
        with open(file_path, 'w', encoding='utf-8') as f:
            # 写入标题和时间
            f.write(f"{title}\n")
            f.write(f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"项目路径: {get_project_root()}\n")
            f.write("="*50 + "\n\n")
            
            # 写入日志条目
            for log in logs:
                f.write(f"{log}\n")
        
        # 计算下载URL
        download_url = f"/export/{filename}"
        
        app_logger.info(f"日志已导出到文件: {os.path.abspath(file_path)}")
        app_logger.info(f"下载URL: {download_url}")
        
        return jsonify({
            "success": True,
            "message": "日志导出成功",
            "filename": filename,
            "download_url": download_url,
            "file_path": os.path.abspath(file_path)  # 在响应中包含完整路径
        })
        
    except Exception as e:
        app_logger.error(f"导出日志失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"导出日志失败: {str(e)}"
        }), 500

def _ensure_export_directory():
    """确保导出目录存在
    
    使用全局配置的项目路径获取导出目录
    
    Returns:
        str: 导出目录路径
    """
    try:
        # 使用全局配置的导出目录
        export_dir = get_export_dir()
        app_logger.info(f"使用全局配置获取导出目录: {export_dir}")
        return export_dir
    except Exception as e:
        app_logger.error(f"获取导出目录失败: {str(e)}", exc_info=True)
        
        # 使用一个确定可写入的目录作为备用
        fallback_dir = os.path.join(os.getcwd(), 'export')
        app_logger.warning(f"使用备用目录: {fallback_dir}")
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir

@import_api_bp.route('/export/<path:filename>')
def download_export_file(filename):
    """提供导出文件下载的路由
    
    Args:
        filename: 文件名
        
    Returns:
        文件下载响应
    """
    try:
        # 使用全局配置的导出目录
        export_dir = get_export_dir()
        
        # 记录尝试的路径
        app_logger.info(f"尝试从导出目录下载文件: {export_dir}")
        
        # 检查文件是否存在
        file_path = os.path.join(export_dir, filename)
        if not os.path.exists(file_path):
            app_logger.error(f"要下载的文件不存在: {file_path}")
            return jsonify({
                "success": False,
                "message": f"文件不存在: {filename}"
            }), 404
        
        app_logger.info(f"下载导出文件: {filename}, 目录: {export_dir}")
        
        # 返回文件
        return send_from_directory(export_dir, filename, as_attachment=True)
    except Exception as e:
        app_logger.error(f"下载文件失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"下载文件失败: {str(e)}"
        }), 500 