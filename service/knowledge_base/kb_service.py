"""
知识库服务核心功能

处理文档处理、文本添加、向量存储和检索等功能
"""

import os
import uuid
import json
import glob
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Union
import re

import numpy as np
from pymilvus import connections, Collection, utility
from service.log.logger import app_logger
from service.knowledge_base.kb_config import *

# Ollama 嵌入模型
OLLAMA_EMBED_MODEL = "nomic-embed-text:latest"

# 向量维度 (nomic-embed-text 模型的输出维度)
VECTOR_DIMENSION = 768

# 知识库元数据文件路径
KB_METADATA_PATH = "file/knowledge_base/kb_metadata.json"

# 默认分块大小
DEFAULT_CHUNK_SIZE = 1000

# 确保Milvus集合存在
def ensure_milvus_collection():
    """确保Milvus集合存在"""
    try:
        # 连接到Milvus
        connections.connect(
            alias="default", 
            host=MILVUS_HOST, 
            port=MILVUS_PORT
        )
        
        # 检查集合是否存在
        if not utility.has_collection(MILVUS_COLLECTION):
            app_logger.info(f"创建Milvus集合: {MILVUS_COLLECTION}")
            
            # 定义集合结构
            from pymilvus import CollectionSchema, FieldSchema, DataType
            
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="item_id", dtype=DataType.VARCHAR, max_length=36),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=20),
                FieldSchema(name="chunk_index", dtype=DataType.INT64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
            ]
            
            schema = CollectionSchema(fields=fields)
            collection = Collection(name=MILVUS_COLLECTION, schema=schema)
            
            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64}
            }
            
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            
            app_logger.info(f"成功创建并索引Milvus集合: {MILVUS_COLLECTION}")
        else:
            app_logger.info(f"Milvus集合已存在: {MILVUS_COLLECTION}")
            
            # 加载集合
            collection = Collection(name=MILVUS_COLLECTION)
            collection.load()
        
        return True
    
    except Exception as e:
        app_logger.error(f"确保Milvus集合存在时发生错误: {str(e)}")
        return False

