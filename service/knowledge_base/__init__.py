"""
知识库服务模块
"""

import os
from service.log.logger import app_logger
from service.knowledge_base.kb_config import KB_DOCUMENTS_DIR, KB_METADATA_PATH, OLLAMA_HOST, OLLAMA_PORT, MILVUS_HOST, MILVUS_PORT

def init_knowledge_base():
    """初始化知识库服务"""
    app_logger.info("初始化知识库服务")
    print("[DEBUG] 开始初始化知识库服务")
    
    # 确保知识库相关目录存在
    kb_dirs = [
        os.path.dirname(KB_METADATA_PATH),
        KB_DOCUMENTS_DIR
    ]
    
    for directory in kb_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            app_logger.info(f"创建知识库目录: {directory}")
            print(f"[DEBUG] 创建知识库目录: {directory}")
    
    # 初始化元数据文件
    if not os.path.exists(KB_METADATA_PATH):
        from service.knowledge_base.kb_service import init_kb_metadata
        init_kb_metadata()
        print("[DEBUG] 初始化知识库元数据文件")
    
    # 尝试连接到Milvus
    try:
        from service.knowledge_base.kb_service import ensure_milvus_collection
        print(f"[DEBUG] 尝试连接到Milvus服务 {MILVUS_HOST}:{MILVUS_PORT}")
        if ensure_milvus_collection():
            app_logger.info("成功连接到Milvus向量数据库")
            print("[DEBUG] 成功连接到Milvus向量数据库")
        else:
            app_logger.warning("无法连接到Milvus向量数据库，部分知识库功能可能不可用")
            print("[DEBUG] 警告: 无法连接到Milvus向量数据库，部分知识库功能可能不可用")
    except Exception as e:
        app_logger.error(f"初始化Milvus连接时发生错误: {str(e)}")
        print(f"[DEBUG] 错误: 初始化Milvus连接时发生错误: {str(e)}")
        
    # 尝试测试Ollama嵌入模型
    try:
        from service.knowledge_base.kb_service import generate_embedding
        from service.knowledge_base.kb_config import OLLAMA_EMBED_MODEL
        
        print(f"[DEBUG] 尝试测试Ollama嵌入模型: {OLLAMA_HOST}:{OLLAMA_PORT}, 模型: {OLLAMA_EMBED_MODEL}")
        test_embedding = generate_embedding("测试嵌入模型")
        if test_embedding:
            app_logger.info(f"成功测试Ollama嵌入模型: {OLLAMA_EMBED_MODEL}")
            print(f"[DEBUG] 成功测试Ollama嵌入模型: {OLLAMA_EMBED_MODEL}, 向量维度: {len(test_embedding)}")
        else:
            app_logger.warning(f"无法使用Ollama嵌入模型: {OLLAMA_EMBED_MODEL}，部分知识库功能可能不可用")
            print(f"[DEBUG] 警告: 无法使用Ollama嵌入模型: {OLLAMA_EMBED_MODEL}，部分知识库功能可能不可用")
            print("[DEBUG] 请确保Ollama服务已启动并已下载nomic-embed-text模型")
    except Exception as e:
        app_logger.error(f"测试Ollama嵌入模型时发生错误: {str(e)}")
        print(f"[DEBUG] 错误: 测试Ollama嵌入模型时发生错误: {str(e)}")
        print("[DEBUG] 请检查Ollama服务是否已启动，或是否可以通过以下命令下载模型: ollama pull nomic-embed-text:latest") 