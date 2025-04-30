from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
from utils.log.logger import reload_log_config, app_logger

log_settings_bp = Blueprint('log_settings', __name__, url_prefix='/api/settings/log')

# 配置文件路径
LOG_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'config', 'settings', 'log_config.json')

@log_settings_bp.route('/get', methods=['GET'])
def get_log_settings():
    """获取日志设置"""
    try:
        if not os.path.exists(LOG_CONFIG_PATH):
            # 如果配置文件不存在，创建默认配置
            default_config = {
                "log_path": "logs",
                "last_updated": ""
            }
            with open(LOG_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return jsonify({"success": True, "data": default_config})
        
        # 读取配置文件
        with open(LOG_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({"success": True, "data": config})
    except Exception as e:
        app_logger.error(f"获取日志设置失败: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"获取日志设置失败: {str(e)}"}), 500

@log_settings_bp.route('/save', methods=['POST'])
def save_log_settings():
    """保存日志设置"""
    try:
        data = request.json
        log_path = data.get('log_path')
        
        if not log_path:
            return jsonify({"success": False, "message": "日志路径不能为空"}), 400
        
        # 读取现有配置
        if os.path.exists(LOG_CONFIG_PATH):
            with open(LOG_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 更新配置
        config['log_path'] = log_path
        config['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 确保设置的路径存在
        log_dir = os.path.abspath(log_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # 保存配置
        with open(LOG_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        # 重新加载日志配置
        reload_log_config()
        
        app_logger.info(f"日志设置已更新，路径: {log_path}")
        return jsonify({"success": True, "message": "日志设置已保存"})
    except Exception as e:
        app_logger.error(f"保存日志设置失败: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"保存日志设置失败: {str(e)}"}), 500 