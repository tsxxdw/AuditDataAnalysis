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

@pages_bp.route('/index_query')
def index_query():
    """业务查询页面"""
    app_logger.info("访问业务查询页面")
    return render_template('index_query.html', page_title='数据分析')

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

@pages_bp.route('/index_sql')
def index_sql():
    """常用SQL页面"""
    app_logger.info("访问常用SQL页面")
    return render_template('index_sql.html', page_title='常用SQL')

@pages_bp.route('/settings')
def settings():
    """系统设置页面"""
    app_logger.info("访问系统设置页面")
    return render_template('settings.html', page_title='系统设置') 