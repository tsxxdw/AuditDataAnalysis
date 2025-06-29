import json
import os
from service.session_service import session_service

class SettingsDatabaseService:
    """数据库设置服务，处理数据库配置的读取和保存"""
    
    def __init__(self):
        # 初始化时不设置固定路径，每次操作时动态获取配置路径
        pass
    
    def _get_current_username(self):
        user_info = session_service.get_user_info()
        username = user_info.get('username')
        if not username:
            raise ValueError("未登录或无法获取用户名")
        return username
    
    def get_config_path(self):
        username = self._get_current_username()
        
        # 首先检查settings子目录中的文件
        configuration_data_path = os.path.join('configuration_data', username, 'settings', 'database_config.json')
        # 确保父目录存在
        os.makedirs(os.path.dirname(configuration_data_path), exist_ok=True)
        return configuration_data_path

        
    def get_database_settings(self):
        try:
            config_path = self.get_config_path()
            
            # 默认空配置
            default_config = {"databases": {}, "defaultDbType": ""}
            
            # 检查配置文件是否存在
            if not os.path.exists(config_path):
                # 直接返回空配置
                return default_config
            
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except ValueError as e:
            # 重新抛出用户名相关的错误
            raise e
        except Exception as e:
            print(f"读取数据库配置出错: {str(e)}")
            # 读取出错时返回默认空配置
            return {"databases": {}, "defaultDbType": "mysql"}
    
    def save_database_settings(self, settings_data):
        try:
            username = self._get_current_username()
            config_path = self.get_config_path()
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 保存配置到文件
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(settings_data, file, indent=4, ensure_ascii=False)
            
            return True
        except ValueError as e:
            # 重新抛出用户名相关的错误
            raise e
        except Exception as e:
            print(f"保存数据库配置出错: {str(e)}")
            return False

# 创建服务实例
db_service = SettingsDatabaseService() 