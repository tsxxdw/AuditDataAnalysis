import json
import os

class SettingsDatabaseController:
    """数据库设置控制器，处理数据库配置的读取和保存"""
    
    def __init__(self):
        # 配置文件路径
        self.config_path = 'config/settings/database_config.json'
        
    def get_database_settings(self):
        """获取数据库设置"""
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                # 如果不存在，返回默认空配置
                return {"databases": {}, "defaultDbType": "mysql"}
            
            # 读取配置文件
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"读取数据库配置出错: {str(e)}")
            # 读取出错时返回默认空配置
            return {"databases": {}, "defaultDbType": "mysql"}
    
    def save_database_settings(self, settings_data):
        """保存数据库设置
        
        参数:
            settings_data: 要保存的数据库设置数据
        
        返回:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 保存配置到文件
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(settings_data, file, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存数据库配置出错: {str(e)}")
            return False

# 创建控制器实例
db_controller = SettingsDatabaseController() 