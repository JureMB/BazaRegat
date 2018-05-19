from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)

bootstrap = Bootstrap(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/regate')
def regate():
    return render_template('regate.html')

@app.route('/jadralci')
def jadralci():
    return render_template('jadralci.html')

@app.route('/lestvica')
def lestvica():
    return render_template('lestvica.html')