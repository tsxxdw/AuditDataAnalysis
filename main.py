from flask import Flask, render_template, request
import webbrowser
import threading
import time
import os

app = Flask(__name__)

# 定义一个函数，在短暂延迟后打开浏览器
def open_browser():
    # 等待1秒，确保Flask服务器已启动
    time.sleep(1)
    # 打开默认浏览器并访问应用URL
    webbrowser.open('http://127.0.0.1:5000/')

@app.route('/')
def index():
    return render_template('index.html', page_title='数据分析系统')

@app.route('/index_db')
def index_db():
    return render_template('index_db.html', page_title='数据库表结构管理')

@app.route('/index_import')
def index_import():
    return render_template('index_import.html', page_title='数据导入')

@app.route('/index_query')
def index_query():
    return render_template('index_query.html', page_title='业务查询')

@app.route('/settings')
def settings():
    return render_template('settings.html', page_title='系统设置')

if __name__ == '__main__':
    # 仅在主进程中打开浏览器
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Thread(target=open_browser).start()
    # 启动Flask应用
    app.run(debug=True) 