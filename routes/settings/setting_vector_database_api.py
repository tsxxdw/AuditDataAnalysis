"""
向量数据库设置API

提供向量数据库设置相关的API接口
"""

from flask import Blueprint, jsonify, request
from service.settings.vector_database.settings_vector_database_service import vector_db_service
from service.exception import AppException
from service.log.logger import app_logger
from service.log.tools import log_with_context, handle_exceptions
import importlib
import os
import time
import socket

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

def test_socket_connection(host, port, timeout=3):
    """测试TCP连接是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        app_logger.warning(f"测试TCP连接失败: {str(e)}")
        return False

def test_chroma_connection(config):
    """测试Chroma数据库连接"""
    try:
        # 检查chromadb模块是否已安装
        chromadb_spec = importlib.util.find_spec("chromadb")
        if chromadb_spec is None:
            return False, "未安装chromadb模块，请先安装: pip install chromadb"
        
        # 导入chromadb
        import chromadb
        from chromadb.config import Settings
        
        # 先测试TCP连接
        host = config.get('host', 'localhost')
        port = int(config.get('port', 8000))
        
        if not test_socket_connection(host, port):
            return False, f"无法连接到Chroma服务器 {host}:{port}，请确认服务是否启动"
        
        # 尝试创建客户端并连接
        client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 测试连接
        heartbeat = client.heartbeat()
        if heartbeat:
            return True, f"成功连接到Chroma服务器，心跳值: {heartbeat}"
        else:
            return False, "连接到Chroma服务器，但未收到有效心跳响应"
            
    except Exception as e:
        app_logger.exception(f"测试Chroma连接时出错: {str(e)}")
        return False, f"连接Chroma数据库失败: {str(e)}"

def test_milvus_connection(config):
    """测试Milvus数据库连接"""
    try:
        # 检查pymilvus模块是否已安装
        milvus_spec = importlib.util.find_spec("pymilvus")
        if milvus_spec is None:
            return False, "未安装pymilvus模块，请先安装: pip install pymilvus"
        
        # 导入pymilvus
        from pymilvus import connections
        
        # 获取配置参数
        host = config.get('host', 'localhost')
        # 处理可能包含端口号的主机地址
        if ':' in host:
            host_parts = host.split(':')
            host = host_parts[0]
            port = host_parts[1]
        else:
            port = config.get('port', '19530')
        
        # 先测试TCP连接
        if not test_socket_connection(host, int(port)):
            return False, f"无法连接到Milvus服务器 {host}:{port}，请确认服务是否启动"
        
        # 尝试连接
        connections.connect(
            alias="default", 
            host=host, 
            port=port
        )
        
        # 检查连接状态
        if connections.has_connection("default"):
            connections.disconnect("default")
            return True, f"成功连接到Milvus服务器 {host}:{port}"
        else:
            return False, "无法建立与Milvus的连接"
            
    except Exception as e:
        app_logger.exception(f"测试Milvus连接时出错: {str(e)}")
        return False, f"连接Milvus数据库失败: {str(e)}"

def test_faiss_connection(config):
    """测试FAISS索引文件是否可访问"""
    try:
        # 检查faiss模块是否已安装
        faiss_spec = importlib.util.find_spec("faiss")
        if faiss_spec is None:
            return False, "未安装faiss-cpu模块，请先安装: pip install faiss-cpu 或 pip install faiss-gpu"
        
        # 导入faiss
        import faiss
        
        # 获取索引文件路径
        index_path = config.get('index_path')
        if not index_path:
            return False, "未提供FAISS索引文件路径"
        
        # 检查索引文件是否存在
        if not os.path.exists(index_path):
            # 如果索引文件不存在，我们可以认为这是一个新配置
            return True, f"索引文件路径 {index_path} 不存在，但可以用于创建新索引"
        
        # 尝试加载索引文件
        try:
            index = faiss.read_index(index_path)
            return True, f"成功加载FAISS索引文件，维度: {index.d}, 索引大小: {index.ntotal}"
        except Exception as e:
            return False, f"索引文件存在但无法加载: {str(e)}"
            
    except Exception as e:
        app_logger.exception(f"测试FAISS连接时出错: {str(e)}")
        return False, f"测试FAISS索引访问失败: {str(e)}"

def test_elasticsearch_connection(config):
    """测试Elasticsearch连接"""
    try:
        # 检查elasticsearch模块是否已安装
        es_spec = importlib.util.find_spec("elasticsearch")
        if es_spec is None:
            return False, "未安装elasticsearch模块，请先安装: pip install elasticsearch"
        
        # 导入elasticsearch
        from elasticsearch import Elasticsearch
        
        # 获取配置参数
        host = config.get('host', 'localhost')
        port = config.get('port', '9200')
        username = config.get('username', '')
        password = config.get('password', '')
        
        # 先测试TCP连接
        if not test_socket_connection(host, int(port)):
            return False, f"无法连接到Elasticsearch服务器 {host}:{port}，请确认服务是否启动"
        
        # 构建连接URL
        url = f"http://{host}:{port}"
        
        # 创建客户端
        if username and password:
            es = Elasticsearch(url, basic_auth=(username, password))
        else:
            es = Elasticsearch(url)
        
        # 测试连接
        if es.ping():
            info = es.info()
            version = info.get('version', {}).get('number', 'unknown')
            return True, f"成功连接到Elasticsearch服务器，版本: {version}"
        else:
            return False, "无法连接到Elasticsearch服务器"
            
    except Exception as e:
        app_logger.exception(f"测试Elasticsearch连接时出错: {str(e)}")
        return False, f"连接Elasticsearch失败: {str(e)}"

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
            # 如果主机地址不包含端口号，检查是否提供了端口参数
            if ':' not in db_config['host'] and 'port' not in db_config:
                db_config['port'] = '19530'  # 使用默认端口
        elif db_type == 'elasticsearch':
            if not all(key in db_config for key in ['host', 'port']):
                return jsonify({"success": False, "message": "Elasticsearch连接缺少必要参数"})
        elif db_type == 'faiss':
            if 'index_path' not in db_config:
                return jsonify({"success": False, "message": "FAISS连接缺少必要参数"})
        else:
            return jsonify({"success": False, "message": f"不支持的向量数据库类型: {db_type}"})
        
        # 执行实际的连接测试
        success, message = False, "未知错误"
        
        if db_type == 'chroma':
            success, message = test_chroma_connection(db_config)
        elif db_type == 'milvus':
            success, message = test_milvus_connection(db_config)
        elif db_type == 'faiss':
            success, message = test_faiss_connection(db_config)
        elif db_type == 'elasticsearch':
            success, message = test_elasticsearch_connection(db_config)
        
        return jsonify({
            "success": success, 
            "message": message
        })
        
    except AppException as e:
        # 处理应用异常
        app_logger.warning(f"向量数据库连接测试失败: {e.message}")
        return jsonify({"success": False, "message": e.message})
    except Exception as e:
        # 处理其他异常
        app_logger.exception("测试向量数据库连接时发生错误")
        return jsonify({"success": False, "message": f"系统错误: {str(e)}"}) 