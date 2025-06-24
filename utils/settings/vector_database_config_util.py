"""
向量数据库配置工具类

提供向量数据库配置的读取和管理功能
"""

import os
import json
from typing import Dict, Any, List, Optional

class VectorDatabaseConfigUtil:
    """向量数据库配置工具类，管理向量数据库的配置信息"""
    
    CONFIG_FILE_PATH = 'config/settings/vector_database_config.json'
    
    @staticmethod
    def load_vector_database_config() -> Dict[str, Any]:
        """
        加载向量数据库配置文件
        
        Returns:
            Dict[str, Any]: 向量数据库配置数据
        """
        config_data = {
            "defaultVectorDbType": "chroma",
            "vectorDatabases": {}
        }
        
        try:
            if os.path.exists(VectorDatabaseConfigUtil.CONFIG_FILE_PATH):
                with open(VectorDatabaseConfigUtil.CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
                    file_data = json.load(file)
                    config_data.update(file_data)
        except Exception as e:
            print(f"加载向量数据库配置文件失败: {str(e)}")
        
        return config_data
    
    @staticmethod
    def save_vector_database_config(config_data: Dict[str, Any]) -> bool:
        """
        保存向量数据库配置到文件
        
        Args:
            config_data: 要保存的配置数据
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(VectorDatabaseConfigUtil.CONFIG_FILE_PATH), exist_ok=True)
            
            with open(VectorDatabaseConfigUtil.CONFIG_FILE_PATH, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存向量数据库配置失败: {str(e)}")
            return False
    
    @staticmethod
    def get_default_vector_db_type() -> str:
        """
        获取默认的向量数据库类型
        
        Returns:
            str: 默认向量数据库类型
        """
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config()
            return config_data.get("defaultVectorDbType", "chroma")
        except Exception as e:
            print(f"获取默认向量数据库类型失败: {str(e)}")
            return "chroma"
    
    @staticmethod
    def get_all_vector_database_types() -> List[str]:
        """
        获取所有可用的向量数据库类型
        
        Returns:
            List[str]: 向量数据库类型列表
        """
        # 支持的向量数据库类型列表
        return ["chroma", "milvus", "faiss", "elasticsearch"]
    
    @staticmethod
    def get_vector_database_config(db_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取指定类型的向量数据库配置，如果不指定类型则返回默认类型的配置
        
        Args:
            db_type (Optional[str]): 向量数据库类型，如chroma, milvus等。如果为None，则使用默认类型
            
        Returns:
            Optional[Dict[str, Any]]: 向量数据库配置信息，如果未找到则返回None
        """
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config()
            
            # 如果未指定数据库类型，使用默认类型
            if db_type is None:
                db_type = VectorDatabaseConfigUtil.get_default_vector_db_type()
            
            # 如果配置中存在该类型的数据库配置，则返回它
            if "vectorDatabases" in config_data and isinstance(config_data["vectorDatabases"], dict):
                databases = config_data["vectorDatabases"]
                if db_type in databases:
                    # 将数据库类型也添加到配置中，方便后续使用
                    db_config = databases[db_type].copy()
                    db_config["type"] = db_type
                    return db_config
            
            return None
        except Exception as e:
            print(f"获取向量数据库配置失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all_vector_database_configs() -> Dict[str, Dict[str, Any]]:
        """
        获取所有向量数据库的配置信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 所有向量数据库配置的字典，键为数据库类型
        """
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config()
            
            result = {}
            
            if "vectorDatabases" in config_data and isinstance(config_data["vectorDatabases"], dict):
                databases = config_data["vectorDatabases"]
                
                # 为每个配置添加type字段
                for db_type, db_config in databases.items():
                    config_with_type = db_config.copy()
                    config_with_type["type"] = db_type
                    result[db_type] = config_with_type
            
            return result
        except Exception as e:
            print(f"获取所有向量数据库配置失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_vector_db_display_name(db_type: str) -> str:
        """获取向量数据库类型的显示名称
        
        Args:
            db_type: 向量数据库类型标识符
            
        Returns:
            str: 向量数据库类型的显示名称
        """
        display_names = {
            'chroma': 'Chroma',
            'milvus': 'Milvus',
            'faiss': 'FAISS',
            'elasticsearch': 'Elasticsearch'
        }
        return display_names.get(db_type, db_type) 