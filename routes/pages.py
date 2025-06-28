"""
页面路由蓝图

管理所有页面的路由定义，包括首页、数据库管理、数据导入等页面
"""

from flask import Blueprint, render_template, redirect, url_for, session, request
from service.log.logger import app_logger
from service.auth.auth_middleware import login_required, admin_required, has_permission

# 创建页面蓝图
pages_bp = Blueprint('pages', __name__)

# 判断是否为AJAX请求的辅助函数
def is_ajax_request():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

@pages_bp.route('/login')
def login():
    """登录页面"""
    # 如果用户已登录，重定向到首页
    if 'user_info' in session:
        return redirect(url_for('pages.index'))

    app_logger.info("访问登录页面")
    return render_template('login.html', page_title='登录')

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

# 设置子页面路由
@pages_bp.route('/settings/setting_personal')
def settings_personal():
    """个人设置页面"""
    app_logger.info("访问个人设置页面")

    # 如果是AJAX请求，只返回子页面内容
    if is_ajax_request():
        return render_template('settings/setting_personal.html')

    # 常规请求返回完整页面
    return render_template('settings.html', page_title='个人设置', active_tab='personal-settings')

@pages_bp.route('/settings/setting_relational_database')
def setting_relational_database():
    """数据库设置页面"""
    app_logger.info("访问数据库设置页面")

    # 如果是AJAX请求，只返回子页面内容
    if is_ajax_request():
        return render_template('settings/setting_relational_database.html')

    # 常规请求返回完整页面
    return render_template('settings.html', page_title='关系型数据库设置', active_tab='db-settings')

@pages_bp.route('/settings/setting_vector_database')
def settings_vector_database():
    """向量数据库设置页面"""
    app_logger.info("访问向量数据库设置页面")

    # 如果是AJAX请求，只返回子页面内容
    if is_ajax_request():
        return render_template('settings/setting_vector_database.html')

    # 常规请求返回完整页面
    return render_template('settings.html', page_title='向量数据库设置', active_tab='vector-db-settings')

@pages_bp.route('/settings/setting_log')
def settings_log():
    """日志设置页面"""
    app_logger.info("访问日志设置页面")

    # 如果是AJAX请求，只返回子页面内容
    if is_ajax_request():
        return render_template('settings/setting_log.html')

    # 常规请求返回完整页面
    return render_template('settings.html', page_title='日志设置', active_tab='log-settings')

@pages_bp.route('/settings/setting_model_server')
def settings_model_service():
    """模型服务设置页面"""
    app_logger.info("访问模型服务设置页面")

    # 如果是AJAX请求，只返回子页面内容
    if is_ajax_request():
        return render_template('settings/setting_model_server.html')

    # 常规请求返回完整页面
    return render_template('settings.html', page_title='模型服务', active_tab='model-service')

@pages_bp.route('/share_base')
def share_base():
    """股票基本信息页面"""
    app_logger.info("访问股票基本信息页面")
    return render_template('share_base.html', page_title='股票基本信息')
    return render_template('settings.html', page_title='系统设置')

@pages_bp.route('/index_knowledge_base')
def index_knowledge_base():
    """本地知识库页面"""
    app_logger.info("访问本地知识库页面")
    return render_template('index_knowledge_base.html', page_title='本地知识库')

@pages_bp.route('/user_management')
@admin_required
def user_management():
    """用户管理页面"""
    app_logger.info("访问用户管理页面")
    return render_template('user_management.html', page_title='用户管理')