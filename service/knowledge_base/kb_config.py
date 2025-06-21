"""
知识库配置

包含知识库相关的配置参数和设置
"""

# Ollama 配置
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_EMBED_MODEL = "nomic-embed-text:latest"

# Milvus 配置
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "knowledge_base"

# 向量维度 (nomic-embed-text 模型的输出维度)
VECTOR_DIMENSION = 768

# 知识库文件目录
KB_DOCUMENTS_DIR = "file/knowledge_base/documents"
KB_METADATA_PATH = "file/knowledge_base/kb_metadata.json"

# 分块设置
DEFAULT_CHUNK_SIZE = 1000  # 默认分块大小（字符数）
MAX_CHUNK_SIZE = 3000      # 最大分块大小
MIN_CHUNK_SIZE = 200       # 最小分块大小

# 搜索设置
DEFAULT_SEARCH_LIMIT = 10  # 默认搜索结果数量限制 