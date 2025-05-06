"""
数据库配置工具类

用于读取和解析数据库配置信息，从config/settings/database_config.json文件中获取连接信息
"""

import os
import json
from typing import Dict, List, Optional, Any


class DatabaseConfigUtil:
    """
    数据库配置工具类，提供静态方法获取数据库连接信息
    """
    
    @staticmethod
    def get_config_file_path() -> str:
        """
        获取配置文件路径
        
        Returns:
            str: 配置文件的绝对路径
        """
        # 获取项目根目录路径
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 配置文件路径
        config_path = os.path.join(root_dir, 'config', 'settings', 'database_config.json')
        return config_path
    
    @staticmethod
    def load_database_config() -> Dict[str, Any]:
        """
        加载数据库配置信息
        
        Returns:
            Dict[str, Any]: 包含所有数据库配置的字典
        
        Raises:
            FileNotFoundError: 当配置文件不存在时
            json.JSONDecodeError: 当配置文件格式错误时
        """
        config_path = DatabaseConfigUtil.get_config_file_path()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return config_data
        except FileNotFoundError:
            raise FileNotFoundError(f"数据库配置文件不存在: {config_path}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"数据库配置文件格式错误: {config_path}", "", 0)
    
    @staticmethod
    def get_default_db_type() -> str:
        """
        获取默认数据库类型
        
        Returns:
            str: 默认数据库类型，如mysql, sqlserver等
        """
        try:
            config_data = DatabaseConfigUtil.load_database_config()
            return config_data.get("defaultDbType", "mysql")
        except Exception as e:
            print(f"获取默认数据库类型失败: {str(e)}")
            return "mysql"
    
    @staticmethod
    def get_all_database_types() -> List[str]:
        """
        获取所有支持的数据库类型
        
        Returns:
            List[str]: 所有支持的数据库类型列表
        """
        try:
            config_data = DatabaseConfigUtil.load_database_config()
            if "databases" in config_data and isinstance(config_data["databases"], dict):
                return list(config_data["databases"].keys())
            return []
        except Exception as e:
            print(f"获取数据库类型列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_database_config(db_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取指定类型的数据库配置，如果不指定类型则返回默认类型的配置
        
        Args:
            db_type (Optional[str]): 数据库类型，如mysql, sqlserver, oracle等。如果为None，则使用默认类型
            
        Returns:
            Optional[Dict[str, Any]]: 数据库配置信息，如果未找到则返回None
        """
        try:
            config_data = DatabaseConfigUtil.load_database_config()
            
            # 如果未指定数据库类型，使用默认类型
            if db_type is None:
                db_type = DatabaseConfigUtil.get_default_db_type()
            
            # 如果配置中存在该类型的数据库配置，则返回它
            if "databases" in config_data and isinstance(config_data["databases"], dict):
                databases = config_data["databases"]
                if db_type in databases:
                    # 将数据库类型也添加到配置中，方便后续使用
                    db_config = databases[db_type].copy()
                    db_config["type"] = db_type
                    return db_config
            
            return None
        except Exception as e:
            print(f"获取数据库配置失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all_database_configs() -> Dict[str, Dict[str, Any]]:
        """
        获取所有数据库的配置信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 所有数据库配置的字典，键为数据库类型
        """
        try:
            config_data = DatabaseConfigUtil.load_database_config()
            
            result = {}
            
            if "databases" in config_data and isinstance(config_data["databases"], dict):
                databases = config_data["databases"]
                
                # 为每个配置添加type字段
                for db_type, db_config in databases.items():
                    config_with_type = db_config.copy()
                    config_with_type["type"] = db_type
                    result[db_type] = config_with_type
            
            return result
        except Exception as e:
            print(f"获取所有数据库配置失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_db_display_name(db_type: str) -> str:
        """获取数据库类型的显示名称
        
        Args:
            db_type: 数据库类型标识符
            
        Returns:
            str: 数据库类型的显示名称
        """
        display_names = {
            'mysql': 'MySQL',
            'sqlserver': 'SQL Server',
            'oracle': 'Oracle'
        }
        return display_names.get(db_type, db_type)


if __name__ == "__main__":
    # 测试代码，在直接运行该文件时执行
    try:
        print("默认数据库类型:")
        default_type = DatabaseConfigUtil.get_default_db_type()
        print(f"默认类型: {default_type}")
        
        print("\n支持的数据库类型:")
        db_types = DatabaseConfigUtil.get_all_database_types()
        for db_type in db_types:
            print(f"- {db_type}")
        
        print("\n获取默认数据库配置:")
        default_config = DatabaseConfigUtil.get_database_config()
        if default_config:
            print(f"主机: {default_config.get('host')}")
            print(f"端口: {default_config.get('port', 'N/A')}")
            print(f"数据库: {default_config.get('database', 'N/A')}")
            print(f"用户名: {default_config.get('username')}")
        
        print("\n获取所有数据库配置:")
        all_configs = DatabaseConfigUtil.get_all_database_configs()
        for db_type, config in all_configs.items():
            print(f"\n[{db_type}]")
            for key, value in config.items():
                if key != "password":  # 不显示密码
                    print(f"{key}: {value}")
    except Exception as e:
        print(f"测试过程中出错: {str(e)}") 