"""
EXCEL校验API模块

处理Excel文件校验、获取工作表列表等API接口
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from service.log.logger import app_logger
from utils.excel_util import ExcelUtil

# 创建蓝图
excel_validation_bp = Blueprint('excel_validation', __name__)

@excel_validation_bp.route('/api/excel/get_sheets', methods=['POST'])
def get_sheets():
    """获取Excel文件的工作表列表"""
    app_logger.info("获取Excel工作表列表")
    
    try:
        # 获取请求数据
        data = request.json
        file_path = data.get('filePath')
        
        # 验证文件路径
        if not file_path:
            return jsonify({
                "success": False,
                "message": "未提供文件路径"
            }), 400
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "message": "文件不存在"
            }), 404
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.xlsx', '.xls']:
            return jsonify({
                "success": False,
                "message": "不支持的文件类型，请选择.xlsx或.xls文件"
            }), 400
        
        # 使用ExcelUtil获取工作表信息
        sheets_info = ExcelUtil.get_sheets_info(file_path)
        
        return jsonify({
            "success": True,
            "message": "获取工作表成功",
            "sheets": sheets_info
        })
        
    except Exception as e:
        app_logger.error(f"获取工作表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取工作表失败: {str(e)}"
        }), 500

@excel_validation_bp.route('/api/excel/load_files_info', methods=['POST'])
def load_files_info():
    """加载多个Excel文件的信息"""
    app_logger.info("加载Excel文件信息")
    
    try:
        # 获取请求数据
        data = request.json
        file_paths = data.get('filePaths', [])
        sheet_index = data.get('sheetIndex')
        
        if not file_paths:
            return jsonify({
                "success": False,
                "message": "未提供文件路径"
            }), 400
            
        if not sheet_index:
            return jsonify({
                "success": False,
                "message": "未提供工作表序号"
            }), 400
        
        # 转换为整数
        try:
            sheet_index = int(sheet_index) - 1  # 转为0基索引
            if sheet_index < 0:
                raise ValueError("工作表序号必须大于0")
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": f"无效的工作表序号: {str(e)}"
            }), 400
        
        # 加载每个文件的信息
        files_info = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                app_logger.warning(f"文件不存在: {file_path}")
                continue
                
            try:
                # 获取该文件的所有工作表
                sheets_info = ExcelUtil.get_sheets_info(file_path)
                
                # 日志记录实际获取的工作表信息
                app_logger.info(f"文件 {os.path.basename(file_path)} 包含 {len(sheets_info)} 个工作表")
                for sheet in sheets_info:
                    app_logger.info(f"  - 工作表: {sheet['name']}, 索引: {sheet['index']}")
                
                # 创建文件信息
                file_info = {
                    "filePath": file_path,
                    "fileName": os.path.basename(file_path),
                    "sheets": sheets_info,
                    "currentSheet": None,
                    "sheetExists": True
                }
                
                # 尝试获取指定索引的工作表
                if 0 <= sheet_index < len(sheets_info):
                    file_info["currentSheet"] = sheets_info[sheet_index]
                    app_logger.info(f"文件 {os.path.basename(file_path)} 选择工作表: {sheets_info[sheet_index]['name']}")
                else:
                    # 如果索引超出范围，创建一个特殊标记
                    file_info["sheetExists"] = False
                    file_info["requestedSheetIndex"] = sheet_index + 1  # 转回1基索引用于显示
                    # 默认使用第一个工作表
                    file_info["currentSheet"] = sheets_info[0] if sheets_info else None
                    app_logger.warning(f"文件 {os.path.basename(file_path)} 不存在第 {sheet_index + 1} 个工作表，最大索引为 {len(sheets_info)}")
                    
                files_info.append(file_info)
                    
            except Exception as e:
                app_logger.error(f"处理文件失败: {file_path}, 错误: {str(e)}")
                # 继续处理下一个文件
        
        if not files_info:
            return jsonify({
                "success": False,
                "message": "没有有效的Excel文件"
            }), 400
        
        return jsonify({
            "success": True,
            "message": "加载Excel文件信息成功",
            "filesInfo": files_info
        })
        
    except Exception as e:
        app_logger.error(f"加载Excel文件信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"加载Excel文件信息失败: {str(e)}"
        }), 500

@excel_validation_bp.route('/api/excel/validate', methods=['POST'])
def validate_excel():
    """校验Excel文件"""
    app_logger.info("校验Excel文件")
    
    try:
        # 获取请求数据
        data = request.json
        files_info = data.get('filesInfo', [])
        read_row = data.get('readRow')
        validation_type = data.get('validationType')
        
        # 验证参数
        if not files_info:
            return jsonify({
                "success": False,
                "message": "未提供文件信息"
            }), 400
            
        if not read_row:
            return jsonify({
                "success": False,
                "message": "未提供读取行号"
            }), 400
            
        if not validation_type:
            return jsonify({
                "success": False,
                "message": "未提供校验类型"
            }), 400
        
        # 将读取行转为整数
        try:
            read_row_index = int(read_row) - 1  # 转为0基索引
            if read_row_index < 0:
                raise ValueError("读取行必须大于0")
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": f"无效的读取行: {str(e)}"
            }), 400
        
        # 根据校验类型执行相应的校验
        result = {}
        
        if validation_type == "header_validation":
            # 执行表头一致性校验，返回分组结果
            result = validate_headers(files_info, read_row_index)
        else:
            return jsonify({
                "success": False,
                "message": f"不支持的校验类型: {validation_type}"
            }), 400
        
        # 生成汇总信息
        summary = {
            "total_files": len(files_info),
            "total_issues": len(result.get("issues", [])),
            "total_groups": result.get("total_groups", 0),
            "pass_rate": 100 if len(result.get("issues", [])) == 0 else round(100 - (len(result.get("issues", [])) / max(1, len(files_info)) * 100), 2)
        }
        
        # 返回包含分组信息和问题列表的结果
        return jsonify({
            "success": True,
            "message": "Excel校验完成",
            "summary": summary,
            "groups": result.get("groups", []),
            "issues": result.get("issues", [])
        })
        
    except Exception as e:
        app_logger.error(f"Excel校验失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Excel校验失败: {str(e)}"
        }), 500

def normalize_header_value(value):
    """
    标准化表头值，用于比较
    
    - 将None转为空字符串
    - 将数值类型转为字符串
    - 对字符串类型去除所有空白（包括中间的空白）并转为小写
    
    Args:
        value: 任意类型的表头值
        
    Returns:
        str: 标准化后的字符串
    """
    if value is None:
        return ""
    
    # 将值转为字符串
    str_value = str(value)
    
    # 去除所有空白（包括中间的空白）并转为小写
    normalized = str_value.replace(" ", "").lower()
    
    # 记录调试信息
    app_logger.debug(f"标准化表头值: 原始值 [{value}]({type(value)}) -> 标准化后 [{normalized}]")
    
    return normalized

def get_header_key(headers):
    """
    生成表头的唯一键，用于分组
    将每个表头值标准化后连接
    
    Args:
        headers (list): 表头值列表
        
    Returns:
        str: 表头键
    """
    return "__".join([normalize_header_value(h) for h in headers])

def validate_headers(files_info, read_row_index):
    """
    校验多个Excel文件中指定行的表头是否一致，并将相同表头的文件分组
    
    Args:
        files_info (list): 文件信息列表
        read_row_index (int): 默认表头所在行的索引，如果文件中指定了readRow则优先使用
        
    Returns:
        dict: 包含分组信息和不一致问题的字典
    """
    app_logger.info(f"开始校验表头一致性，默认表头行索引: {read_row_index}")
    
    if len(files_info) < 2:
        app_logger.info("文件数量少于2个，无需进行表头一致性校验")
        return {
            "groups": [],
            "issues": []
        }
    
    try:
        # 第一步：读取每个文件指定工作表的表头行
        files_headers = []
        
        for file_info in files_info:
            file_path = file_info.get('filePath')
            current_sheet = file_info.get('currentSheet')
            
            if not file_path or not current_sheet:
                app_logger.warning(f"文件信息不完整，跳过: {file_info}")
                continue
                
            # 获取工作表名称和索引
            sheet_name = current_sheet.get('name')
            sheet_index = current_sheet.get('index')
            
            if sheet_name is None or sheet_index is None:
                app_logger.warning(f"工作表信息不完整，跳过: {current_sheet}")
                continue
            
            # 获取每个文件的读取行，如果存在则优先使用
            file_read_row = file_info.get('readRow')
            if file_read_row:
                try:
                    file_read_row_index = int(file_read_row) - 1  # 转为0基索引
                    if file_read_row_index < 0:
                        raise ValueError("读取行必须大于0")
                    current_read_row_index = file_read_row_index
                except (ValueError, TypeError):
                    app_logger.warning(f"文件 {file_path} 指定的读取行无效: {file_read_row}，使用默认值: {read_row_index+1}")
                    current_read_row_index = read_row_index
            else:
                current_read_row_index = read_row_index
            
            # 读取指定行的数据（表头）
            try:
                # 读取单行数据作为表头
                headers_data = ExcelUtil.read_excel_data(
                    file_path=file_path,
                    sheet_name=sheet_name,
                    sheet_index=sheet_index,
                    start_row=current_read_row_index,
                    row_limit=1,
                    ignore_empty_rows=False
                )
                
                if not headers_data or len(headers_data) == 0:
                    app_logger.warning(f"未读取到表头数据: {file_path}, sheet: {sheet_name}, 行: {current_read_row_index+1}")
                    
                    # 创建一个空白表头记录，而不是跳过这个文件
                    app_logger.info(f"为未读取到的表头创建空白表头记录: {file_path}, sheet: {sheet_name}, 行: {current_read_row_index+1}")
                    original_headers = []  # 空数组
                    
                    # 存储这个文件的空白表头信息
                    files_headers.append({
                        'file_path': file_path,
                        'file_name': os.path.basename(file_path),
                        'sheet_name': sheet_name,
                        'headers': original_headers,  # 空数组作为表头
                        'normalized_headers': [],  # 空数组
                        'header_key': "__EMPTY_HEADER__",  # 特殊键用于分组
                        'read_row_index': current_read_row_index  # 记录使用的读取行索引，用于显示问题位置
                    })
                    
                    app_logger.info(f"已为文件 {os.path.basename(file_path)} 创建空白表头记录")
                    continue  # 继续处理下一个文件
                
                # 原始表头值（用于显示）
                original_headers = headers_data[0]
                
                # 存储这个文件的表头信息和文件名
                files_headers.append({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'sheet_name': sheet_name,
                    'headers': original_headers,  # 原始表头值
                    'normalized_headers': [normalize_header_value(h) for h in original_headers],  # 标准化后的表头
                    'header_key': get_header_key(original_headers),  # 用于分组的键
                    'read_row_index': current_read_row_index  # 记录使用的读取行索引，用于显示问题位置
                })
                
                app_logger.info(f"成功读取文件 {os.path.basename(file_path)} 的表头，工作表: {sheet_name}, 行: {current_read_row_index+1}")
                
            except Exception as e:
                app_logger.error(f"读取表头失败: {file_path}, sheet: {sheet_name}, 错误: {str(e)}")
                continue
        
        # 第二步：将文件按表头分组
        if len(files_headers) < 2:
            app_logger.info("有效文件数量少于2个，无需进行表头一致性校验")
            return {
                "groups": [],
                "issues": []
            }
        
        # 按表头内容分组
        header_groups = {}
        
        for file_header in files_headers:
            header_key = file_header['header_key']
            if header_key not in header_groups:
                header_groups[header_key] = {
                    'headers': file_header['headers'],
                    'normalized_headers': file_header['normalized_headers'],
                    'files': []
                }
            
            header_groups[header_key]['files'].append({
                'file_path': file_header['file_path'],
                'file_name': file_header['file_name'],
                'sheet_name': file_header['sheet_name'],
                'read_row_index': file_header['read_row_index']
            })
        
        # 转换为列表格式，方便前端处理
        groups = []
        for i, (header_key, group) in enumerate(header_groups.items()):
            groups.append({
                'group_id': i + 1,
                'headers': group['headers'],
                'files': group['files'],
                'file_count': len(group['files'])
            })
        
        # 按文件数量降序排序，通常最多的那组是"正确"的表头
        groups.sort(key=lambda x: x['file_count'], reverse=True)
        
        # 第三步：生成不一致问题列表
        issues = []
        
        # 添加辅助函数判断是否为空白行分组
        def is_empty_headers_group(headers):
            """判断一个表头组是否为空白行组（所有单元格为空或数组为空）"""
            # 记录原始头部值用于调试
            app_logger.debug(f"检查是否为空白行分组，头部值: {headers}")
            
            # 空数组直接视为空白行分组
            if not headers or len(headers) == 0:
                app_logger.debug("发现空数组表头，视为空白行分组")
                return True
            
            is_empty = all(normalize_header_value(h) == "" for h in headers)
            app_logger.debug(f"空白行分组检查结果: {is_empty}")
            
            return is_empty
        
        # 只有当存在多个不同的表头组时才需要比较
        if len(groups) > 1:
            # 找出所有非空白行分组
            non_empty_groups = []
            empty_groups = []
            
            for group_index, group in enumerate(groups):
                if is_empty_headers_group(group['headers']):
                    empty_groups.append(group)
                    app_logger.info(f"发现空白行分组: 组 {group_index + 1}，包含 {group['file_count']} 个文件")
                else:
                    non_empty_groups.append(group)
            
            # 只有当存在多个非空白分组时才比较它们
            if len(non_empty_groups) > 1:
                # 以第一个非空白组作为参考
                reference_group = non_empty_groups[0]
                reference_headers = reference_group['headers']
                reference_group_original_index = groups.index(reference_group) + 1  # 原始组索引
                
                # 与其他非空白组比较
                for i, compare_group in enumerate(non_empty_groups[1:], 1):
                    compare_headers = compare_group['headers']
                    compare_group_original_index = groups.index(compare_group) + 1  # 原始组索引
                    
                    # 表头长度不一致，记录问题
                    if len(reference_headers) != len(compare_headers):
                        issues.append({
                            "location": "表头",
                            "type": "表头数量不一致",
                            "message": f"组{reference_group_original_index}的表头数量({len(reference_headers)})与组{compare_group_original_index}的表头数量({len(compare_headers)})不一致",
                            "groups": [reference_group_original_index, compare_group_original_index]
                        })
                    
                    # 取两者中较短的长度进行比较
                    compare_length = min(len(reference_headers), len(compare_headers))
                    
                    # 比较每个表头字段（标准化后）
                    for col_index in range(compare_length):
                        ref_header = reference_headers[col_index]
                        comp_header = compare_headers[col_index]
                        
                        # 标准化表头值用于比较
                        ref_norm = normalize_header_value(ref_header)
                        comp_norm = normalize_header_value(comp_header)
                        
                        # 检查标准化后的表头是否一致
                        if ref_norm != comp_norm:
                            # 使用原始值显示
                            ref_str = str(ref_header) if ref_header is not None else "(空)"
                            comp_str = str(comp_header) if comp_header is not None else "(空)"
                            
                            # Excel列编号（A, B, C...）
                            col_letter = get_column_letter(col_index)
                            
                            # 获取参考组和比较组的第一个文件的读取行位置用于显示
                            ref_row = reference_group['files'][0]['read_row_index'] + 1 if reference_group['files'] else read_row_index + 1
                            comp_row = compare_group['files'][0]['read_row_index'] + 1 if compare_group['files'] else read_row_index + 1
                            
                            issues.append({
                                "location": f"{col_letter}{ref_row}/{col_letter}{comp_row}",
                                "type": "表头不一致",
                                "message": f"列 {col_letter} 的表头在组{reference_group_original_index}中为 '{ref_str}'，而在组{compare_group_original_index}中为 '{comp_str}'",
                                "groups": [reference_group_original_index, compare_group_original_index]
                            })
                
                app_logger.info(f"非空白行分组比较完成，发现 {len(issues)} 个问题")
            else:
                app_logger.info("只存在一个非空白行分组，无需进行表头一致性校验")
                
            # 记录空白行分组信息，但不参与比较
            if empty_groups:
                app_logger.info(f"存在 {len(empty_groups)} 个空白行分组，这些分组不参与表头差异比较")
                
            # 重新排序组，将空白行分组放到最前面（前端会再次排序）
            groups_reordered = empty_groups + non_empty_groups
            groups = groups_reordered
        
        result = {
            "groups": groups,
            "issues": issues,
            "total_groups": len(groups)
        }
        
        app_logger.info(f"表头一致性校验完成，发现 {len(issues)} 个问题，共 {len(groups)} 个不同的表头组")
        return result
        
    except Exception as e:
        app_logger.error(f"表头一致性校验失败: {str(e)}")
        raise

def get_column_letter(column_index):
    """
    将列索引转换为Excel列名（A, B, C, ..., Z, AA, AB, ...）
    
    Args:
        column_index (int): 列索引（从0开始）
        
    Returns:
        str: Excel列名
    """
    result = ""
    
    while column_index >= 0:
        remainder = column_index % 26
        result = chr(65 + remainder) + result
        column_index = (column_index // 26) - 1
        
        if column_index < 0:
            break
    
    return result 