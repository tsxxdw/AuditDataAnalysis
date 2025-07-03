from flask import Flask, render_template
from routes.ai_chat_api import ai_chat_api

# 创建Flask应用
app = Flask(__name__)

# 注册蓝图
app.register_blueprint(ai_chat_api)

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# AI聊天页面
@app.route('/ai_chat')
def ai_chat():
    return render_template('ai_chat.html')

# 启动应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 