from flask import Flask, render_template, make_response, url_for, redirect, request, session, flash
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message = 'Для продолжения необходимо пройти авторизацию'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login

USERS_DB = [{'id': '01', 'login': 'user', 'pass': 'qwerty'}]

@login_manager.user_loader
def load_user(user_id):
    for user in USERS_DB:
        if user_id == user['id']:
            return User(user_id, user['login'])

@app.route('/')
def index():
    url = request.url
    return render_template('index.html', url=url)

@app.route('/counter')
def counter():
    session['counter'] = session.get('counter', 0) + 1
    return render_template('counter.html')

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        return render_template('auth.html')
    
    for user in USERS_DB:
        if request.form.get("login", "") == user['login'] and \
        request.form.get("pass", "") == user['pass']:
            login_user(User(user['id'], user['login']), remember=request.form.get("remember") == "on")
            flash('Успешная авторизация', category='success')
            return redirect(request.args.get('next', url_for('index')))

    flash('Логин или пароль неправильный!', category='danger')
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))