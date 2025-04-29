from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index_db')
def index_db():
    return render_template('index_db.html')

@app.route('/index_import')
def index_import():
    return render_template('index_import.html')

@app.route('/index_query')
def index_query():
    return render_template('index_query.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True) 