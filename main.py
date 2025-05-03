import os
from flask import Flask, render_template, send_from_directory
import webbrowser
import threading
import time
from routes.settings.settings_database_api import settings_database_bp
from routes.settings.log_settings_api import log_settings_bp
from routes.index_file_upload_api import file_upload_bp
from routes.index_import_api import import_api_bp
from routes.pages import pages_bp
from service.log.logger import app_logger
from service.log.middleware import init_log_middleware
from service.exception import register_error_handlers
from service.database.db_pool_manager import DatabasePoolManager

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(settings_database_bp)
app.register_blueprint(log_settings_bp)
app.register_blueprint(file_upload_bp)
app.register_blueprint(import_api_bp)
app.register_blueprint(pages_bp)  # 注册页面路由蓝图

# 初始化中间件
init_log_middleware(app)

# 注册异常处理器
register_error_handlers(app)

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