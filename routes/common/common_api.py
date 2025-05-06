"""
通用API模块

提供系统级别的通用API接口
"""

from flask import Blueprint, jsonify
from service.log.logger import app_logger
from utils.database_config_util import DatabaseConfigUtil

# 创建蓝图
common_api_bp = Blueprint('common_api', __name__, url_prefix='/api/common')

@common_api_bp.route('/database_info', methods=['GET'])
def get_database_info():
    """获取当前连接的数据库信息
    
    Returns:
        JSON: 包含当前数据库类型和名称的信息
    """
    try:
        # 获取默认数据库类型
        db_type = DatabaseConfigUtil.get_default_db_type()
        
        # 获取数据库配置
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        # 获取数据库名称
        db_name = db_config.get('database', '') if db_config else ''
        
        # 获取数据库类型的显示名称
        db_type_display = DatabaseConfigUtil.get_db_display_name(db_type)
        
        return jsonify({
            "success": True,
            "db_type": db_type_display,
            "db_name": db_name
        })
    except Exception as e:
        app_logger.error(f"获取数据库信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取数据库信息失败: {str(e)}"
        }), 500 