# 初始化知识库元数据
def init_kb_metadata():
    """初始化知识库元数据"""
    if not os.path.exists(KB_METADATA_PATH):
        metadata = {
            "items": [],
            "total_chunks": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(KB_METADATA_PATH), exist_ok=True)
        
        with open(KB_METADATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        app_logger.info(f"初始化知识库元数据文件: {KB_METADATA_PATH}")
    
    else:
        app_logger.info(f"知识库元数据文件已存在: {KB_METADATA_PATH}")

# 获取知识库元数据
def get_kb_metadata():
    """获取知识库元数据"""
    if not os.path.exists(KB_METADATA_PATH):
        init_kb_metadata()
    
    with open(KB_METADATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存知识库元数据
def save_kb_metadata(metadata):
    """保存知识库元数据"""
    metadata["last_updated"] = datetime.now().isoformat()
    
    with open(KB_METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

# 检测文档类型
def detect_document_type(file_path: str) -> str:
    """检测文档类型"""
    extension = os.path.splitext(file_path)[1].lower()
    print(f"[DEBUG] 检测文档类型，文件路径: {file_path}, 扩展名: {extension}")
    
    # 如果有明确的扩展名，使用扩展名判断
    if extension in ['.docx', '.doc']:
        print(f"[DEBUG] 检测到Word文档类型: {extension}")
        return 'doc'
    elif extension == '.txt':
        # 对于TXT文件，通过内容进一步判断可能的文档类型
        print("[DEBUG] 检测到TXT文件，进一步分析内容")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)  # 读取前2000个字符进行分析
        
        # 检查是否可能是法律文档
        if re.search(r'第[一二三四五六七八九十百千]+条|法律|条例|规定|违反|处罚', content):
            print("[DEBUG] 检测到法律文档")
            return 'legal'
        
        # 检查是否可能是审计报告
        if re.search(r'审计报告|审计发现|审计结果|财务|会计|报表|资产|负债|利润', content):
            print("[DEBUG] 检测到审计报告")
            return 'audit'
        
        print("[DEBUG] 检测到普通文本文件")
        return 'txt'
    elif not extension:
        # 如果没有扩展名，尝试通过文件内容判断
        print("[DEBUG] 文件没有扩展名，尝试通过内容判断类型")
        
        # 尝试以二进制方式打开前几个字节判断文件类型
        with open(file_path, 'rb') as f:
            header = f.read(8)
        
        # 检查是否为DOCX文件 (ZIP格式，PK头)
        if header.startswith(b'PK\x03\x04'):
            print("[DEBUG] 通过文件头识别为DOCX文件")
            return 'doc'
        
        # 尝试作为文本文件打开，看是否能成功读取
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)
                
            # 如果能成功读取，检查内容特征
            if re.search(r'第[一二三四五六七八九十百千]+条|法律|条例|规定|违反|处罚', content):
                print("[DEBUG] 通过内容识别为法律文档")
                return 'legal'
            elif re.search(r'审计报告|审计发现|审计结果|财务|会计|报表|资产|负债|利润', content):
                print("[DEBUG] 通过内容识别为审计报告")
                return 'audit'
            else:
                print("[DEBUG] 无法确定类型，默认为文本文件")
                return 'txt'
        except:
            # 如果无法作为文本文件读取，假设为doc文件
            print("[DEBUG] 无法作为文本文件读取，推测为Word文档")
            return 'doc'
    else:
        print(f"[DEBUG] 检测到不支持的文件类型: {extension}")
        
        # 尝试查看文件的MIME类型
        try:
            import magic
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            print(f"[DEBUG] 文件MIME类型: {file_type}")
            
            if 'msword' in file_type or 'officedocument' in file_type:
                print("[DEBUG] 通过MIME类型识别为Word文档")
                return 'doc'
            elif 'text/plain' in file_type:
                print("[DEBUG] 通过MIME类型识别为文本文件")
                return 'txt'
        except ImportError:
            print("[DEBUG] python-magic库未安装，无法进行MIME类型检测")
        except Exception as e:
            print(f"[DEBUG] MIME类型检测失败: {str(e)}")
        
        # 如果还是无法确定，检查文件是否可以作为文本文件打开
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(100)  # 尝试读取前100个字符
            print("[DEBUG] 文件可以作为文本打开，假设为文本文件")
            return 'txt'
        except:
            pass
        
        return 'unknown'

# 根据文档类型和策略分块
def chunk_document(content: str, doc_type: str, chunking_strategy: str = 'auto', custom_chunk_size: Optional[int] = None) -> List[str]:
    """根据文档类型和策略分块"""
    chunks = []
    
    # 自定义分块大小
    if chunking_strategy == 'custom' and custom_chunk_size and custom_chunk_size > 0:
        # 简单按字符数分块
        for i in range(0, len(content), custom_chunk_size):
            chunk = content[i:i + custom_chunk_size]
            if chunk.strip():  # 确保不添加空块
                chunks.append(chunk)
        return chunks
    
    # 根据文档类型自动选择分块策略
    if doc_type == 'legal':
        # 法律文档按条款分块
        legal_pattern = r'第[一二三四五六七八九十百千]+条([\s\S]*?)(?=第[一二三四五六七八九十百千]+条|$)'
        matches = re.finditer(legal_pattern, content)
        
        # 提取匹配的条款
        for match in matches:
            article = match.group(0).strip()
            if article:
                chunks.append(article)
        
        # 处理前导内容（第一条之前的内容）
        first_article_pos = content.find('第')
        if first_article_pos > 0:
            intro = content[:first_article_pos].strip()
            if intro:
                chunks.insert(0, intro)
    
    elif doc_type == 'audit':
        # 审计报告使用三层分级切割
        
        # 1. 提取全文摘要（通常在报告开头）
        summary_match = re.search(r'摘要|概述|总结|Executive Summary', content)
        if summary_match:
            summary_start = summary_match.start()
            summary_end = content.find('\n\n', summary_start)
            if summary_end == -1:
                summary_end = min(summary_start + 2000, len(content))
            
            summary = content[summary_start:summary_end].strip()
            if summary:
                chunks.append(summary)
        
        # 2. 按章节切割
        chapter_pattern = r'([一二三四五六七八九十]、[\s\S]*?)(?=[一二三四五六七八九十]、|$)'
        chapters = re.finditer(chapter_pattern, content)
        
        for chapter in chapters:
            chapter_text = chapter.group(0).strip()
            if chapter_text:
                chunks.append(chapter_text)
        
        # 3. 提取表格和关键段落（简化模拟）
        # 在实际应用中，这需要更复杂的表格提取逻辑
        table_pattern = r'表\d+[：:]([\s\S]*?)(?=\n\n)'
        tables = re.finditer(table_pattern, content)
        
        for table in tables:
            table_text = table.group(0).strip()
            if table_text and len(table_text) > 50:  # 排除过短的匹配
                chunks.append(table_text)
    
    else:  # doc, txt 或其他类型
        # 默认按段落分块，合并短段落
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # 如果当前段落加上新段落不超过最大块大小，则合并
            if len(current_chunk) + len(para) < DEFAULT_CHUNK_SIZE:
                current_chunk += ("\n" if current_chunk else "") + para
            else:
                # 当前块已足够大，保存并开始新块
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
    
    # 如果没有成功分块，退回到简单分块
    if not chunks:
        app_logger.warning(f"未能按{doc_type}文档类型成功分块，使用默认分块方法")
        
        # 默认分块方法
        chunk_size = custom_chunk_size or DEFAULT_CHUNK_SIZE
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
    
    return chunks

# 从文档中提取文本内容
def extract_text_from_document(file_path: str) -> Tuple[bool, str, str]:
    """从文档中提取文本内容"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        print(f"[DEBUG] 开始处理文件: {file_path}, 扩展名: {file_extension}")
        
        # 对于没有扩展名的文件，尝试猜测文件类型
        if not file_extension:
            print("[DEBUG] 文件没有扩展名，尝试根据内容判断文件类型")
            
            # 先尝试通过文件头部判断
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            # 检查是否为DOCX文件 (ZIP格式，PK头)
            if header.startswith(b'PK\x03\x04'):
                print("[DEBUG] 通过文件头识别为DOCX文件，将作为docx处理")
                file_extension = '.docx'  # 假定为docx
            else:
                # 尝试作为文本文件打开
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        sample = f.read(100)
                    print("[DEBUG] 文件可以作为文本打开，将作为txt处理")
                    file_extension = '.txt'  # 假定为txt
                except:
                    print("[DEBUG] 无法作为文本打开，默认作为docx处理")
                    file_extension = '.docx'  # 默认尝试作为docx
        
        if file_extension == '.txt':
            # 处理TXT文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print(f"[DEBUG] 成功读取TXT文件，内容长度: {len(content)}")
            return True, content, "提取TXT文件内容成功"
        
        elif file_extension in ['.docx', '.doc'] or not file_extension:
            # 处理Word文档
            print(f"[DEBUG] 处理Word文档: {file_path}")
            success = False
            error_messages = []
            
            # 多种方法尝试提取
            # 1. 尝试使用python-docx库（处理.docx）
            if file_extension == '.docx' or not file_extension:
                try:
                    print("[DEBUG] 尝试使用python-docx库")
                    import docx
                    print("[DEBUG] 成功导入docx库")
                    doc = docx.Document(file_path)
                    print("[DEBUG] 成功打开docx文档")
                    content = '\n\n'.join([para.text for para in doc.paragraphs])
                    print(f"[DEBUG] 使用python-docx成功提取内容，内容长度: {len(content)}")
                    return True, content, "使用python-docx提取Word文档内容成功"
                except ImportError as e:
                    print(f"[DEBUG] 导入python-docx失败: {str(e)}")
                    error_messages.append(f"导入python-docx失败: {str(e)}")
                except Exception as e:
                    print(f"[DEBUG] 使用python-docx处理文档失败: {str(e)}")
                    error_messages.append(f"使用python-docx处理文档失败: {str(e)}")
            
            # 2. 尝试使用docx2txt库（处理.docx）
            try:
                print("[DEBUG] 尝试使用docx2txt库")
                import docx2txt
                print("[DEBUG] 成功导入docx2txt库")
                content = docx2txt.process(file_path)
                print(f"[DEBUG] 使用docx2txt成功提取内容，内容长度: {len(content)}")
                return True, content, "使用docx2txt提取Word文档内容成功"
            except ImportError as e:
                print(f"[DEBUG] 导入docx2txt失败: {str(e)}")
                error_messages.append(f"导入docx2txt失败: {str(e)}")
            except Exception as e:
                print(f"[DEBUG] 使用docx2txt处理文档失败: {str(e)}")
                error_messages.append(f"使用docx2txt处理文档失败: {str(e)}")
            
            # 3. 尝试读取为普通文本（不推荐，但作为备选）
            try:
                print("[DEBUG] 尝试以普通文本方式读取")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 检查内容是否包含大量非ASCII字符（可能是二进制格式）
                non_ascii_ratio = sum(1 for c in content if ord(c) > 127) / max(len(content), 1)
                print(f"[DEBUG] 非ASCII字符比例: {non_ascii_ratio}")
                if non_ascii_ratio > 0.3:
                    print("[DEBUG] 非ASCII字符比例过高，无法以文本方式读取")
                    error_messages.append("非ASCII字符比例过高，无法以文本方式读取")
                else:
                    print(f"[DEBUG] 以文本方式成功读取，内容长度: {len(content)}")
                    return True, content, "以文本方式提取Word文档内容成功"
            except Exception as e:
                print(f"[DEBUG] 以普通文本方式读取失败: {str(e)}")
                error_messages.append(f"以普通文本方式读取失败: {str(e)}")
            
            # 如果所有方法都失败
            error_msg = "\n".join(error_messages)
            print(f"[DEBUG] 所有提取方法都失败: {error_msg}")
            return False, "", f"无法读取文档内容: {error_msg}"
        
        else:
            print(f"[DEBUG] 不支持的文件类型: {file_extension}")
            return False, "", f"不支持的文件类型: {file_extension}"
    
    except Exception as e:
        print(f"[DEBUG] 提取文档内容时发生错误: {str(e)}")
        app_logger.error(f"提取文档内容时发生错误: {str(e)}")
        return False, "", f"提取文档内容失败: {str(e)}"

# 处理文档并添加到知识库
def process_document(file_path: str, chunking_strategy: str = 'auto', custom_chunk_size: Optional[int] = None) -> Dict[str, Any]:
    """处理文档并添加到知识库"""
    try:
        print(f"[DEBUG] 开始处理文档: {file_path}, 分块策略: {chunking_strategy}")
        
        # 确保文件存在
        if not os.path.exists(file_path):
            print(f"[DEBUG] 文件不存在: {file_path}")
            return {
                'success': False,
                'message': f"文件不存在: {file_path}"
            }
        
        # 确保Milvus集合存在
        if not ensure_milvus_collection():
            print("[DEBUG] 连接到Milvus失败")
            return {
                'success': False,
                'message': "连接到Milvus失败，请检查Milvus服务是否运行"
            }
        
        # 获取文件名
        filename = os.path.basename(file_path)
        print(f"[DEBUG] 处理文件名: {filename}")
        
        # 检测文档类型
        doc_type = detect_document_type(file_path)
        print(f"[DEBUG] 检测到文档类型: {doc_type}")
        
        # 提取文本内容
        print("[DEBUG] 开始提取文本内容")
        success, content, message = extract_text_from_document(file_path)
        print(f"[DEBUG] 提取文本结果: 成功={success}, 消息={message}")
        
        if not success:
            return {
                'success': False,
                'message': message
            }
        
        # 根据文档类型和策略分块
        print(f"[DEBUG] 开始分块处理，文本长度: {len(content)}")
        chunks = chunk_document(content, doc_type, chunking_strategy, custom_chunk_size)
        print(f"[DEBUG] 分块结果: 生成了 {len(chunks)} 个文本块")
        
        if not chunks:
            print("[DEBUG] 文档分块失败，无有效内容")
            return {
                'success': False,
                'message': "文档分块失败，无法提取有效内容"
            }
        
        # 生成唯一ID作为知识项目ID
        item_id = str(uuid.uuid4())
        print(f"[DEBUG] 生成知识项目ID: {item_id}")
        
        # 连接到Milvus集合
        print("[DEBUG] 连接到Milvus集合")
        collection = Collection(MILVUS_COLLECTION)
        
        # 准备插入数据
        insert_data = []
        
        for i, chunk in enumerate(chunks):
            # 生成嵌入向量
            print(f"[DEBUG] 为文档块 {i+1}/{len(chunks)} 生成嵌入向量")
            embedding = generate_embedding(chunk)
            
            if embedding is None:
                print(f"[DEBUG] 为文档块 {i+1}/{len(chunks)} 生成嵌入向量失败")
                app_logger.error(f"为文档块 {i+1}/{len(chunks)} 生成嵌入向量失败")
                continue
            
            # 准备数据记录
            record = {
                "id": str(uuid.uuid4()),
                "content": chunk,
                "item_id": item_id,
                "title": filename,
                "source_type": doc_type,
                "chunk_index": i,
                "embedding": embedding
            }
            
            insert_data.append(record)
        
        # 批量插入数据
        if insert_data:
            print(f"[DEBUG] 准备将 {len(insert_data)} 个文档块添加到Milvus集合")
            collection.insert(insert_data)
            print(f"[DEBUG] 成功将 {len(insert_data)} 个文档块添加到Milvus集合")
            app_logger.info(f"成功将 {len(insert_data)} 个文档块添加到Milvus集合")
        else:
            print("[DEBUG] 没有生成任何有效的嵌入向量")
            return {
                'success': False,
                'message': "所有文档块生成嵌入向量失败"
            }
        
        # 更新元数据
        print("[DEBUG] 更新知识库元数据")
        metadata = get_kb_metadata()
        
        # 添加知识项目信息
        metadata["items"].append({
            "id": item_id,
            "title": filename,
            "source_type": doc_type,
            "file_path": file_path,
            "chunks_count": len(insert_data),
            "created_at": datetime.now().isoformat(),
            "type": "file"
        })
        
        # 更新总块数
        metadata["total_chunks"] += len(insert_data)
        
        # 保存元数据
        save_kb_metadata(metadata)
        print("[DEBUG] 元数据更新完成")
        
        print(f"[DEBUG] 文档处理完成: {filename}")
        return {
            'success': True,
            'message': f"成功处理文档 {filename}",
            'id': item_id,
            'document_type': doc_type,
            'chunks_count': len(insert_data)
        }
    
    except Exception as e:
        print(f"[DEBUG] 处理文档时发生错误: {str(e)}")
        app_logger.error(f"处理文档时发生错误: {str(e)}")
        return {
            'success': False,
            'message': f"处理文档失败: {str(e)}"
        }

# 添加文本到知识库
def add_text_to_knowledge_base(title: str, content: str, tags: List[str] = []) -> Dict[str, Any]:
    """添加文本到知识库"""
    try:
        # 确保Milvus集合存在
        if not ensure_milvus_collection():
            return {
                'success': False,
                'message': "连接到Milvus失败，请检查Milvus服务是否运行"
            }
        
        # 生成唯一ID作为知识项目ID
        item_id = str(uuid.uuid4())
        
        # 连接到Milvus集合
        collection = Collection(MILVUS_COLLECTION)
        
        # 生成嵌入向量
        embedding = generate_embedding(content)
        
        if embedding is None:
            return {
                'success': False,
                'message': "生成嵌入向量失败"
            }
        
        # 准备数据记录
        record = {
            "id": str(uuid.uuid4()),
            "content": content,
            "item_id": item_id,
            "title": title,
            "source_type": "manual",
            "chunk_index": 0,
            "embedding": embedding
        }
        
        # 插入数据
        collection.insert([record])
        app_logger.info(f"成功将文本添加到Milvus集合")
        
        # 更新元数据
        metadata = get_kb_metadata()
        
        # 添加知识项目信息
        metadata["items"].append({
            "id": item_id,
            "title": title,
            "source_type": "manual",
            "tags": tags,
            "chunks_count": 1,
            "created_at": datetime.now().isoformat(),
            "type": "text"
        })
        
        # 更新总块数
        metadata["total_chunks"] += 1
        
        # 保存元数据
        save_kb_metadata(metadata)
        
        return {
            'success': True,
            'message': f"成功添加文本到知识库",
            'id': item_id
        }
    
    except Exception as e:
        app_logger.error(f"添加文本到知识库时发生错误: {str(e)}")
        return {
            'success': False,
            'message': f"添加文本到知识库失败: {str(e)}"
        }

# 搜索知识库
def search_knowledge_base(query: str, filter_type: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
    """搜索知识库"""
    try:
        # 确保Milvus集合存在
        if not ensure_milvus_collection():
            app_logger.error("连接到Milvus失败，请检查Milvus服务是否运行")
            return []
        
        # 生成查询嵌入向量
        query_embedding = generate_embedding(query)
        
        if query_embedding is None:
            app_logger.error("为查询生成嵌入向量失败")
            return []
        
        # 连接到Milvus集合
        collection = Collection(MILVUS_COLLECTION)
        
        # 准备搜索参数
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        
        # 构建查询条件
        expr = None
        if filter_type != 'all':
            expr = f'source_type == "{filter_type}"'
        
        # 执行向量搜索
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["id", "content", "item_id", "title", "source_type", "chunk_index"]
        )
        
        # 处理搜索结果
        search_results = []
        
        for hits in results:
            for hit in hits:
                result = {
                    "id": hit.id,
                    "item_id": hit.entity.get("item_id"),
                    "title": hit.entity.get("title"),
                    "source_type": hit.entity.get("source_type"),
                    "chunk_index": hit.entity.get("chunk_index"),
                    "content": hit.entity.get("content"),
                    "score": hit.score
                }
                search_results.append(result)
        
        app_logger.info(f"知识库搜索完成，找到 {len(search_results)} 个结果")
        return search_results
    
    except Exception as e:
        app_logger.error(f"搜索知识库时发生错误: {str(e)}")
        return []

# 获取知识库项目列表
def get_knowledge_items(filter_type: str = 'all', page: int = 1, per_page: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    """获取知识库项目列表"""
    try:
        # 获取元数据
        metadata = get_kb_metadata()
        items = metadata.get("items", [])
        
        # 应用过滤
        if filter_type != 'all':
            items = [item for item in items if item.get("source_type") == filter_type]
        
        # 计算总数
        total = len(items)
        
        # 应用分页
        start = (page - 1) * per_page
        end = start + per_page
        
        # 排序（按创建时间倒序）
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # 返回当前页的项目
        return items[start:end], total
    
    except Exception as e:
        app_logger.error(f"获取知识库项目列表时发生错误: {str(e)}")
        return [], 0

# 获取单个知识库项目详情
def get_knowledge_item_by_id(item_id: str) -> Optional[Dict[str, Any]]:
    """获取单个知识库项目详情"""
    try:
        # 获取元数据
        metadata = get_kb_metadata()
        items = metadata.get("items", [])
        
        # 查找指定ID的项目
        for item in items:
            if item.get("id") == item_id:
                return item
        
        app_logger.warning(f"未找到ID为{item_id}的知识库项目")
        return None
    
    except Exception as e:
        app_logger.error(f"获取知识库项目详情时发生错误: {str(e)}")
        return None

# 删除知识库项目
def delete_knowledge_item(item_id: str) -> Dict[str, Any]:
    """删除知识库项目"""
    try:
        # 确保Milvus集合存在
        if not ensure_milvus_collection():
            return {
                'success': False,
                'message': "连接到Milvus失败，请检查Milvus服务是否运行"
            }
        
        # 获取元数据
        metadata = get_kb_metadata()
        items = metadata.get("items", [])
        
        # 查找并删除指定ID的项目
        item_found = False
        chunks_count = 0
        file_path = None
        
        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item_found = True
                chunks_count = item.get("chunks_count", 0)
                file_path = item.get("file_path")
                del items[i]
                break
        
        if not item_found:
            return {
                'success': False,
                'message': f"未找到ID为{item_id}的知识库项目"
            }
        
        # 从Milvus中删除相关记录
        collection = Collection(MILVUS_COLLECTION)
        expr = f'item_id == "{item_id}"'
        collection.delete(expr)
        
        # 如果是文件类型，尝试删除文件
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                app_logger.info(f"已删除文件: {file_path}")
            except Exception as e:
                app_logger.warning(f"删除文件失败: {file_path}, 错误: {str(e)}")
        
        # 更新元数据
        metadata["items"] = items
        metadata["total_chunks"] -= chunks_count
        
        # 保存元数据
        save_kb_metadata(metadata)
        
        return {
            'success': True,
            'message': f"成功删除知识库项目"
        }
    
    except Exception as e:
        app_logger.error(f"删除知识库项目时发生错误: {str(e)}")
        return {
            'success': False,
            'message': f"删除知识库项目失败: {str(e)}"
        }

# 使用Ollama生成嵌入向量
def generate_embedding(text: str) -> Optional[List[float]]:
    """使用Ollama生成嵌入向量"""
    try:
        # 使用subprocess调用Ollama API
        print(f"[DEBUG] 开始生成嵌入向量，文本长度: {len(text)}")
        command = [
            "curl", "-s", f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings",
            "-d", json.dumps({"model": OLLAMA_EMBED_MODEL, "prompt": text})
        ]
        
        print(f"[DEBUG] 调用Ollama API: {OLLAMA_HOST}:{OLLAMA_PORT}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[DEBUG] Ollama API调用失败，返回码: {result.returncode}, 错误: {result.stderr}")
            app_logger.error(f"Ollama API调用失败: {result.stderr}")
            return None
        
        print("[DEBUG] Ollama API调用成功，解析响应")
        response = json.loads(result.stdout)
        
        if "embedding" not in response:
            print(f"[DEBUG] Ollama API返回异常，未包含embedding字段: {response}")
            app_logger.error(f"Ollama API返回异常: {response}")
            return None
        
        embedding_length = len(response["embedding"])
        print(f"[DEBUG] 成功生成嵌入向量，维度: {embedding_length}")
        return response["embedding"]
    
    except Exception as e:
        print(f"[DEBUG] 生成嵌入向量时发生错误: {str(e)}")
        app_logger.error(f"生成嵌入向量时发生错误: {str(e)}")
        return None 