"""
EXCEL修复API路由

提供EXCEL修复相关功能的API接口
"""

from flask import Blueprint, request, jsonify, current_app, send_file, url_for
import os
import pandas as pd
import uuid
import tempfile
from service.log.logger import app_logger
from datetime import datetime, timedelta
import glob
import time

# 创建蓝图
excel_repair_api = Blueprint('excel_repair_api', __name__)

# 存储处理后的文件信息
processed_files = {}

# 定义Excel修复文件保存目录
EXCEL_REPAIR_DIR = 'file/download/excel_repair'

# 清理过期的Excel修复文件
def cleanup_old_files(max_age_hours=24):
    """
    清理指定小时数之前的Excel修复文件
    """
    try:
        if not os.path.exists(EXCEL_REPAIR_DIR):
            return
            
        # 计算过期时间
        expire_time = time.time() - (max_age_hours * 3600)
        
        # 获取目录中的所有Excel文件
        excel_files = glob.glob(os.path.join(EXCEL_REPAIR_DIR, "*.xls*"))
        
        # 检查并删除过期文件
        deleted_count = 0
        for file_path in excel_files:
            file_time = os.path.getmtime(file_path)
            if file_time < expire_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    app_logger.warning(f"删除过期Excel文件失败: {file_path}, 错误: {str(e)}")
        
        if deleted_count > 0:
            app_logger.info(f"清理了 {deleted_count} 个过期的Excel修复文件")
    except Exception as e:
        app_logger.error(f"清理过期Excel文件时出错: {str(e)}")

