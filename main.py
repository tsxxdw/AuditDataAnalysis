from flask import Flask, render_template
import webbrowser
import threading
import time
import os
from routes.settings.settings_database_api import settings_database_bp
from routes.settings.log_settings_api import log_settings_bp
from service.log.logger import app_logger
from service.log.middleware import init_log_middleware
from service.exception import register_error_handlers

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(settings_database_bp)
app.register_blueprint(log_settings_bp)

# 初始化中间件
init_log_middleware(app)

# 注册异常处理器
register_error_handlers(app)

# 定义一个函数，在短暂延迟后打开浏览器
def open_browser():
    # 等待1秒，确保Flask服务器已启动
    time.sleep(1)
    # 打开默认浏览器并访问应用URL
    webbrowser.open('http://127.0.0.1:5000/')

@app.route('/')
def index():
    app_logger.info("访问首页")
    return render_template('index.html', page_title='数据分析系统')

@app.route('/index_db')
def index_db():
    app_logger.info("访问数据库表结构管理页面")
    return render_template('index_db.html', page_title='数据库表结构管理')

@app.route('/index_import')
def index_import():
    app_logger.info("访问数据导入页面")
    return render_template('index_import.html', page_title='数据导入')

@app.route('/index_query')
def index_query():
    app_logger.info("访问业务查询页面")
    return render_template('index_query.html', page_title='业务查询')

@app.route('/settings')
def settings():
    app_logger.info("访问系统设置页面")
    return render_template('settings.html', page_title='系统设置')

if __name__ == '__main__':
    app_logger.info("启动应用服务器")
    
    # 仅在主进程中打开浏览器
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Thread(target=open_browser).start()
    
    # 启动Flask应用
    app.run(debug=True) 