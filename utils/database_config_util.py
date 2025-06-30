"""
数据库配置工具类

用于读取和解析数据库配置信息，从configuration_data/{用户名}/database_config.json文件中获取连接信息
"""

import os
import json
from typing import Dict, List, Optional, Any


class DatabaseConfigUtil:
    """
    数据库配置工具类，提供静态方法获取数据库连接信息
    """

    @staticmethod
    def get_config_file_path(username=None) -> str:
        # 首先检查settings子目录中的文件
        configuration_data_path = os.path.join('configuration_data', username, 'settings',
                                               'database_config.json')
        # 确保父目录存在
        os.makedirs(os.path.dirname(configuration_data_path), exist_ok=True)
        return configuration_data_path

    @staticmethod
    def load_database_config(username=None) -> Dict[str, Any]:
        if not username:
            raise ValueError("用户名不能为空")
        config_path = DatabaseConfigUtil.get_config_file_path(username)
        # 默认空配置
        default_config = {"databases": {}, "defaultDbType": ""}
        try:
            # 如果配置文件不存在，直接返回空配置
            if not os.path.exists(config_path):
                return default_config
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return config_data
        except FileNotFoundError:
            # 文件不存在，返回空配置
            return default_config
        except json.JSONDecodeError:
            # 配置文件格式错误时抛出异常
            raise json.JSONDecodeError(f"数据库配置文件格式错误: {config_path}", "", 0)
        except Exception as e:
            print(f"加载数据库配置失败: {str(e)}")
            return default_config

    @staticmethod
    def get_default_db_type(username=None) -> str:
        if not username:
            raise ValueError("用户名不能为空")

        try:
            config_data = DatabaseConfigUtil.load_database_config(username)
            return config_data.get("defaultDbType", "mysql")
        except Exception as e:
            print(f"获取默认数据库类型失败: {str(e)}")
            return "mysql"

    @staticmethod
    def get_all_database_types(username=None) -> List[str]:

        if not username:
            raise ValueError("用户名不能为空")
        try:
            config_data = DatabaseConfigUtil.load_database_config(username)
            if "databases" in config_data and isinstance(config_data["databases"], dict):
                return list(config_data["databases"].keys())
            return []
        except Exception as e:
            print(f"获取数据库类型列表失败: {str(e)}")
            return []

    @staticmethod
    def get_database_config(username=None, db_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not username:
            raise ValueError("用户名不能为空")

        try:
            config_data = DatabaseConfigUtil.load_database_config(username)

            # 如果未指定数据库类型，使用默认类型
            if db_type is None:
                db_type = DatabaseConfigUtil.get_default_db_type(username)

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
    def get_all_database_configs(username=None) -> Dict[str, Dict[str, Any]]:

        if not username:
            raise ValueError("用户名不能为空")

        try:
            config_data = DatabaseConfigUtil.load_database_config(username)

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