@excel_repair_api.route('/api/excel_repair/remove_blank_rows', methods=['POST'])
def remove_blank_rows():
    """
    去除Excel中的空白行
    """
    try:
        # 清理旧文件
        cleanup_old_files()
        
        data = request.json
        file_path = data.get('file_path')
        sheet_name = data.get('sheet_name')
        start_row = data.get('start_row', 1)  # 默认从第1行开始
        
        if not file_path or not sheet_name:
            return jsonify({"success": False, "message": "文件路径或工作表名不能为空"}), 400
        
        # 确保start_row是整数
        try:
            start_row = int(start_row)
        except (ValueError, TypeError):
            app_logger.warning(f"无效的数据开始行: {start_row}，使用默认值1")
            start_row = 1
            
        app_logger.info(f"处理请求: 文件={file_path}, 工作表={sheet_name}, 数据开始行={start_row}")
        
        try:
            # 读取Excel文件的所有工作表
            excel = pd.ExcelFile(file_path, engine='openpyxl')
            sheet_names = excel.sheet_names
            
            # 读取需要处理的工作表（不指定header，以便获取所有行）
            df_original = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
            
            # 获取原始行数（包括所有标题行和数据行）
            original_rows = len(df_original)
            app_logger.info(f"原始Excel文件行数: {original_rows}")
            
            # 确保start_row不超过文件行数
            if start_row > original_rows:
                app_logger.warning(f"数据开始行 {start_row} 超过文件总行数 {original_rows}，使用默认值1")
                start_row = 1
            
            # 使用指定的数据开始行读取数据（header=None表示不使用任何行作为列名）
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=start_row-1, engine='openpyxl')
            
            # 获取列数
            num_columns = len(df.columns)
            app_logger.info(f"读取到的列数: {num_columns}")
            
            # 获取数据行数
            data_rows_before = len(df)
            app_logger.info(f"读取的数据行数: {data_rows_before}")
            
            # 删除全为空的行
            df_cleaned = df.dropna(how='all')
            data_rows_after = len(df_cleaned)
            app_logger.info(f"清除空行后数据行数: {data_rows_after}")
            
            # 移除的行数 = 原始数据行数 - 处理后数据行数
            removed_data_rows = data_rows_before - data_rows_after
            
            # 保留的行数 = 原始行数 - 移除的行数
            processed_rows = original_rows - removed_data_rows
            removed_rows = removed_data_rows
            
            app_logger.info(f"处理结果: 原始行数={original_rows}, 处理后行数={processed_rows}, 移除行数={removed_rows}")
            
            # 确保保存目录存在
            os.makedirs(EXCEL_REPAIR_DIR, exist_ok=True)
            
            # 创建输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = os.path.basename(file_path)
            base_name, ext = os.path.splitext(filename)
            new_filename = f"{base_name}_cleaned_{timestamp}{ext}"
            output_path = os.path.join(EXCEL_REPAIR_DIR, new_filename)
            
            # 创建一个ExcelWriter对象，用于写入多个工作表
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 复制原Excel的所有工作表
                for sheet in sheet_names:
                    # 读取原始工作表
                    original_sheet_data = pd.read_excel(file_path, sheet_name=sheet, header=None, engine='openpyxl')
                    # 保存到新Excel中
                    original_sheet_data.to_excel(writer, sheet_name=sheet, index=False, header=False)
                
                # 添加处理后的工作表（额外的工作表）
                sheet_index = 1
                new_sheet_name = f"已清除空白行_{sheet_name}"
                
                # 检查是否存在同名工作表，如果存在则添加序号
                while new_sheet_name in sheet_names:
                    sheet_index += 1
                    new_sheet_name = f"已清除空白行_{sheet_name}_{sheet_index}"
                
                # 保存处理后的工作表
                df_cleaned.to_excel(writer, sheet_name=new_sheet_name, index=False, header=False)
                
                # 创建修复信息工作表
                repair_info = pd.DataFrame({
                    '项目': ['原始行数', '处理后行数', '移除行数', '数据开始行', '处理时间', '操作类型', '处理的工作表'],
                    '值': [
                        original_rows, 
                        processed_rows, 
                        removed_rows, 
                        f"第{start_row}行",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "清除空白行",
                        sheet_name
                    ]
                })
                
                # 保存修复信息工作表
                info_sheet_name = "修复信息"
                # 检查是否存在同名工作表，如果存在则添加序号
                info_sheet_index = 1
                while info_sheet_name in sheet_names:
                    info_sheet_index += 1
                    info_sheet_name = f"修复信息_{info_sheet_index}"
                
                repair_info.to_excel(writer, sheet_name=info_sheet_name, index=False)
                
                # 设置所有工作表的格式，禁用科学计数法
                workbook = writer.book
                for sheet_name, worksheet in writer.sheets.items():
                    # 遍历所有列
                    for column in worksheet.columns:
                        for cell in column:
                            if isinstance(cell.value, (int, float)) and cell.data_type == 'n':
                                cell.number_format = '0'
            
            # 生成唯一ID，用于后续下载
            file_id = str(uuid.uuid4())
            processed_files[file_id] = {
                "output_path": output_path,
                "filename": new_filename,
                "original_rows": original_rows,
                "processed_rows": processed_rows,
                "removed_rows": removed_rows
            }
            
            app_logger.info(f"Excel文件空白行去除完成: {file_path}, 原始行数: {original_rows}, 处理后行数: {processed_rows}, 移除行数: {removed_rows}, 数据开始行: {start_row}")
            
            return jsonify({
                "success": True,
                "message": "Excel文件处理完成",
                "file_id": file_id,
                "original_rows": original_rows,
                "processed_rows": processed_rows,
                "removed_rows": removed_rows,
                "download_url": url_for('excel_repair_api.download_file', file_id=file_id)
            })
            
        except Exception as e:
            app_logger.error(f"Excel文件空白行去除失败: {str(e)}")
            return jsonify({"success": False, "message": f"处理失败: {str(e)}"}), 500
    
    except Exception as e:
        app_logger.error(f"Excel文件空白行去除API错误: {str(e)}")
        return jsonify({"success": False, "message": f"处理失败: {str(e)}"}), 500

