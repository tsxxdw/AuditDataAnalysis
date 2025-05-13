"""
提示词模板 API

负责处理与提示词模板相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.log.logger import app_logger
from service.prompt_templates.index_prompt_templates_service import PromptTemplateService

# 创建蓝图
index_prompt_templates_bp = Blueprint('index_prompt_templates_api', __name__, url_prefix='/api/prompt_templates')

# 创建服务实例
template_service = PromptTemplateService()

@index_prompt_templates_bp.route('/list', methods=['GET'])
def get_templates():
    """获取模板列表"""
    app_logger.info("获取提示词模板列表")
    
    try:
        templates = template_service.load_all_templates()
        
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
        template = template_service.load_template_from_file(template_id)
        
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
        
        success, message, template = template_service.create_template(
            name=data.get('name'),
            description=data.get('description', ''),
            content=data.get('content')
        )
        
        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400
        
        return jsonify({
            "success": True,
            "message": message,
            "template": template
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
        
        success, message, template = template_service.update_template(
            template_id=template_id,
            name=data.get('name'),
            description=data.get('description', ''),
            content=data.get('content')
        )
        
        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 404 if "未找到" in message else 400
        
        return jsonify({
            "success": True,
            "message": message,
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
        success = template_service.delete_template_file(template_id)
        
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