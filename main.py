import os
from flask import Flask, render_template, send_from_directory
import webbrowser
import threading
import time
from routes.settings.setting_relational_database_api import settings_database_bp
from routes.settings.setting_vector_database_api import settings_vector_database_bp  # 新增导入向量数据库设置API蓝图
from routes.settings.setting_log_api import log_settings_bp
from routes.index_file_upload_api import file_upload_bp, ensure_dir_exists, UPLOAD_FOLDER
from routes.index_import_api import import_api_bp
from routes.index_one_to_one_import_api import index_one_to_one_import_bp
from routes.index_table_structure_api import index_table_structure_bp
from routes.common.common_database_api import common_api_bp
from routes.index_analysis_api import index_analysis_bp
from routes.index_prompt_templates_api import index_prompt_templates_bp
from routes.index_excel_validation_api import excel_validation_bp
from routes.index_validation_api import index_validation_bp  # 导入数据校验API蓝图
from routes.pages import pages_bp
from routes.excel_repair_api import excel_repair_api  # 导入EXCEL修复API蓝图
from routes.knowledge_base_api import knowledge_base_api  # 导入知识库API蓝图
from routes.user_management_api import user_management_api  # 导入用户管理API蓝图
from service.log.logger import app_logger
from service.log.middleware import init_log_middleware
from service.exception import register_error_handlers
from service.database.db_pool_manager import DatabasePoolManager
from service.knowledge_base import init_knowledge_base  # 导入知识库初始化函数
from config.global_config import init_project_root
from routes.common.model_common_service_api import model_api  # 导入模型服务API蓝图
from routes.settings.setting_model_server_api import model_settings_api  # 导入模型设置API蓝图
from routes.index_repair_api import index_repair_bp  # 注册数据修复API路由

# 初始化项目根路径（全局配置）
project_root = init_project_root()
app_logger.info(f"项目根路径: {project_root}")

# 确保文件上传目录存在
ensure_dir_exists(UPLOAD_FOLDER)
app_logger.info(f"确保文件上传目录存在: {os.path.abspath(UPLOAD_FOLDER)}")

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(settings_database_bp)
app.register_blueprint(settings_vector_database_bp)  # 注册向量数据库设置API蓝图
app.register_blueprint(log_settings_bp)
app.register_blueprint(file_upload_bp)
app.register_blueprint(import_api_bp)
app.register_blueprint(index_one_to_one_import_bp)
app.register_blueprint(index_table_structure_bp)  # 注册表结构相关API路由
app.register_blueprint(common_api_bp)  # 注册通用API路由
app.register_blueprint(index_analysis_bp)  # 注册数据分析API路由
app.register_blueprint(index_prompt_templates_bp)  # 注册提示词模板API路由
app.register_blueprint(excel_validation_bp)  # 注册Excel校验API路由
app.register_blueprint(index_validation_bp)  # 注册数据校验API路由
app.register_blueprint(pages_bp)  # 注册页面路由蓝图
app.register_blueprint(model_api)  # 注册模型服务API路由
app.register_blueprint(model_settings_api)  # 注册模型设置API路由
app.register_blueprint(index_repair_bp)  # 注册数据修复API路由
app.register_blueprint(excel_repair_api)  # 注册EXCEL修复API路由
app.register_blueprint(knowledge_base_api)  # 注册知识库API路由
app.register_blueprint(user_management_api)  # 注册用户管理API路由

# 初始化中间件
init_log_middleware(app)

# 注册异常处理器
register_error_handlers(app)

# 初始化知识库服务
init_knowledge_base()

# 在应用关闭时关闭所有连接池
@app.teardown_appcontext
def shutdown_db_pools(exception=None):
    DatabasePoolManager.get_instance().shutdown()

# 定义一个函数，在短暂延迟后打开浏览器
def open_browser():
    # 等待1秒，确保Flask服务器已启动
    time.sleep(1)
    # 打开默认浏览器并访问应用URL
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    app_logger.info("启动应用服务器")
    
    # 仅在主进程中打开浏览器
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Thread(target=open_browser).start()
    
    # 启动Flask应用
    app.run(debug=True) 