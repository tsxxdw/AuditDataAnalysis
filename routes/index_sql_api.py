"""
常用SQL API

负责处理与常用SQL相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.log.logger import app_logger

# 创建蓝图
index_sql_bp = Blueprint('index_sql_api', __name__, url_prefix='/api/sql')

@index_sql_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取SQL分类列表"""
    app_logger.info("获取SQL分类列表")
    # 此处添加获取SQL分类列表的逻辑
    return jsonify({"message": "获取SQL分类列表成功", "categories": []})

@index_sql_bp.route('/templates', methods=['GET'])
def get_templates():
    """获取SQL模板列表"""
    app_logger.info("获取SQL模板列表")
    # 此处添加获取SQL模板列表的逻辑
    return jsonify({"message": "获取SQL模板列表成功", "templates": []})

@index_sql_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """获取SQL模板详情"""
    app_logger.info(f"获取SQL模板详情：{template_id}")
    # 此处添加获取SQL模板详情的逻辑
    return jsonify({"message": f"获取SQL模板详情成功", "template": {}})

@index_sql_bp.route('/templates', methods=['POST'])
def add_template():
    """添加SQL模板"""
    app_logger.info("添加SQL模板")
    # 此处添加添加SQL模板的逻辑
    return jsonify({"message": "添加SQL模板成功", "template_id": 0})

@index_sql_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """更新SQL模板"""
    app_logger.info(f"更新SQL模板：{template_id}")
    # 此处添加更新SQL模板的逻辑
    return jsonify({"message": f"更新SQL模板成功"})

@index_sql_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除SQL模板"""
    app_logger.info(f"删除SQL模板：{template_id}")
    # 此处添加删除SQL模板的逻辑
    return jsonify({"message": f"删除SQL模板成功"}) 