@excel_repair_api.route('/api/excel_repair/remove_duplicates', methods=['POST'])
def remove_duplicates():
    """
    根据选择的字段去除Excel中的重复行
    """
    try:
        # 清理旧文件
        cleanup_old_files()
        
        data = request.json
        file_path = data.get('file_path')
        sheet_name = data.get('sheet_name')
        columns = data.get('columns', [])
        start_row = data.get('start_row', 1)  # 默认从第1行开始
        
        if not file_path or not sheet_name or not columns:
            return jsonify({"success": False, "message": "文件路径、工作表名或列名不能为空"}), 400
        
        # 确保start_row是整数
        try:
            start_row = int(start_row)
        except (ValueError, TypeError):
            app_logger.warning(f"无效的数据开始行: {start_row}，使用默认值1")
            start_row = 1
            
        app_logger.info(f"处理请求: 文件={file_path}, 工作表={sheet_name}, 列={columns}, 数据开始行={start_row}")
        
        try:
            # 读取Excel文件的所有工作表
            excel = pd.ExcelFile(file_path, engine='openpyxl')
            sheet_names = excel.sheet_names
            
            # 读取需要处理的工作表（不指定header，以便获取所有行）
            df_original = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
            
            # 获取原始行数（包括所有标题行和数据行）
            original_rows = len(df_original)
            app_logger.info(f"原始Excel文件行数: {original_rows}")
            
            # 确保start_row不超过文件行数
            if start_row > original_rows:
                app_logger.warning(f"数据开始行 {start_row} 超过文件总行数 {original_rows}，使用默认值1")
                start_row = 1
            
            # 读取实际数据（不使用列名）
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=start_row-1, engine='openpyxl')
            
            # 获取列数
            num_columns = len(df.columns)
            app_logger.info(f"读取到的列数: {num_columns}")
            
            # 检查columns是否为有效的列索引
            actual_column_indices = []
            for col in columns:
                # 记录收到的列值，便于调试
                app_logger.info(f"处理列值: {col}, 类型: {type(col)}")
                
                try:
                    # 尝试将列值转换为整数索引
                    if isinstance(col, int) or (isinstance(col, str) and col.isdigit()):
                        idx = int(col)
                        if 0 <= idx < num_columns:
                            actual_column_indices.append(idx)
                            app_logger.info(f"使用列索引: {idx}")
                        else:
                            app_logger.warning(f"列索引超出范围: {idx}, 有效范围: 0-{num_columns-1}")
                            return jsonify({"success": False, "message": f"列索引超出范围: {idx}, 有效范围: 0-{num_columns-1}"}), 400
                    # 如果是字符串但不是数字，可能是列名
                    elif isinstance(col, str):
                        # 对于非数字字符串，我们只能将其视为列索引错误
                        app_logger.warning(f"无法处理列名: {col}，请使用列索引（0-{num_columns-1}）")
                        return jsonify({"success": False, "message": f"无法处理列名: {col}，请使用列索引（0-{num_columns-1}）"}), 400
                    else:
                        app_logger.warning(f"无效的列标识: {col}")
                        return jsonify({"success": False, "message": f"无效的列标识: {col}"}), 400
                except Exception as e:
                    app_logger.error(f"处理列标识时出错: {col}, 错误: {str(e)}")
                    return jsonify({"success": False, "message": f"处理列标识 '{col}' 时出错: {str(e)}"}), 400
            
            if not actual_column_indices:
                app_logger.warning("没有有效的列被选择用于去重")
                return jsonify({"success": False, "message": "没有有效的列被选择用于去重"}), 400
                
            # 记录实际使用的列
            app_logger.info(f"使用列索引进行去重: {actual_column_indices}, 数据开始行: {start_row}")
            
            # 获取数据行数
            data_rows_before = len(df)
            app_logger.info(f"读取的数据行数: {data_rows_before}")
            
            # 保存原始数据副本，用于后续比较
            df_original_data = df.copy()
            
            # 识别重复行（保留第一个出现的记录，标记其余为重复）
            # 创建一个布尔掩码，True表示重复行，False表示非重复行
            duplicate_mask = df.duplicated(subset=actual_column_indices, keep='first')
            
            # 使用这个掩码找出所有重复行
            df_duplicates = df[duplicate_mask].copy()
            
            # 找出非重复行（也就是要保留的行）
            df_deduped = df[~duplicate_mask].copy()
            
            # 获取处理后的数据行数
            data_rows_after = len(df_deduped)
            app_logger.info(f"去重后数据行数: {data_rows_after}")
            
            # 移除的行数 = 原始数据行数 - 处理后数据行数
            removed_data_rows = data_rows_before - data_rows_after
            
            # 保留的行数 = 原始行数 - 移除的行数
            processed_rows = original_rows - removed_data_rows
            removed_rows = removed_data_rows
            
            app_logger.info(f"处理结果: 原始行数={original_rows}, 处理后行数={processed_rows}, 移除行数={removed_rows}, 重复行数={len(df_duplicates)}")
            
            # 确保保存目录存在
            os.makedirs(EXCEL_REPAIR_DIR, exist_ok=True)
            
            # 创建输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = os.path.basename(file_path)
            base_name, ext = os.path.splitext(filename)
            new_filename = f"{base_name}_dedup_{timestamp}{ext}"
            output_path = os.path.join(EXCEL_REPAIR_DIR, new_filename)
            
            # 创建一个ExcelWriter对象，用于写入多个工作表
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 复制原Excel的所有工作表
                for sheet in sheet_names:
                    # 读取原始工作表
                    original_sheet_data = pd.read_excel(file_path, sheet_name=sheet, header=None, engine='openpyxl')
                    # 保存到新Excel中
                    original_sheet_data.to_excel(writer, sheet_name=sheet, index=False, header=False)
                
                # 添加处理后的工作表（额外的工作表）
                sheet_index = 1
                new_sheet_name = f"已去重_{sheet_name}"
                
                # 检查是否存在同名工作表，如果存在则添加序号
                while new_sheet_name in sheet_names:
                    sheet_index += 1
                    new_sheet_name = f"已去重_{sheet_name}_{sheet_index}"
                
                # 保存处理后的工作表
                df_deduped.to_excel(writer, sheet_name=new_sheet_name, index=False, header=False)
                
                # 添加重复行工作表
                duplicates_sheet_name = f"重复行_{sheet_name}"
                
                # 检查是否存在同名工作表，如果存在则添加序号
                duplicates_sheet_index = 1
                while duplicates_sheet_name in sheet_names or duplicates_sheet_name == new_sheet_name:
                    duplicates_sheet_index += 1
                    duplicates_sheet_name = f"重复行_{sheet_name}_{duplicates_sheet_index}"
                
                # 保存重复行工作表
                df_duplicates.to_excel(writer, sheet_name=duplicates_sheet_name, index=False, header=False)
                
                # 创建修复信息工作表
                # 将列索引转换为Excel列标识（A, B, C...）
                def get_column_letter(idx):
                    result = ""
                    while idx >= 0:
                        result = chr(idx % 26 + 65) + result
                        idx = idx // 26 - 1
                    return result
                
                column_letters = [get_column_letter(idx) for idx in actual_column_indices]
                
                repair_info = pd.DataFrame({
                    '项目': ['原始行数', '处理后行数', '移除行数', '重复行数', '数据开始行', '处理时间', '操作类型', '处理的工作表', '去重列'],
                    '值': [
                        original_rows, 
                        processed_rows, 
                        removed_rows, 
                        len(df_duplicates),
                        f"第{start_row}行",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "字段去重",
                        sheet_name,
                        ', '.join(column_letters)
                    ]
                })
                
                # 保存修复信息工作表
                info_sheet_name = "修复信息"
                # 检查是否存在同名工作表，如果存在则添加序号
                info_sheet_index = 1
                while info_sheet_name in sheet_names or info_sheet_name == new_sheet_name or info_sheet_name == duplicates_sheet_name:
                    info_sheet_index += 1
                    info_sheet_name = f"修复信息_{info_sheet_index}"
                
                repair_info.to_excel(writer, sheet_name=info_sheet_name, index=False)
                
                # 设置所有工作表的格式，禁用科学计数法
                workbook = writer.book
                for sheet_name, worksheet in writer.sheets.items():
                    # 遍历所有列
                    for column in worksheet.columns:
                        for cell in column:
                            if isinstance(cell.value, (int, float)) and cell.data_type == 'n':
                                cell.number_format = '0'
            
            # 生成唯一ID，用于后续下载
            file_id = str(uuid.uuid4())
            processed_files[file_id] = {
                "output_path": output_path,
                "filename": new_filename,
                "original_rows": original_rows,
                "processed_rows": processed_rows,
                "removed_rows": removed_rows,
                "duplicate_rows": len(df_duplicates)
            }
            
            app_logger.info(f"Excel文件重复行去除完成: {file_path}, 原始行数: {original_rows}, 处理后行数: {processed_rows}, 移除行数: {removed_rows}, 重复行数: {len(df_duplicates)}, 数据开始行: {start_row}")
            
            return jsonify({
                "success": True,
                "message": "Excel文件处理完成",
                "file_id": file_id,
                "original_rows": original_rows,
                "processed_rows": processed_rows,
                "removed_rows": removed_rows,
                "duplicate_rows": len(df_duplicates),
                "download_url": url_for('excel_repair_api.download_file', file_id=file_id)
            })
            
        except Exception as e:
            app_logger.error(f"Excel文件重复行去除失败: {str(e)}")
            return jsonify({"success": False, "message": f"处理失败: {str(e)}"}), 500
    
    except Exception as e:
        app_logger.error(f"Excel文件重复行去除API错误: {str(e)}")
        return jsonify({"success": False, "message": f"处理失败: {str(e)}"}), 500

