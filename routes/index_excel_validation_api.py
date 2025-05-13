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
                else:
                    # 如果索引超出范围，创建一个特殊标记
                    file_info["sheetExists"] = False
                    file_info["requestedSheetIndex"] = sheet_index + 1  # 转回1基索引用于显示
                    # 默认使用第一个工作表
                    file_info["currentSheet"] = sheets_info[0] if sheets_info else None
                    
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
    return str_value.replace(" ", "").lower()

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
        read_row_index (int): 表头所在行的索引
        
    Returns:
        dict: 包含分组信息和不一致问题的字典
    """
    app_logger.info(f"开始校验表头一致性，表头行索引: {read_row_index}")
    
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
            
            # 读取指定行的数据（表头）
            try:
                # 读取单行数据作为表头
                headers_data = ExcelUtil.read_excel_data(
                    file_path=file_path,
                    sheet_name=sheet_name,
                    sheet_index=sheet_index,
                    start_row=read_row_index,
                    row_limit=1,
                    ignore_empty_rows=False
                )
                
                if not headers_data or len(headers_data) == 0:
                    app_logger.warning(f"未读取到表头数据: {file_path}, sheet: {sheet_name}")
                    continue
                
                # 原始表头值（用于显示）
                original_headers = headers_data[0]
                
                # 存储这个文件的表头信息和文件名
                files_headers.append({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'sheet_name': sheet_name,
                    'headers': original_headers,  # 原始表头值
                    'normalized_headers': [normalize_header_value(h) for h in original_headers],  # 标准化后的表头
                    'header_key': get_header_key(original_headers)  # 用于分组的键
                })
                
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
                'sheet_name': file_header['sheet_name']
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
        
        # 只有当存在多个不同的表头组时才需要比较
        if len(groups) > 1:
            # 以第一个组（文件数量最多的组）作为参考
            reference_group = groups[0]
            reference_headers = reference_group['headers']
            
            # 与其他组比较
            for i in range(1, len(groups)):
                compare_group = groups[i]
                compare_headers = compare_group['headers']
                
                # 表头长度不一致，记录问题
                if len(reference_headers) != len(compare_headers):
                    issues.append({
                        "location": "表头",
                        "type": "表头数量不一致",
                        "message": f"组1的表头数量({len(reference_headers)})与组{i+1}的表头数量({len(compare_headers)})不一致",
                        "groups": [1, i+1]
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
                        
                        issues.append({
                            "location": f"{col_letter}{read_row_index + 1}",
                            "type": "表头不一致",
                            "message": f"列 {col_letter} 的表头在组1中为 '{ref_str}'，而在组{i+1}中为 '{comp_str}'",
                            "groups": [1, i+1]
                        })
        
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