"""
Excel工具类

提供Excel文件操作相关的工具函数，包括读取Excel文件、获取工作表列表等
"""

import os
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
            
            for _, row in preview_data.iterrows():
                rows.append(row.tolist())
            
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