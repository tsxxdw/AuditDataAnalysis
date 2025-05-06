"""
通用API模块

提供系统级别的通用API接口
"""

from flask import Blueprint, jsonify, request
from service.log.logger import app_logger
from utils.database_config_util import DatabaseConfigUtil

# 创建通用API蓝图
common_api_bp = Blueprint('common_api', __name__, url_prefix='/api/common')

@common_api_bp.route('/database_info', methods=['GET'])
def get_database_info():
    """获取当前数据库类型和名称"""
    app_logger.info("获取当前数据库信息")
    
    try:
        # 获取当前数据库连接信息
        db_type = DatabaseConfigUtil.get_default_db_type()
        db_config = DatabaseConfigUtil.get_database_config(db_type)
        
        if not db_config:
            return jsonify({
                "success": False, 
                "message": "获取数据库配置失败", 
                "db_type": "未知", 
                "db_name": "未知"
            }), 500
        
        db_name = db_config.get('database', '未知')
        
        return jsonify({
            "success": True,
            "message": "获取数据库信息成功", 
            "db_type": db_type,
            "db_name": db_name
        })
        
    except Exception as e:
        app_logger.error(f"获取数据库信息失败: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"获取数据库信息失败: {str(e)}", 
            "db_type": "未知", 
            "db_name": "未知"
        }), 500 