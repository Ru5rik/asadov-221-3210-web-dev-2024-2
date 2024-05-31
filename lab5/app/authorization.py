from flask import render_template, request, redirect, flash, url_for, Blueprint, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from app import db_connector
from users_policy import UsersPolicy
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

class User(UserMixin):
    def __init__(self, user_id, login, role_id):
        self.id = user_id
        self.login = login
        self.role_id = role_id
    
    def is_admin(self):
        return self.role_id == current_app.config['ADMIN_ROLE_ID']

    def can(self, action, user=None):
        user_policy = UsersPolicy(user)
        method = getattr(user_policy, action, lambda: False)
        return method()
            
def check_rights(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = None
            user_id = kwargs.get('user_id')
            if user_id:
                user = get_user(user_id)

            if not current_user.can(action, user):
                flash("У вас недостаточно прав для доступа к этой странице", "warning")
                return redirect(url_for("users.index"))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Для продолжения необходимо пройти авторизацию"
    login_manager.login_message_category = "warning"
    login_manager.user_loader(load_user)

def get_user(id):
    query = ("SELECT Users.ID as id, Users.Login as login, Users.LastName as last_name, "
             "Users.FirstName as first_name, Users.MiddleName as middle_name, RoleID as role_id, Roles.Name as role_name "
             "FROM Users LEFT JOIN Roles ON Users.RoleID = Roles.ID WHERE Users.ID = %s")
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (id, ))
        return cursor.fetchone()

def load_user(user_id):
    user = get_user(user_id)
    if user:
        return User(user_id, user.login, user.role_id)
    return None

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth.html")
    
    login = request.form.get("login", "")
    password = request.form.get("pass", "")
    remember = request.form.get("remember") == "on"

    query = 'SELECT ID as id, Login as login, RoleID as role_id FROM Users WHERE login=%s AND PassHash=SHA2(%s, 256)'
    print(query)

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (login, password))
        print(cursor.statement)
        user = cursor.fetchone()

    if user:
        login_user(User(user.id, user.login, user.role_id), remember=remember)
        flash("Успешная авторизация", category="success")
        target_page = request.args.get("next", url_for("index"))
        return redirect(target_page)

    flash("Введены некорректные учётные данные пользователя", category="danger")    

    return render_template("auth.html")

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))