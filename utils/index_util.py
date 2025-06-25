"""
索引文件工具类

提供读取JSON文件等功能
"""

import json
import os
from flask import current_app

class IndexUtil:
    @staticmethod
    def read_json_file(file_path):
        """
        读取JSON文件内容
        
        参数:
            file_path: JSON文件路径
            
        返回:
            成功: (True, data)
            失败: (False, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return True, data
        except Exception as e:
            current_app.logger.error(f"读取JSON文件失败: {str(e)}")
            return False, f"读取JSON文件失败: {str(e)}" 