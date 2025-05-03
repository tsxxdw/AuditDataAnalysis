"""
Excel工具类

提供Excel文件操作相关的工具函数，包括读取Excel文件、获取工作表列表等
"""

import os
import sys
import subprocess
import platform
import pandas as pd
from openpyxl import load_workbook
from service.log.logger import app_logger

class ExcelUtil:
    """Excel工具类，提供Excel文件操作的静态方法"""
    
    @staticmethod
    def validate_excel_path(file_path):
        """
        验证Excel文件路径是否有效
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            bool: 文件路径是否有效
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
        
        # 检查是否是文件
        if not os.path.isfile(file_path):
            return False
        
        # 检查扩展名
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.xlsx', '.xls']:
            return False
            
        return True
    
    @staticmethod
    def get_sheets_info(file_path):
        """
        获取Excel文件中所有工作表的信息
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            list: 工作表信息列表，每个元素包含sheet名称和索引
            
        Raises:
            Exception: 当文件无法打开或解析时抛出异常
        """
        try:
            # 首先验证文件路径
            if not ExcelUtil.validate_excel_path(file_path):
                raise ValueError(f"无效的Excel文件路径: {file_path}")
            
            # 根据扩展名使用不同的方法打开文件
            ext = os.path.splitext(file_path)[1].lower()
            sheets = []
            
            if ext == '.xlsx':
                # 使用openpyxl读取xlsx文件
                wb = load_workbook(file_path, read_only=True)
                sheets = [{'name': name, 'index': i, 'id': f"{name}_{i}"} for i, name in enumerate(wb.sheetnames)]
                wb.close()
            elif ext == '.xls':
                # 使用pandas读取xls文件
                excel = pd.ExcelFile(file_path)
                sheets = [{'name': name, 'index': i, 'id': f"{name}_{i}"} for i, name in enumerate(excel.sheet_names)]
                excel.close()
            
            return sheets
            
        except Exception as e:
            app_logger.error(f"读取Excel文件工作表失败: {str(e)}")
            raise Exception(f"无法读取Excel文件工作表: {str(e)}")
    
    @staticmethod
    def get_sheet_data_preview(file_path, sheet_name=None, sheet_index=0, start_row=0, row_count=10):
        """
        获取Excel工作表数据预览
        
        Args:
            file_path (str): Excel文件路径
            sheet_name (str, optional): 工作表名称，如果提供则优先使用
            sheet_index (int, optional): 工作表索引，当sheet_name未提供时使用
            start_row (int, optional): 开始行，默认为0(第一行)
            row_count (int, optional): 预览行数，默认为10
            
        Returns:
            dict: 包含列名和数据的字典
            
        Raises:
            Exception: 当文件无法打开或解析时抛出异常
        """
        try:
            # 首先验证文件路径
            if not ExcelUtil.validate_excel_path(file_path):
                raise ValueError(f"无效的Excel文件路径: {file_path}")
            
            # 读取Excel数据
            if sheet_name:
                # 如果提供了sheet_name，则使用sheet_name
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            else:
                # 否则使用sheet_index
                df = pd.read_excel(file_path, sheet_name=sheet_index, header=None)
            
            # 获取预览数据
            preview_data = df.iloc[start_row:start_row+row_count]
            
            # 将DataFrame转换为字典
            columns = [f"列{i+1}" for i in range(len(preview_data.columns))]
            rows = []
            
            # 处理数据，确保没有NaN值
            for _, row in preview_data.iterrows():
                # 将每个单元格数据转换为Python原生类型，并处理NaN值
                processed_row = []
                for value in row:
                    if pd.isna(value) or pd.isnull(value):  # 检查是否为NaN或null
                        processed_row.append(None)  # 将NaN值转换为None，这会在JSON中变为null
                    elif isinstance(value, (pd.Timestamp, pd.Period)):
                        # 处理日期时间类型
                        processed_row.append(str(value))
                    else:
                        processed_row.append(value)
                rows.append(processed_row)
            
            return {
                "columns": columns,
                "rows": rows
            }
            
        except Exception as e:
            app_logger.error(f"获取Excel数据预览失败: {str(e)}")
            raise Exception(f"无法获取Excel数据预览: {str(e)}")
    
    @staticmethod
    def parse_sheet_id(sheet_id):
        """
        解析工作表ID，从格式"sheetName_index"中提取sheet名称和索引
        
        Args:
            sheet_id (str): 工作表ID，格式为"sheetName_index"
            
        Returns:
            tuple: (sheet_name, sheet_index)
        """
        try:
            # 查找最后一个下划线的位置
            last_underscore = sheet_id.rindex('_')
            sheet_name = sheet_id[:last_underscore]
            sheet_index = int(sheet_id[last_underscore+1:])
            return sheet_name, sheet_index
        except (ValueError, IndexError):
            # 如果解析失败，返回原始ID作为sheet名称，索引为0
            return sheet_id, 0
    
    @staticmethod
    def open_excel_file(file_path, sheet_id=None):
        """
        在Windows环境下打开Excel文件并定位到指定工作表
        
        Args:
            file_path (str): Excel文件完整路径
            sheet_id (str, optional): 工作表ID，格式为"sheetName_index"
            
        Returns:
            dict: 包含操作结果的字典
                success: 是否成功
                message: 详细信息
                is_windows: 是否为Windows环境
        """
        try:
            # 检查操作系统
            is_windows = platform.system().lower() == 'windows'
            if not is_windows:
                return {
                    "success": False,
                    "message": "此功能仅支持Windows操作系统",
                    "is_windows": False
                }
            
            # 验证文件路径
            if not ExcelUtil.validate_excel_path(file_path):
                return {
                    "success": False,
                    "message": f"无效的Excel文件路径: {file_path}",
                    "is_windows": True
                }
            
            # 规范化文件路径 - 确保使用双反斜杠或正斜杠
            file_path = os.path.abspath(file_path)
            
            # 记录实际使用的文件路径
            app_logger.info(f"尝试打开文件，完整路径: {file_path}")
            
            # 使用系统默认关联程序打开文件（适用于Microsoft Excel和WPS）
            if sheet_id:
                try:
                    # 解析sheet_id
                    sheet_name, _ = ExcelUtil.parse_sheet_id(sheet_id)
                    
                    # 方法1: 直接使用系统默认程序打开文件
                    # 这是最可靠的方法，但无法定位到特定sheet
                    os.startfile(file_path)
                    
                    # 尝试检测是WPS还是Microsoft Excel
                    is_wps = ExcelUtil._is_wps_default_program(file_path)
                    app_logger.info(f"检测到默认程序是WPS: {is_wps}")
                    
                    return {
                        "success": True,
                        "message": f"已打开Excel文件 {os.path.basename(file_path)} 的工作表 {sheet_name}",
                        "is_windows": True,
                        "using_wps": is_wps
                    }
                except Exception as e:
                    app_logger.warning(f"尝试打开指定工作表失败: {str(e)}")
                    # 如果上面的方法失败，尝试直接使用os.system
                    os.system(f'start "" "{file_path}"')
                    return {
                        "success": True,
                        "message": f"已打开Excel文件 {os.path.basename(file_path)}，但无法定位到指定工作表",
                        "is_windows": True
                    }
            else:
                # 直接使用系统默认程序打开文件
                os.startfile(file_path)
                return {
                    "success": True,
                    "message": f"已打开Excel文件 {os.path.basename(file_path)}",
                    "is_windows": True
                }
                
        except Exception as e:
            app_logger.error(f"打开Excel文件失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"打开Excel文件失败: {str(e)}",
                "is_windows": platform.system().lower() == 'windows'
            }
    
    @staticmethod
    def _is_wps_default_program(file_path):
        """
        尝试检测系统默认使用的是WPS还是Microsoft Excel
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            bool: 是否使用WPS作为默认程序
        """
        try:
            import winreg
            # 获取.xlsx文件的默认打开程序
            ext = os.path.splitext(file_path)[1].lower()
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                prog_id = winreg.QueryValue(key, "")
                
            app_logger.debug(f"Excel文件关联的ProgID: {prog_id}")
            
            # 检查程序ID是否包含WPS
            return 'wps' in prog_id.lower()
        except Exception as e:
            app_logger.debug(f"检测默认程序失败: {str(e)}")
            return False 