@excel_repair_api.route('/api/excel_repair/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """
    下载处理后的文件
    """
    try:
        if file_id not in processed_files:
            return jsonify({"success": False, "message": "文件不存在或已过期"}), 404
        
        file_info = processed_files[file_id]
        output_path = file_info.get('output_path')
        filename = file_info.get('filename')
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({"success": False, "message": "文件不存在"}), 404
        
        return send_file(output_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        app_logger.error(f"下载文件失败: {str(e)}")
        return jsonify({"success": False, "message": f"下载文件失败: {str(e)}"}), 500

@excel_repair_api.route('/api/excel_repair/files', methods=['GET'])
def list_excel_repair_files():
    """
    列出所有Excel修复文件
    """
    try:
        # 确保目录存在
        if not os.path.exists(EXCEL_REPAIR_DIR):
            os.makedirs(EXCEL_REPAIR_DIR, exist_ok=True)
            return jsonify({
                "success": True,
                "message": "目录为空",
                "files": []
            })
        
        # 获取所有Excel文件
        excel_files = []
        for file_ext in ['.xlsx', '.xls']:
            excel_files.extend(glob.glob(os.path.join(EXCEL_REPAIR_DIR, f"*{file_ext}")))
        
        # 生成文件信息列表
        file_list = []
        for file_path in sorted(excel_files, key=os.path.getmtime, reverse=True):
            filename = os.path.basename(file_path)
            file_time = os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
            
            # 文件类型标识（清除还是去重）
            file_type = "未知"
            if "_cleaned_" in filename:
                file_type = "空白行清除"
            elif "_dedup_" in filename:
                file_type = "字段去重"
            
            # 计算相对时间（几分钟前，几小时前等）
            time_diff = time.time() - file_time
            if time_diff < 60:
                relative_time = "刚刚"
            elif time_diff < 3600:
                minutes = int(time_diff / 60)
                relative_time = f"{minutes}分钟前"
            elif time_diff < 86400:
                hours = int(time_diff / 3600)
                relative_time = f"{hours}小时前"
            else:
                days = int(time_diff / 86400)
                relative_time = f"{days}天前"
            
            # 创建文件信息对象
            file_info = {
                "name": filename,
                "path": file_path,
                "size": file_size,
                "size_formatted": format_file_size(file_size),
                "modified": datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M:%S"),
                "relative_time": relative_time,
                "type": file_type,
                "download_url": url_for('excel_repair_api.download_direct_file', filename=filename)
            }
            
            file_list.append(file_info)
        
        return jsonify({
            "success": True,
            "message": f"找到 {len(file_list)} 个Excel修复文件",
            "files": file_list
        })
    
    except Exception as e:
        app_logger.error(f"获取Excel修复文件列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取文件列表失败: {str(e)}"
        }), 500

@excel_repair_api.route('/api/excel_repair/download/direct/<filename>', methods=['GET'])
def download_direct_file(filename):
    """
    直接下载指定名称的修复文件
    """
    try:
        # 检查文件名是否安全
        if '..' in filename or filename.startswith('/'):
            return jsonify({"success": False, "message": "不允许的文件名"}), 400
        
        # 构建完整文件路径
        file_path = os.path.join(EXCEL_REPAIR_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"success": False, "message": "文件不存在"}), 404
        
        # 返回文件供下载
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        app_logger.error(f"直接下载文件失败: {str(e)}")
        return jsonify({"success": False, "message": f"下载文件失败: {str(e)}"}), 500

# 辅助函数：格式化文件大小
def format_file_size(size_bytes):
    """
    将字节数格式化为人类可读的形式
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB" 