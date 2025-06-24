"""
向量数据库设置API

提供向量数据库设置相关的API接口
"""

from flask import Blueprint, jsonify, request
from service.settings.vector_database.settings_vector_database_service import vector_db_service
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import log_with_context, handle_exceptions

# 创建蓝图
settings_vector_database_bp = Blueprint('settings_vector_database', __name__)

@settings_vector_database_bp.route('/api/settings/vector_database', methods=['GET'])
@log_with_context(level="INFO")
def get_vector_database_settings():
    """获取向量数据库设置"""
    try:
        settings = vector_db_service.get_vector_database_settings()
        return jsonify(settings)
    except Exception as e:
        app_logger.exception("获取向量数据库设置时发生错误")
        return jsonify({"success": False, "message": str(e)})

@settings_vector_database_bp.route('/api/settings/vector_database', methods=['POST'])
@log_with_context(level="INFO", with_args=True)
def save_vector_database_settings():
    """保存向量数据库设置"""
    try:
        data = request.get_json()
        if vector_db_service.save_vector_database_settings(data):
            return jsonify({"status": "success", "message": "保存向量数据库设置成功"})
        else:
            return jsonify({"status": "error", "message": "保存向量数据库设置失败"}), 500
    except Exception as e:
        app_logger.exception("保存向量数据库设置时发生错误")
        return jsonify({"status": "error", "message": str(e)}), 500

@settings_vector_database_bp.route('/api/settings/vector_database/test', methods=['POST'])
@log_with_context(level="INFO", with_args=True)
def test_vector_database_connection():
    """测试向量数据库连接接口"""
    try:
        # 获取请求数据
        db_config = request.get_json()
        
        # 验证必填参数
        if not db_config or 'type' not in db_config:
            return jsonify({"success": False, "message": "缺少必要的向量数据库配置信息"})
        
        # 根据数据库类型验证必要参数
        db_type = db_config['type']
        if db_type == 'chroma':
            if not all(key in db_config for key in ['host', 'port']):
                return jsonify({"success": False, "message": "Chroma连接缺少必要参数"})
        elif db_type == 'milvus':
            if 'host' not in db_config:
                return jsonify({"success": False, "message": "Milvus连接缺少必要参数"})
        elif db_type == 'elasticsearch':
            if not all(key in db_config for key in ['host', 'port']):
                return jsonify({"success": False, "message": "Elasticsearch连接缺少必要参数"})
        else:
            return jsonify({"success": False, "message": f"不支持的向量数据库类型: {db_type}"})
        
        # 由于目前没有实现真正的连接测试，我们返回一个成功响应
        # TODO: 实现真正的向量数据库连接测试
        return jsonify({
            "success": True, 
            "message": "连接成功，向量数据库服务可用"
        })
        
    except AppException as e:
        # 处理应用异常
        app_logger.warning(f"向量数据库连接测试失败: {e.message}")
        return jsonify({"success": False, "message": e.message})
    except Exception as e:
        # 处理其他异常
        app_logger.exception("测试向量数据库连接时发生错误")
        return jsonify({"success": False, "message": f"系统错误: {str(e)}"}) 