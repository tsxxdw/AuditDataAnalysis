"""
全局配置模块

存储全局配置参数，如项目根路径等
"""

import os

# 项目根路径（将在应用启动时设置）
PROJECT_ROOT = None

def init_project_root():
    """
    初始化项目根路径
    
    基于main.py文件的位置确定项目根目录
    """
    global PROJECT_ROOT
    
    # main.py所在目录就是项目根目录
    main_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))
    if os.path.exists(main_file_path):
        PROJECT_ROOT = os.path.dirname(main_file_path)
    else:
        # 尝试其他方法确定项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(os.path.dirname(current_dir))  # config -> 项目根目录
    
    return PROJECT_ROOT

def get_project_root():
    """
    获取项目根路径
    
    Returns:
        str: 项目根路径
    """
    global PROJECT_ROOT
    if PROJECT_ROOT is None:
        return init_project_root()
    return PROJECT_ROOT

def get_export_dir():
    """
    获取导出目录路径
    
    Returns:
        str: 导出目录路径
    """
    export_dir = os.path.join(get_project_root(), 'export')
    
    # 确保目录存在
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    return export_dir 