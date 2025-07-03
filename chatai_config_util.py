import os
import json
import shutil
from typing import Dict, List, Optional, Any
import uuid
import datetime

class ChatAIConfigUtil:
    """
    ChatAI配置工具类，用于管理工作区、会话和向量数据库配置
    所有方法都是静态方法，不需要实例化
    """
    
    # 配置文件路径
    CONFIG_FILE_PATH = "configuration_data/admin/chatai/chatai_config.json"
    # 工作区文件夹路径
    WORKSPACE_DIR_PATH = "file/admin/aichat/workspace"
    
    @staticmethod
    def ensure_directories_exist():
        """确保必要的目录结构存在"""
        os.makedirs(os.path.dirname(ChatAIConfigUtil.CONFIG_FILE_PATH), exist_ok=True)
        os.makedirs(ChatAIConfigUtil.WORKSPACE_DIR_PATH, exist_ok=True)
    
    @staticmethod
    def load_config() -> Dict:
        """加载配置文件，如果不存在则创建默认配置"""
        ChatAIConfigUtil.ensure_directories_exist()
        
        if not os.path.exists(ChatAIConfigUtil.CONFIG_FILE_PATH):
            default_config = {
                "workspaces": [],
                "vector_collections": []
            }
            ChatAIConfigUtil.save_config(default_config)
            return default_config
        
        try:
            with open(ChatAIConfigUtil.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            default_config = {
                "workspaces": [],
                "vector_collections": []
            }
            ChatAIConfigUtil.save_config(default_config)
            return default_config
    
    @staticmethod
    def save_config(config: Dict) -> bool:
        """保存配置到文件"""
        ChatAIConfigUtil.ensure_directories_exist()
        
        try:
            with open(ChatAIConfigUtil.CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
    
    @staticmethod
    def create_workspace(workspace_name: str) -> Dict:
        """
        创建新的工作区
        
        Args:
            workspace_name: 工作区名称
            
        Returns:
            新创建的工作区信息
        """
        # 生成工作区ID
        workspace_id = str(uuid.uuid4())
        
        # 创建工作区目录
        workspace_dir = os.path.join(ChatAIConfigUtil.WORKSPACE_DIR_PATH, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # 更新配置文件
        config = ChatAIConfigUtil.load_config()
        
        # 创建工作区对象
        workspace = {
            "id": workspace_id,
            "name": workspace_name,
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessions": []
        }
        
        # 添加到配置
        config["workspaces"].append(workspace)
        
        # 保存配置
        ChatAIConfigUtil.save_config(config)
        
        return workspace
    
    @staticmethod
    def create_session(workspace_id: str, session_name: str) -> Optional[Dict]:
        """
        在指定工作区下创建新会话
        
        Args:
            workspace_id: 工作区ID
            session_name: 会话名称
            
        Returns:
            新创建的会话信息，如果工作区不存在则返回None
        """
        # 加载配置
        config = ChatAIConfigUtil.load_config()
        
        # 查找工作区
        workspace = None
        for ws in config["workspaces"]:
            if ws["id"] == workspace_id:
                workspace = ws
                break
        
        if workspace is None:
            print(f"工作区不存在: {workspace_id}")
            return None
        
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建会话文件
        workspace_dir = os.path.join(ChatAIConfigUtil.WORKSPACE_DIR_PATH, workspace_id)
        session_file = os.path.join(workspace_dir, f"{session_id}.txt")
        
        # 创建空会话文件
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"# 会话: {session_name}\n# 创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 创建会话对象
        session = {
            "id": session_id,
            "name": session_name,
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": session_file
        }
        
        # 添加到工作区
        workspace["sessions"].append(session)
        
        # 保存配置
        ChatAIConfigUtil.save_config(config)
        
        return session
    
    @staticmethod
    def get_all_workspaces() -> List[Dict]:
        """获取所有工作区信息"""
        config = ChatAIConfigUtil.load_config()
        return config.get("workspaces", [])
    
    @staticmethod
    def get_workspace(workspace_id: str) -> Optional[Dict]:
        """获取指定ID的工作区信息"""
        config = ChatAIConfigUtil.load_config()
        
        for workspace in config.get("workspaces", []):
            if workspace["id"] == workspace_id:
                return workspace
        
        return None
    
    @staticmethod
    def get_sessions(workspace_id: str) -> List[Dict]:
        """获取指定工作区下的所有会话"""
        workspace = ChatAIConfigUtil.get_workspace(workspace_id)
        
        if workspace:
            return workspace.get("sessions", [])
        
        return []
    
    @staticmethod
    def get_session(workspace_id: str, session_id: str) -> Optional[Dict]:
        """获取指定工作区下的指定会话"""
        sessions = ChatAIConfigUtil.get_sessions(workspace_id)
        
        for session in sessions:
            if session["id"] == session_id:
                return session
        
        return None
    
    @staticmethod
    def save_message_to_session(workspace_id: str, session_id: str, sender: str, message: str) -> bool:
        """
        保存消息到会话文件
        
        Args:
            workspace_id: 工作区ID
            session_id: 会话ID
            sender: 发送者 ('user' 或 'ai')
            message: 消息内容
            
        Returns:
            是否保存成功
        """
        session = ChatAIConfigUtil.get_session(workspace_id, session_id)
        
        if not session:
            print(f"会话不存在: {workspace_id}/{session_id}")
            return False
        
        file_path = session.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            print(f"会话文件不存在: {file_path}")
            return False
        
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sender_name = "用户" if sender == "user" else "AI"
                f.write(f"[{timestamp}] {sender_name}:\n{message}\n\n")
            return True
        except Exception as e:
            print(f"保存消息失败: {str(e)}")
            return False
    
    @staticmethod
    def rename_workspace(workspace_id: str, new_name: str) -> bool:
        """重命名工作区"""
        config = ChatAIConfigUtil.load_config()
        
        for workspace in config.get("workspaces", []):
            if workspace["id"] == workspace_id:
                workspace["name"] = new_name
                ChatAIConfigUtil.save_config(config)
                return True
        
        return False
    
    @staticmethod
    def rename_session(workspace_id: str, session_id: str, new_name: str) -> bool:
        """重命名会话"""
        workspace = ChatAIConfigUtil.get_workspace(workspace_id)
        
        if not workspace:
            return False
        
        for session in workspace.get("sessions", []):
            if session["id"] == session_id:
                session["name"] = new_name
                
                # 更新会话文件中的名称
                file_path = session.get("file_path")
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        if lines and lines[0].startswith("# 会话:"):
                            lines[0] = f"# 会话: {new_name}\n"
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                    except Exception as e:
                        print(f"更新会话文件失败: {str(e)}")
                
                config = ChatAIConfigUtil.load_config()
                ChatAIConfigUtil.save_config(config)
                return True
        
        return False
    
    @staticmethod
    def delete_workspace(workspace_id: str) -> bool:
        """删除工作区及其所有会话"""
        config = ChatAIConfigUtil.load_config()
        
        # 查找工作区索引
        workspace_index = -1
        for i, workspace in enumerate(config.get("workspaces", [])):
            if workspace["id"] == workspace_id:
                workspace_index = i
                break
        
        if workspace_index == -1:
            return False
        
        # 删除工作区目录
        workspace_dir = os.path.join(ChatAIConfigUtil.WORKSPACE_DIR_PATH, workspace_id)
        if os.path.exists(workspace_dir):
            try:
                shutil.rmtree(workspace_dir)
            except Exception as e:
                print(f"删除工作区目录失败: {str(e)}")
        
        # 从配置中删除工作区
        config["workspaces"].pop(workspace_index)
        ChatAIConfigUtil.save_config(config)
        
        return True
    
    @staticmethod
    def delete_session(workspace_id: str, session_id: str) -> bool:
        """删除指定会话"""
        workspace = ChatAIConfigUtil.get_workspace(workspace_id)
        
        if not workspace:
            return False
        
        # 查找会话索引
        session_index = -1
        for i, session in enumerate(workspace.get("sessions", [])):
            if session["id"] == session_id:
                session_index = i
                session_to_delete = session
                break
        
        if session_index == -1:
            return False
        
        # 删除会话文件
        file_path = session_to_delete.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"删除会话文件失败: {str(e)}")
        
        # 从配置中删除会话
        workspace["sessions"].pop(session_index)
        
        config = ChatAIConfigUtil.load_config()
        ChatAIConfigUtil.save_config(config)
        
        return True
    
    @staticmethod
    def create_vector_collection(collection_name: str, description: str = "") -> Dict:
        """创建向量数据库集合"""
        config = ChatAIConfigUtil.load_config()
        
        collection = {
            "id": str(uuid.uuid4()),
            "name": collection_name,
            "description": description,
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "vector_collections" not in config:
            config["vector_collections"] = []
        
        config["vector_collections"].append(collection)
        ChatAIConfigUtil.save_config(config)
        
        return collection
    
    @staticmethod
    def get_all_vector_collections() -> List[Dict]:
        """获取所有向量数据库集合"""
        config = ChatAIConfigUtil.load_config()
        return config.get("vector_collections", []) 