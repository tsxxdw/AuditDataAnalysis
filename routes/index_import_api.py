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
        JSON: 包含所有表名和备注的列表
    """
    db_type = request.args.get('db_type')
    if not db_type:
        return jsonify({"error": "未指定数据库类型"}), 400
    
    try:
        # 获取数据库配置
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        if not db_config:
            return jsonify({"error": f"找不到数据库类型 '{db_type}' 的配置"}), 404
        
        # 使用数据库服务获取所有表信息
        tables = db_service.get_database_tables(db_type, db_config)
        
        # 返回结果
        return jsonify(tables)
    except Exception as e:
        app_logger.error(f"获取数据库表列表失败: {str(e)}")
        return jsonify({"error": f"获取表列表失败: {str(e)}"}), 500

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
        
        # 使用数据库服务获取表字段信息
        fields = db_service.get_table_field_info(db_type, db_config, table_name)
        
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
    """预览Excel数据"""
    app_logger.info("请求预览Excel数据")
    try:
        # 获取请求参数
        data = request.get_json() or {}
        file_path = data.get('file_path', '')
        sheet_id = data.get('sheet_id', '0')
        start_row = int(data.get('start_row', 0))
        row_count = int(data.get('row_count', 10))
        get_total_rows = data.get('get_total_rows', False)  # 新增参数，表示是否需要获取总行数

        # 将前端传入的起始行（从1开始计数）转换为Python中的索引（从0开始计数）
        if start_row > 0:
            start_row = start_row - 1

        # 验证Excel文件路径
        if not ExcelUtil.validate_excel_path(file_path):
            app_logger.warning(f"无效的Excel文件路径: {file_path}")
            return jsonify({
                "success": False,
                "message": f"无效的Excel文件路径: {file_path}"
            })

        # 解析sheet_id，可能是"name:index"或仅索引
        sheet_name, sheet_index = ExcelUtil.parse_sheet_id(sheet_id)
        
        # 获取数据预览
        try:
            headers, rows = ExcelUtil.get_sheet_data_preview(
                file_path, sheet_name, sheet_index, start_row, row_count
            )
            
            # 构建数据对象，兼容前端期望的格式
            preview_data = {
                "rows": rows
            }
            
        except Exception as e:
            app_logger.error(f"获取Excel预览数据失败: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": f"获取Excel预览数据失败: {str(e)}"
            })
        
        # 如果请求获取总行数，则添加到响应中
        total_rows = None
        if get_total_rows:
            try:
                # 获取所有行，但忽略空行
                all_rows = ExcelUtil.read_excel_data(
                    file_path=file_path, 
                    sheet_name=sheet_name, 
                    sheet_index=sheet_index,
                    start_row=0,  # 从第一行开始
                    row_limit=None,  # 读取所有行
                    ignore_empty_rows=True  # 忽略空行
                )
                
                # 计算非空行的数量
                total_rows = len(all_rows)
                if total_rows is not None:
                    total_rows = int(total_rows)  # 确保是Python原生int类型
                
                app_logger.info(f"获取到Excel工作表实际总行数(排除空行): {total_rows}")
            except Exception as e:
                app_logger.error(f"获取工作表总行数失败: {str(e)}")
                # 失败时不返回错误，只是不提供总行数信息
        
        response = {
            "success": True,
            "data": preview_data,
            "start_row": start_row  # 添加这个字段以兼容前端使用
        }
        
        # 如果获取到总行数，添加到响应中
        if total_rows is not None:
            response["total_rows"] = total_rows
            
        return jsonify(response)
    except Exception as e:
        app_logger.error(f"预览Excel数据失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"预览Excel数据失败: {str(e)}"
        })

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

@import_api_bp.route('/api/import/excel/import', methods=['POST'])
def import_excel_data():
    """导入Excel数据到数据库表
    
    Request Body:
        file_path: Excel文件路径
        sheet_id: 工作表ID
        database_id: 数据库ID
        table_id: 表ID
        start_row: 开始导入行
        condition: 可选的导入条件
        supplements: 可选的补充字段列表
        
    Returns:
        JSON: 包含导入结果的JSON对象
    """
    try:
        # 记录请求参数
        app_logger.info("接收到Excel导入请求")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "未提供请求数据"
            }), 400
        
        # 记录请求内容
        app_logger.info(f"Excel导入请求参数: {data}")
        
        # 提取必要参数
        file_path = data.get('file_path')
        sheet_id = data.get('sheet_id')
        database_id = data.get('database_id')
        table_id = data.get('table_id')
        start_row = data.get('start_row', 2)
        condition = data.get('condition')
        supplements = data.get('supplements', [])
        
        # 验证必要参数
        if not file_path:
            return jsonify({"success": False, "message": "未指定Excel文件路径"}), 400
        
        if not sheet_id:
            return jsonify({"success": False, "message": "未指定工作表ID"}), 400
        
        if not database_id:
            return jsonify({"success": False, "message": "未指定数据库ID"}), 400
        
        if not table_id:
            return jsonify({"success": False, "message": "未指定表ID"}), 400
        
        # 验证Excel文件路径
        if not ExcelUtil.validate_excel_path(file_path):
            return jsonify({"success": False, "message": f"无效的Excel文件路径: {file_path}"}), 400
        
        # 解析sheet_id获取sheet名称和索引
        try:
            sheet_name, sheet_index = ExcelUtil.parse_sheet_id(sheet_id)
        except Exception as e:
            app_logger.error(f"解析sheet_id失败: {str(e)}")
            return jsonify({"success": False, "message": f"无效的工作表ID: {sheet_id}"}), 400
        
        # 获取数据库配置
        db_config = DatabaseConfigUtil.get_database_config(database_id)
        if not db_config:
            return jsonify({"success": False, "message": f"找不到数据库类型 '{database_id}' 的配置"}), 404
        
        # 开始执行导入过程
        start_time = time.time()
        
        app_logger.info(f"开始导入Excel数据到数据库，文件: {file_path}, 表: {table_id}")
        addLog = []  # 用于存储导入过程中的日志
        
        # 添加日志记录
        addLog.append({"type": "info", "message": f"开始读取Excel文件: {os.path.basename(file_path)}"})
        
        # 读取Excel数据
        try:
            excel_data = ExcelUtil.read_excel_data(
                file_path=file_path, 
                sheet_name=sheet_name, 
                start_row=start_row-1, 
                row_limit=None,
                ignore_empty_rows=True  # 添加参数，忽略全空行
            )
            total_rows = len(excel_data)
            addLog.append({"type": "info", "message": f"成功读取Excel数据，共{total_rows}行（已忽略空行）"})
        except Exception as e:
            app_logger.error(f"读取Excel数据失败: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "读取Excel数据失败",
                "error": {
                    "message": str(e)
                }
            }), 500
        
        # 如果没有数据，返回错误
        if not excel_data or len(excel_data) == 0:
            return jsonify({
                "success": False,
                "message": "Excel文件中没有数据",
                "total_rows": 0
            }), 400
        
        # 获取表结构信息
        try:
            table_fields = db_service.get_table_field_info(database_id, db_config, table_id)
            addLog.append({"type": "info", "message": f"获取表 {table_id} 的字段信息，共{len(table_fields)}个字段"})
        except Exception as e:
            app_logger.error(f"获取表结构信息失败: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "获取表结构信息失败",
                "error": {
                    "message": str(e)
                }
            }), 500
        
        try:
            # 应用条件筛选
            filtered_data = []
            if condition and condition.get('column') is not None and condition.get('type'):
                column_index = int(condition['column'])
                condition_type = condition['type']
                
                addLog.append({"type": "info", "message": f"应用筛选条件: {condition.get('column_name')} {condition.get('type_name')}"})
                
                for row in excel_data:
                    # 确保行数据长度足够
                    if len(row) > column_index:
                        cell_value = row[column_index]
                        
                        # 应用条件
                        if condition_type == 'empty' and (cell_value is None or cell_value == ''):
                            filtered_data.append(row)
                        elif condition_type == 'not_empty' and (cell_value is not None and cell_value != ''):
                            filtered_data.append(row)
                        # 可以根据需要添加更多条件类型
                    else:
                        # 如果行数据不够长，忽略这一行
                        continue
                
                addLog.append({"type": "info", "message": f"筛选后保留{len(filtered_data)}行数据"})
            else:
                # 没有条件，使用所有数据
                filtered_data = excel_data
                addLog.append({"type": "info", "message": f"未设置筛选条件，使用所有{len(filtered_data)}行数据"})
            
            # 准备导入数据
            prepared_data = []
            
            # 转换数据格式: 从行列表转为字段映射字典
            for row_data in filtered_data:
                row_dict = {}
                # 将Excel列数据映射到表字段
                for col_index, field in enumerate(table_fields):
                    if col_index < len(row_data):
                        row_dict[field['name']] = row_data[col_index]
                prepared_data.append(row_dict)
            
            # 准备补充字段
            prepared_supplements = []
            for supplement in supplements:
                if supplement.get('enabled') and supplement.get('column') is not None and 'value' in supplement:
                    column_index = int(supplement['column'])
                    if column_index < len(table_fields):
                        field_name = table_fields[column_index]['name']
                        prepared_supplements.append({
                            'enabled': True,
                            'name': field_name,
                            'column_name': supplement.get('column_name', f"列{column_index}"),
                            'value': supplement['value']
                        })
            
            # 开始导入数据
            addLog.append({"type": "info", "message": f"开始导入数据到表 {table_id}"})
            
            # 使用数据库服务的execute_sql方法执行数据导入
            success_count = 0
            error_count = 0
            failed_row = None
            error_message = None
            
            try:
                # 分批处理数据，每批200条
                batch_size = 200
                total_rows = len(prepared_data)
                
                for batch_index in range(0, total_rows, batch_size):
                    try:
                        # 获取当前批次的数据
                        end_index = min(batch_index + batch_size, total_rows)
                        current_batch = prepared_data[batch_index:end_index]
                        
                        if not current_batch:
                            continue
                            
                        # 处理补充字段
                        if prepared_supplements:
                            for row_data in current_batch:
                                for supplement in prepared_supplements:
                                    if supplement.get('enabled') and 'value' in supplement:
                                        field_name = supplement.get('name')
                                        if field_name:
                                            row_data[field_name] = supplement['value']
                        
                        # 获取字段列表（从第一行获取）
                        fields = list(current_batch[0].keys())
                        fields_str = ', '.join([f"`{key}`" for key in fields])
                        
                        # 构建批量插入的VALUES部分
                        values_list = []
                        
                        for row_data in current_batch:
                            # 格式化每一行的值
                            row_values = []
                            for field in fields:
                                val = row_data.get(field)
                                if val is None:
                                    row_values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    row_values.append(str(val))
                                else:
                                    escaped_val = str(val).replace("'", "''")
                                    row_values.append(f"'{escaped_val}'")
                            
                            # 添加当前行的值
                            values_list.append(f"({', '.join(row_values)})")
                        
                        # 构建批量插入SQL
                        insert_sql = f"INSERT INTO {table_id} ({fields_str}) VALUES {', '.join(values_list)}"
                        
                        # 执行批量插入
                        result = db_service.execute_sql(
                            db_type=database_id,
                            config=db_config,
                            sql=text(insert_sql),
                            params=()
                        )
                        
                        # 更新成功计数
                        success_count += len(current_batch)
                        
                        # 记录进度
                        progress_percent = int((end_index / total_rows) * 100)
                        addLog.append({"type": "info", "message": f"已批量导入至第 {end_index} 行 ({progress_percent}%)"})
                        app_logger.info(f"导入进度: {progress_percent}%, 已处理{end_index}行")
                        
                        # 尝试执行显式提交
                        try:
                            commit_sql = text("COMMIT")
                            db_service.execute_sql(
                                db_type=database_id,
                                config=db_config,
                                sql=commit_sql,
                                params=()
                            )
                            app_logger.debug(f"在批次 {batch_index}-{end_index} 后执行了显式COMMIT")
                        except Exception as commit_error:
                            app_logger.warning(f"显式提交可能失败: {str(commit_error)}")
                            
                    except Exception as e:
                        # 记录错误信息
                        error_count += (end_index - batch_index)
                        failed_row = batch_index
                        error_message = str(e)
                        app_logger.error(f"导入批次 {batch_index}-{end_index} 失败: {error_message}", exc_info=True)
                        addLog.append({"type": "error", "message": f"导入第 {batch_index+1}-{end_index} 行数据失败: {error_message}"})
                        
                        # 出错时停止后续导入
                        raise
                
                # 记录完成信息
                app_logger.info(f"数据导入成功，共{success_count}行")
                
            except Exception as e:
                # 如果不是已处理的错误，记录为未处理的异常
                if failed_row is None:
                    app_logger.error(f"导入过程中发生未处理的异常: {str(e)}", exc_info=True)
                    addLog.append({"type": "error", "message": f"导入过程中发生未处理的异常: {str(e)}"})
                    error_count = 1
                    error_message = str(e)
                
            # 计算总耗时
            duration = round(time.time() - start_time, 2)
            
            # 处理导入结果
            if error_count == 0:
                # 添加一个验证查询，确认数据确实已经写入
                try:
                    # 构建简单查询以验证数据
                    verify_sql = text(f"SELECT COUNT(*) FROM {table_id}")
                    verify_result = db_service.execute_sql(
                        db_type=database_id,
                        config=db_config,
                        sql=verify_sql
                    )
                    
                    # 提取记录数
                    count_row = next(iter(verify_result['rows']), None)
                    record_count = count_row[0] if count_row else 0
                    
                    addLog.append({"type": "info", "message": f"验证查询: 表 {table_id} 中共有 {record_count} 条记录"})
                    app_logger.info(f"导入后验证查询: 表 {table_id} 中共有 {record_count} 条记录")
                    
                except Exception as e:
                    app_logger.error(f"验证查询失败: {str(e)}", exc_info=True)
                    addLog.append({"type": "warning", "message": f"无法验证数据是否成功写入: {str(e)}"})
                
                # 导入完成后的记录
                addLog.append({"type": "info", "message": f"导入完成，共导入{success_count}行数据，耗时{duration}秒"})
                app_logger.info(f"Excel导入完成，成功:{success_count}, 失败:{error_count}, 耗时:{duration}秒")
                
                # 返回成功响应
                return jsonify({
                    "success": True,
                    "message": "数据导入成功",
                    "success_count": success_count,
                    "error_count": error_count,
                    "total_rows": len(filtered_data),
                    "details": {
                        "duration": duration
                    },
                    "logs": addLog
                })
            else:
                # 处理导入失败的情况
                current_row = failed_row + start_row if failed_row is not None else None
                
                addLog.append({"type": "error", "message": f"导入数据过程中出错: {error_message}"})
                if current_row is not None:
                    addLog.append({"type": "error", "message": f"错误发生在第 {current_row} 行"})
                
                return jsonify({
                    "success": False,
                    "message": "导入数据过程中出错",
                    "error": {
                        "row": current_row,
                        "message": error_message
                    },
                    "processed_rows": failed_row,
                    "success_count": success_count,
                    "error_count": error_count,
                    "total_rows": len(filtered_data),
                    "logs": addLog
                }), 500
        except Exception as e:
            error_msg = str(e)
            app_logger.error(f"Excel导入过程中发生未处理的异常: {error_msg}", exc_info=True)
            addLog.append({"type": "error", "message": f"导入过程中发生异常: {error_msg}"})
            
            return jsonify({
                "success": False,
                "message": "导入过程中发生异常",
                "error": {
                    "message": error_msg
                },
                "total_rows": len(filtered_data),
                "logs": addLog
            }), 500
    
    except Exception as e:
        error_msg = str(e)
        app_logger.error(f"Excel导入API异常: {error_msg}", exc_info=True)
        
        return jsonify({
            "success": False,
            "message": "导入过程中发生异常",
            "error": {
                "message": error_msg
            }
        }), 500 