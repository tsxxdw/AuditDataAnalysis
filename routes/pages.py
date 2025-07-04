"""
页面路由蓝图

管理所有页面的路由定义，包括首页、数据库管理、数据导入等页面
"""

from flask import Blueprint, render_template
from service.log.logger import app_logger

# 创建页面蓝图
pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    """首页"""
    app_logger.info("访问首页")
    return render_template('index.html', page_title='数据分析系统')

@pages_bp.route('/index_table_structure')
def index_table_structure():
    """数据库表结构管理页面"""
    app_logger.info("访问数据库表结构管理页面")
    return render_template('index_table_structure.html', page_title='数据库表结构管理')

@pages_bp.route('/index_import')
def index_import():
    """数据导入页面"""
    app_logger.info("访问数据导入页面")
    return render_template('index_import.html', page_title='数据导入')

@pages_bp.route('/index_analysis')
def index_analysis():
    """数据分析页面"""
    app_logger.info("访问数据分析页面")
    return render_template('index_analysis.html', page_title='数据分析')

@pages_bp.route('/index_file_upload')
def index_file_upload():
    """文件上传页面"""
    app_logger.info("访问文件上传页面")
    return render_template('index_file_upload.html', page_title='文件上传')

@pages_bp.route('/index_repair')
def index_repair():
    """数据修复页面"""
    app_logger.info("访问数据修复页面")
    return render_template('index_repair.html', page_title='数据修复')

@pages_bp.route('/index_validation')
def index_validation():
    """数据校验页面"""
    app_logger.info("访问数据校验页面")
    return render_template('index_validation.html', page_title='数据校验')

@pages_bp.route('/index_excel_validation')
def index_excel_validation():
    """EXCEL校验页面"""
    app_logger.info("访问EXCEL校验页面")
    return render_template('index_excel_validation.html', page_title='EXCEL校验')

@pages_bp.route('/index_sql')
def index_sql():
    """常用SQL页面"""
    app_logger.info("访问常用SQL页面")
    return render_template('index_sql.html', page_title='常用SQL')

@pages_bp.route('/index_one_to_one_import')
def index_one_to_one_import():
    """一对一导入页面"""
    app_logger.info("访问一对一导入页面")
    return render_template('index_one_to_one_import.html', page_title='一对一导入')

@pages_bp.route('/index_prompt_templates')
def index_prompt_templates():
    """提示词模板页面"""
    app_logger.info("访问提示词模板页面")
    return render_template('index_prompt_templates.html', page_title='提示词模板')

@pages_bp.route('/excel_repair')
def excel_repair():
    """EXCEL修复页面"""
    app_logger.info("访问EXCEL修复页面")
    return render_template('excel_repair.html', page_title='EXCEL修复')

@pages_bp.route('/settings')
def settings():
    """系统设置页面"""
    app_logger.info("访问系统设置页面")
    return render_template('settings.html', page_title='系统设置')

@pages_bp.route('/index_knowledge_base')
def index_knowledge_base():
    """本地知识库页面"""
    app_logger.info("访问本地知识库页面")
    return render_template('index_knowledge_base.html', page_title='本地知识库') 