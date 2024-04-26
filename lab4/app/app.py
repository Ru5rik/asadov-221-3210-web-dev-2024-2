from flask import Flask, render_template, make_response, url_for, redirect, request, session, flash
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required
from mysqldb import DBConnector

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db_connector = DBConnector(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message = 'Для продолжения необходимо пройти авторизацию'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    query = 'SELECT ID, Login FROM Users WHERE ID=%s'
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
    if user:
        return User(user_id, user.Login)
    return None

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
    
    login = request.form.get("login", "")
    password = request.form.get("pass", "")
    remember = request.form.get("remember") == "on"

    query = 'SELECT ID, Login FROM Users WHERE Login=%s AND PassHash=SHA2(%s, 256)'
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (login, password))
        user = cursor.fetchone()
    if user:
        login_user(User(user.ID, user.Login), remember=remember)
        flash('Успешная авторизация', category='success')
        target_page = request.args.get("next", url_for("index"))
        return redirect(target_page)

    flash('Логин или пароль неправильный!', category='danger')
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/users')
def users():

    return render_template('users.html')