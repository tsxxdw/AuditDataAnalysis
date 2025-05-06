"""
提示词模板 API

负责处理与提示词模板相关的API请求
"""

import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from config.global_config import get_project_root

# 创建蓝图
index_prompt_templates_bp = Blueprint('index_prompt_templates_api', __name__, url_prefix='/api/prompt_templates')

# 模板目录
TEMPLATES_DIR = os.path.join(get_project_root(), 'config', 'prompt_templates')

# 确保模板目录存在
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# 示例模板数据 - 仅在目录为空时使用
DEFAULT_TEMPLATES = [
    {
        "id": str(uuid.uuid4()),
        "name": "数据异常分析",
        "description": "用于分析数据异常的提示词模板",
        "content": '{"system":"你是一位数据分析专家，专注于查找和解释数据中的异常和模式。你擅长识别异常数据点，理解其背后可能的原因，并提供改进建议。","user":"请分析以下数据中的异常情况，并给出可能的原因和解决方案：\\n\\n{数据}"}',
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "SQL优化建议",
        "description": "用于获取SQL优化建议的提示词模板",
        "content": '{"system":"你是一位SQL优化专家，精通各类数据库的性能调优。你熟悉索引优化、查询改写、执行计划分析等技术。","user":"请分析以下SQL语句，并给出具体的优化建议：\\n\\n```sql\\n{sql}\\n```"}',
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Excel公式生成",
        "description": "帮助生成复杂的Excel公式",
        "content": '{"system":"你是一位Excel和电子表格专家，精通各种函数和公式。请提供清晰的说明并考虑到可能的数据类型问题。","user":"我需要一个Excel公式来{任务描述}。我的数据在{单元格范围}，格式是{数据格式}。"}',
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]

# 初始化默认模板（仅在目录为空时）
def init_default_templates():
    """初始化默认模板"""
    # 检查目录是否为空
    if not os.listdir(TEMPLATES_DIR):
        app_logger.info("模板目录为空，初始化默认模板")
        for template in DEFAULT_TEMPLATES:
            save_template_to_file(template)
        app_logger.info(f"已创建 {len(DEFAULT_TEMPLATES)} 个默认模板")

# 保存模板到文件
def save_template_to_file(template):
    """将模板保存到文件"""
    template_path = os.path.join(TEMPLATES_DIR, f"{template['id']}.json")
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    return template_path

# 从文件加载模板
def load_template_from_file(template_id):
    """从文件加载模板"""
    template_path = os.path.join(TEMPLATES_DIR, f"{template_id}.json")
    if not os.path.exists(template_path):
        return None
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        app_logger.error(f"加载模板文件失败: {template_path}, 错误: {str(e)}")
        return None

# 加载所有模板
def load_all_templates():
    """加载所有模板"""
    templates = []
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.json'):
            template_id = filename[:-5]  # 移除 .json 后缀
            template = load_template_from_file(template_id)
            if template:
                templates.append(template)
    
    # 按更新时间倒序排序
    templates.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    return templates

# 删除模板文件
def delete_template_file(template_id):
    """删除模板文件"""
    template_path = os.path.join(TEMPLATES_DIR, f"{template_id}.json")
    if os.path.exists(template_path):
        os.remove(template_path)
        return True
    return False

# 初始化默认模板
init_default_templates()

@index_prompt_templates_bp.route('/list', methods=['GET'])
def get_templates():
    """获取模板列表"""
    app_logger.info("获取提示词模板列表")
    
    try:
        templates = load_all_templates()
        
        return jsonify({
            "success": True,
            "message": "获取模板列表成功", 
            "templates": templates
        })
    except Exception as e:
        app_logger.error(f"获取模板列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取模板列表失败: {str(e)}",
            "templates": []
        }), 500

@index_prompt_templates_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """获取单个模板详情"""
    app_logger.info(f"获取提示词模板 ID: {template_id}")
    
    try:
        template = load_template_from_file(template_id)
        
        if not template:
            return jsonify({
                "success": False,
                "message": f"未找到ID为 {template_id} 的模板"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "获取模板成功",
            "template": template
        })
    except Exception as e:
        app_logger.error(f"获取模板详情失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取模板详情失败: {str(e)}"
        }), 500

@index_prompt_templates_bp.route('/create', methods=['POST'])
def create_template():
    """创建新模板"""
    app_logger.info("创建提示词模板")
    
    try:
        data = request.json
        
        # 参数验证
        if not data.get('name'):
            return jsonify({"success": False, "message": "模板名称不能为空"}), 400
        
        if not data.get('content'):
            return jsonify({"success": False, "message": "模板内容不能为空"}), 400
        
        # 创建新模板
        new_template = {
            "id": str(uuid.uuid4()),
            "name": data.get('name'),
            "description": data.get('description', ''),
            "content": data.get('content'),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存到文件
        save_template_to_file(new_template)
        
        return jsonify({
            "success": True,
            "message": "创建模板成功",
            "template": new_template
        })
    except Exception as e:
        app_logger.error(f"创建模板失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"创建模板失败: {str(e)}"
        }), 500

@index_prompt_templates_bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id):
    """更新模板"""
    app_logger.info(f"更新提示词模板 ID: {template_id}")
    
    try:
        data = request.json
        
        # 参数验证
        if not data.get('name'):
            return jsonify({"success": False, "message": "模板名称不能为空"}), 400
        
        if not data.get('content'):
            return jsonify({"success": False, "message": "模板内容不能为空"}), 400
        
        # 查找模板
        template = load_template_from_file(template_id)
        
        if not template:
            return jsonify({
                "success": False,
                "message": f"未找到ID为 {template_id} 的模板"
            }), 404
        
        # 更新模板
        template['name'] = data.get('name')
        template['description'] = data.get('description', '')
        template['content'] = data.get('content')
        template['updated_at'] = datetime.now().isoformat()
        
        # 保存到文件
        save_template_to_file(template)
        
        return jsonify({
            "success": True,
            "message": "更新模板成功",
            "template": template
        })
    except Exception as e:
        app_logger.error(f"更新模板失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"更新模板失败: {str(e)}"
        }), 500

@index_prompt_templates_bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除模板"""
    app_logger.info(f"删除提示词模板 ID: {template_id}")
    
    try:
        # 删除模板文件
        success = delete_template_file(template_id)
        
        if not success:
            return jsonify({
                "success": False,
                "message": f"未找到ID为 {template_id} 的模板"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "删除模板成功"
        })
    except Exception as e:
        app_logger.error(f"删除模板失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"删除模板失败: {str(e)}"
        }), 500 