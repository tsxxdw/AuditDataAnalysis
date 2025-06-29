"""
向量数据库配置工具类

提供向量数据库配置的读取和管理功能
"""

import os
import json
from typing import Dict, Any, List, Optional

class VectorDatabaseConfigUtil:
    """向量数据库配置工具类，管理向量数据库的配置信息"""
    
    @staticmethod
    def get_config_path(username=None):
        if not username:
            raise ValueError("用户名不能为空")
            
        # 首先检查settings子目录中的文件
        configuration_data_path = os.path.join('configuration_data', username, 'settings','vector_database_config.json')
        # 确保父目录存在
        os.makedirs(os.path.dirname(configuration_data_path), exist_ok=True)
        return configuration_data_path
    
    @staticmethod
    def load_vector_database_config(username=None) -> Dict[str, Any]:
        if not username:
            raise ValueError("用户名不能为空")
        # 默认空配置
        default_config = {
            "defaultVectorDbType": "",
            "vectorDatabases": {}
        }
        try:
            config_path = VectorDatabaseConfigUtil.get_config_path(username)
            # 如果配置文件不存在，直接返回空配置
            if not os.path.exists(config_path):
                return default_config
                
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as file:
                file_data = json.load(file)
                return file_data
        except Exception as e:
            print(f"加载向量数据库配置文件失败: {str(e)}")
            return default_config
    
    @staticmethod
    def save_vector_database_config(config_data: Dict[str, Any], username=None) -> bool:
        if not username:
            raise ValueError("用户名不能为空")
        try:
            config_path = VectorDatabaseConfigUtil.get_config_path(username)
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存向量数据库配置失败: {str(e)}")
            return False
    
    @staticmethod
    def get_default_vector_db_type(username=None) -> str:
        """
        获取默认的向量数据库类型
        
        Args:
            username (str): 用户名，不能为None或空字符串
            
        Returns:
            str: 默认向量数据库类型
            
        Raises:
            ValueError: 当用户名为None或空字符串时
        """
        if not username:
            raise ValueError("用户名不能为空")
            
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config(username)
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
    def get_vector_database_config(username=None, db_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取指定类型的向量数据库配置，如果不指定类型则返回默认类型的配置
        
        Args:
            username (str): 用户名，不能为None或空字符串
            db_type (Optional[str]): 向量数据库类型，如chroma, milvus等。如果为None，则使用默认类型
            
        Returns:
            Optional[Dict[str, Any]]: 向量数据库配置信息，如果未找到则返回None
            
        Raises:
            ValueError: 当用户名为None或空字符串时
        """
        if not username:
            raise ValueError("用户名不能为空")
            
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config(username)
            
            # 如果未指定数据库类型，使用默认类型
            if db_type is None:
                db_type = VectorDatabaseConfigUtil.get_default_vector_db_type(username)
            
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
    def get_all_vector_database_configs(username=None) -> Dict[str, Dict[str, Any]]:
        if not username:
            raise ValueError("用户名不能为空")
            
        try:
            config_data = VectorDatabaseConfigUtil.load_vector_database_config(username)
            
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
        display_names = {
            'chroma': 'Chroma',
            'milvus': 'Milvus',
            'faiss': 'FAISS',
            'elasticsearch': 'Elasticsearch'
        }
        return display_names.get(db_type, db_type) 