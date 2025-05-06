"""
文件工具模块

提供文件操作相关的工具函数
"""

import os
from flask import current_app
from service.log.logger import app_logger
from config.global_config import get_export_dir

def is_safe_file_path(file_path):
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

def ensure_export_directory():
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