import json
import os
from pathlib import Path

class modelConfigUtil:
    """模型配置工具类，用于管理模型配置信息"""
    
    @staticmethod
    def _get_config_path():
        """获取配置文件路径"""
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        return os.path.join(project_root, "config", "settings", "model_config.json")
    
    @staticmethod
    def _load_config():
        """加载配置文件"""
        config_path = modelConfigUtil._get_config_path()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return None
            
    @staticmethod
    def _save_config(config_data):
        """保存配置文件"""
        config_path = modelConfigUtil._get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    @staticmethod
    def get_all_providers():
        """获取所有服务提供商信息
        
        Returns:
            dict: 所有服务提供商信息
        """
        config_data = modelConfigUtil._load_config()
        if config_data and "providers" in config_data:
            return config_data["providers"]
        return {}
    
    @staticmethod
    def get_default_model_info():
        """获取默认模型的相关信息
        
        Returns:
            dict: 包含默认模型的完整信息，包括提供商ID、模型ID以及模型详细信息
        """
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return None
            
        # 获取默认模型的基本信息
        default_model_basic = config_data.get("defaultModel", {})
        if not default_model_basic:
            return None
            
        provider_id = default_model_basic.get("provider_id")
        model_id = default_model_basic.get("model_id")
        
        if not provider_id or not model_id:
            return default_model_basic
            
        # 获取模型的详细信息
        providers = config_data.get("providers", {})
        provider = providers.get(provider_id, {})
        
        if provider and "models" in provider:
            for model in provider["models"]:
                if model.get("id") == model_id:
                    return {
                        "provider_id": provider_id,
                        "model_id": model_id,
                        "provider_name": provider.get("name"),
                        "model_details": model
                    }
        
        return default_model_basic
    
    @staticmethod
    def update_default_model(provider_id, model_id):
        """修改默认模型
        
        Args:
            provider_id (str): 提供商ID
            model_id (str): 模型ID
            
        Returns:
            bool: 是否成功修改
        """
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return False
            
        # 验证提供商和模型是否存在
        providers = config_data.get("providers", {})
        if provider_id not in providers:
            print(f"提供商 {provider_id} 不存在")
            return False
            
        provider = providers[provider_id]
        model_exists = False
        
        for model in provider.get("models", []):
            if model.get("id") == model_id:
                model_exists = True
                break
                
        if not model_exists:
            print(f"模型 {model_id} 在提供商 {provider_id} 中不存在")
            return False
            
        # 更新默认模型
        config_data["defaultModel"] = {
            "provider_id": provider_id,
            "model_id": model_id
        }
        
        return modelConfigUtil._save_config(config_data)
    
    @staticmethod
    def update_model_visibility(provider_id, model_id, visible):
        """修改某一个模型是否可见
        
        Args:
            provider_id (str): 提供商ID
            model_id (str): 模型ID
            visible (bool): 是否可见
            
        Returns:
            bool: 是否成功修改
        """
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return False
            
        # 验证提供商是否存在
        providers = config_data.get("providers", {})
        if provider_id not in providers:
            print(f"提供商 {provider_id} 不存在")
            return False
            
        provider = providers[provider_id]
        model_found = False
        
        # 更新模型可见性
        for model in provider.get("models", []):
            if model.get("id") == model_id:
                model["visible"] = visible
                model_found = True
                break
                
        if not model_found:
            print(f"模型 {model_id} 在提供商 {provider_id} 中不存在")
            return False
            
        return modelConfigUtil._save_config(config_data)
        
    @staticmethod
    def get_provider_models(provider_id, only_visible=False):
        """根据提供商ID获取对应的模型列表
        
        Args:
            provider_id (str): 提供商ID
            only_visible (bool, optional): 是否只返回可见的模型. 默认为False.
            
        Returns:
            list: 模型列表，如果提供商不存在则返回空列表
        """
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return []
            
        providers = config_data.get("providers", {})
        if provider_id not in providers:
            print(f"提供商 {provider_id} 不存在")
            return []
            
        provider = providers[provider_id]
        models = provider.get("models", [])
        
        # 如果需要过滤只返回可见的模型
        if only_visible:
            models = [model for model in models if model.get("visible", False)]
            
        return models
        
    @staticmethod
    def add_model(provider_id, model_info):
        """向指定提供商添加新模型
        
        Args:
            provider_id (str): 提供商ID
            model_info (dict): 模型信息，必须包含以下字段:
                - id (str): 模型ID
                - name (str): 模型名称
                - visible (bool): 是否可见
                - category (str): 模型分类
                - description (str): 模型描述
                
        Returns:
            bool: 是否成功添加
        """
        # 验证必要的模型信息是否存在
        required_fields = ["id", "name", "category", "description"]
        for field in required_fields:
            if field not in model_info:
                print(f"缺少必要的模型信息字段: {field}")
                return False
                
        # 如果没有提供visible字段，默认为True
        if "visible" not in model_info:
            model_info["visible"] = True
            
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return False
            
        # 验证提供商是否存在
        providers = config_data.get("providers", {})
        if provider_id not in providers:
            print(f"提供商 {provider_id} 不存在")
            return False
            
        provider = providers[provider_id]
        
        # 检查模型是否已经存在
        for model in provider.get("models", []):
            if model.get("id") == model_info["id"]:
                print(f"模型 {model_info['id']} 在提供商 {provider_id} 中已存在")
                return False
                
        # 添加新模型
        if "models" not in provider:
            provider["models"] = []
            
        provider["models"].append(model_info)
        
        return modelConfigUtil._save_config(config_data)
        
    @staticmethod
    def update_provider(provider_id, data):
        """更新服务提供商配置
        
        Args:
            provider_id (str): 提供商ID
            data (dict): 需要更新的数据，可包含以下字段:
                - apiKey (str): API密钥
                - apiUrl (str): API地址
                - apiVersion (str): API版本
                - enabled (bool): 是否启用
                - name (str): 提供商名称
                
        Returns:
            bool: 是否成功更新
        """
        config_data = modelConfigUtil._load_config()
        if not config_data:
            return False
            
        # 验证提供商是否存在
        providers = config_data.get("providers", {})
        if provider_id not in providers:
            print(f"提供商 {provider_id} 不存在")
            return False
            
        # 只更新允许的字段
        allowed_fields = ['apiKey', 'apiUrl', 'apiVersion', 'enabled', 'name']
        for field in allowed_fields:
            if field in data:
                # 对API密钥特殊处理：如果需要加密，可以在这里添加加密逻辑
                config_data['providers'][provider_id][field] = data[field]
        
        return modelConfigUtil._save_config(config_data)
