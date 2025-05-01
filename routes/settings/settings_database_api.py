"""
数据库设置API

提供数据库设置相关的API接口
"""

from flask import Blueprint, jsonify, request
from service.settings.database.settings_database_service import db_service
from service.database import DatabaseService
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import log_with_context, handle_exceptions

# 创建蓝图
settings_database_bp = Blueprint('settings_database', __name__)

@settings_database_bp.route('/api/settings/database', methods=['GET'])
@log_with_context(level="INFO")
def get_database_settings():
    """获取数据库设置"""
    try:
        settings = db_service.get_database_settings()
        return jsonify(settings)
    except Exception as e:
        app_logger.exception("获取数据库设置时发生错误")
        return jsonify({"success": False, "message": str(e)})

@settings_database_bp.route('/api/settings/database', methods=['POST'])
@log_with_context(level="INFO", with_args=True)
def save_database_settings():
    """保存数据库设置"""
    try:
        data = request.get_json()
        if db_service.save_database_settings(data):
            return jsonify({"status": "success", "message": "保存数据库设置成功"})
        else:
            return jsonify({"status": "error", "message": "保存数据库设置失败"}), 500
    except Exception as e:
        app_logger.exception("保存数据库设置时发生错误")
        return jsonify({"status": "error", "message": str(e)}), 500

@settings_database_bp.route('/api/settings/database/test', methods=['POST'])
@log_with_context(level="INFO", with_args=True)
def test_database_connection():
    """测试数据库连接接口"""
    try:
        # 获取请求数据
        db_config = request.get_json()
        
        # 验证必填参数
        if not db_config or 'type' not in db_config:
            return jsonify({"success": False, "message": "缺少必要的数据库配置信息"})
        
        # 根据数据库类型验证必要参数
        db_type = db_config['type']
        if db_type == 'mysql':
            if not all(key in db_config for key in ['host', 'database']):
                return jsonify({"success": False, "message": "MySQL连接缺少必要参数"})
        elif db_type == 'sqlserver':
            if not all(key in db_config for key in ['host', 'database']):
                return jsonify({"success": False, "message": "SQL Server连接缺少必要参数"})
        elif db_type == 'oracle':
            if not all(key in db_config for key in ['host', 'service', 'username', 'password']):
                return jsonify({"success": False, "message": "Oracle连接缺少必要参数"})
        else:
            return jsonify({"success": False, "message": f"不支持的数据库类型: {db_type}"})
        
        # 调用数据库连接测试服务
        db_service = DatabaseService()
        db_service.test_connection(db_config)
        
        return jsonify({
            "success": True, 
            "message": "连接成功，数据库服务可用"
        })
        
    except AppException as e:
        # 处理应用异常
        app_logger.warning(f"数据库连接测试失败: {e.message}")
        return jsonify({"success": False, "message": e.message})
    except Exception as e:
        # 处理其他异常
        app_logger.exception("测试数据库连接时发生错误")
        return jsonify({"success": False, "message": f"系统错误: {str(e)}"})

def register_routes(app):
    """注册路由"""
    
    @app.route('/api/settings/database/save', methods=['POST'])
    @log_with_context(level="INFO", with_args=True)
    def save_database_settings():
        """保存数据库设置"""
        try:
            # 获取请求数据
            data = request.get_json()
            
            if not data:
                return jsonify({"success": False, "message": "未提供数据"})
            
            # 处理保存逻辑
            # ...
            
            return jsonify({"success": True})
            
        except Exception as e:
            app_logger.exception("保存数据库设置时发生错误")
            return jsonify({"success": False, "message": str(e)})
    
    @app.route('/api/settings/database/test', methods=['POST'])
    @log_with_context(level="INFO", with_args=True)
    def test_database_connection():
        """测试数据库连接接口"""
        try:
            # 获取请求数据
            db_config = request.get_json()
            
            # 验证必填参数
            if not db_config or 'type' not in db_config:
                return jsonify({"success": False, "message": "缺少必要的数据库配置信息"})
            
            # 根据数据库类型验证必要参数
            db_type = db_config['type']
            if db_type == 'mysql':
                if not all(key in db_config for key in ['host', 'database']):
                    return jsonify({"success": False, "message": "MySQL连接缺少必要参数"})
            elif db_type == 'sqlserver':
                if not all(key in db_config for key in ['host', 'database']):
                    return jsonify({"success": False, "message": "SQL Server连接缺少必要参数"})
            elif db_type == 'oracle':
                if not all(key in db_config for key in ['host', 'service', 'username', 'password']):
                    return jsonify({"success": False, "message": "Oracle连接缺少必要参数"})
            else:
                return jsonify({"success": False, "message": f"不支持的数据库类型: {db_type}"})
            
            # 调用数据库连接测试服务
            db_service = DatabaseService()
            db_service.test_connection(db_config)
            
            return jsonify({
                "success": True, 
                "message": "连接成功，数据库服务可用"
            })
            
        except AppException as e:
            # 处理应用异常
            app_logger.warning(f"数据库连接测试失败: {e.message}")
            return jsonify({"success": False, "message": e.message})
        except Exception as e:
            # 处理其他异常
            app_logger.exception("测试数据库连接时发生错误")
            return jsonify({"success": False, "message": f"系统错误: {str(e)}"})
    
    @app.route('/api/settings/database/get', methods=['GET'])
    @log_with_context(level="INFO")
    def get_database_settings():
        """获取数据库设置"""
        try:
            # 处理获取逻辑
            # ...
            
            return jsonify({
                "success": True,
                "data": {
                    "default_db": "mysql",
                    "connections": {
                        "mysql": {
                            "host": "localhost",
                            "port": "3306",
                            "database": "audit_db"
                        }
                    }
                }
            })
            
        except Exception as e:
            app_logger.exception("获取数据库设置时发生错误")
            return jsonify({"success": False, "message": str(e)}) 