"""
提示词模板服务

处理提示词模板的业务逻辑，包括模板的增删改查等操作
"""

import os
import json
import uuid
from datetime import datetime
from service.log.logger import app_logger
from config.global_config import get_project_root

class PromptTemplateService:
    def __init__(self):
        # 模板目录
        self.templates_dir = os.path.join(get_project_root(), 'config', 'prompt_templates')
        # 确保模板目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 示例模板数据 - 仅在目录为空时使用
        self.default_templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "数据异常分析",
                "description": "用于分析数据异常的提示词模板",
                "content": '{"system":"你是一位数据分析专家，专注于查找和解释数据中的异常和模式。你擅长识别异常数据点，理解其背后可能的原因，并提供改进建议。","user":"请分析以下数据中的异常情况，并给出可能的原因和解决方案：\\n\\n{数据}"}',
                "page": "数据分析",
                "tag": "通用",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "SQL优化建议",
                "description": "用于获取SQL优化建议的提示词模板",
                "content": '{"system":"你是一位SQL优化专家，精通各类数据库的性能调优。你熟悉索引优化、查询改写、执行计划分析等技术。","user":"请分析以下SQL语句，并给出具体的优化建议：\\n\\n```sql\\n{sql}\\n```"}',
                "page": "SQL查询",
                "tag": "通用",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Excel公式生成",
                "description": "帮助生成复杂的Excel公式",
                "content": '{"system":"你是一位Excel和电子表格专家，精通各种函数和公式。请提供清晰的说明并考虑到可能的数据类型问题。","user":"我需要一个Excel公式来{任务描述}。我的数据在{单元格范围}，格式是{数据格式}。"}',
                "page": "Excel导入",
                "tag": "通用",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # 初始化默认模板
        self.init_default_templates()
    
    def init_default_templates(self):
        """初始化默认模板"""
        # 检查目录是否为空
        if not os.listdir(self.templates_dir):
            app_logger.info("模板目录为空，初始化默认模板")
            for template in self.default_templates:
                self.save_template_to_file(template)
            app_logger.info(f"已创建 {len(self.default_templates)} 个默认模板")
    
    def save_template_to_file(self, template):
        """将模板保存到文件"""
        template_path = os.path.join(self.templates_dir, f"{template['id']}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        return template_path
    
    def load_template_from_file(self, template_id):
        """从文件加载模板"""
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        if not os.path.exists(template_path):
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            app_logger.error(f"加载模板文件失败: {template_path}, 错误: {str(e)}")
            return None
    
    def load_all_templates(self):
        """加载所有模板"""
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_id = filename[:-5]  # 移除 .json 后缀
                template = self.load_template_from_file(template_id)
                if template:
                    templates.append(template)
        
        # 按更新时间倒序排序
        templates.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return templates
    
    def delete_template_file(self, template_id):
        """删除模板文件"""
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        if os.path.exists(template_path):
            os.remove(template_path)
            return True
        return False
    
    def create_template(self, name, description, content, page=''):
        """创建新模板"""
        if not name:
            return False, "模板名称不能为空", None
        
        if not content:
            return False, "模板内容不能为空", None
        
        # 创建新模板
        new_template = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description or '',
            "content": content,
            "page": page or '',
            "tag": "通用",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存到文件
        self.save_template_to_file(new_template)
        
        return True, "创建模板成功", new_template
    
    def update_template(self, template_id, name, description, content, tag=None, page=None):
        """更新模板"""
        if not name:
            return False, "模板名称不能为空", None
        
        if not content:
            return False, "模板内容不能为空", None
        
        # 查找模板
        template = self.load_template_from_file(template_id)
        
        if not template:
            return False, f"未找到ID为 {template_id} 的模板", None
        
        # 更新模板
        template['name'] = name
        template['description'] = description or ''
        template['content'] = content
        if tag is not None:
            template['tag'] = tag
        elif 'tag' not in template:
            template['tag'] = "通用"
        if page is not None:
            template['page'] = page
        elif 'page' not in template:
            template['page'] = ''
        template['updated_at'] = datetime.now().isoformat()
        
        # 保存到文件
        self.save_template_to_file(template)
        
        return True, "更新模板成功", template

    def update_template_tag(self, template_id, tag):
        """更新模板标签"""
        if not tag:
            return False, "标签名称不能为空", None
        
        # 查找模板
        template = self.load_template_from_file(template_id)
        
        if not template:
            return False, f"未找到ID为 {template_id} 的模板", None
        
        # 更新标签
        template['tag'] = tag
        template['updated_at'] = datetime.now().isoformat()
        
        # 保存到文件
        self.save_template_to_file(template)
        
        return True, "更新标签成功", template
