from flask import Blueprint, jsonify, request
from service.settings.database.settings_database_service import db_service

# 创建蓝图
settings_database_bp = Blueprint('settings_database', __name__)

@settings_database_bp.route('/api/settings/database', methods=['GET'])
def get_database_settings():
    """获取数据库设置"""
    settings = db_service.get_database_settings()
    return jsonify(settings)

@settings_database_bp.route('/api/settings/database', methods=['POST'])
def save_database_settings():
    """保存数据库设置"""
    try:
        settings_data = request.json
        success = db_service.save_database_settings(settings_data)
        if success:
            return jsonify({"status": "success", "message": "数据库设置已保存"})
        else:
            return jsonify({"status": "error", "message": "保存数据库设置失败"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500 