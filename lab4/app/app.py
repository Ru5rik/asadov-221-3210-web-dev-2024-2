import re
from flask import Flask, render_template, make_response, url_for, redirect, request, session, flash
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required, current_user
from mysqldb import DBConnector
from mysql.connector.errors import DatabaseError


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


CREATE_USER_FIELDS = ['login', 'password', 'last_name',
                      'first_name', 'middle_name', 'role_id']
EDIT_USER_FIELDS = ['last_name', 'first_name', 'middle_name', 'role_id']
EDIT_PASS_FIELDS = ['password', 'spassword']

def get_user(id):
    query = ("SELECT Users.ID as id, Users.Login as login, Users.LastName as last_name, "
             "Users.FirstName as first_name, Users.MiddleName as middle_name, RoleID as role_id, Roles.Name as role_name "
             "FROM Users LEFT JOIN Roles ON Users.RoleID = Roles.ID WHERE Users.ID = %s")
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (id, ))
        return cursor.fetchone()


def get_roles():
    query = "SELECT ID as id, Name as name FROM Roles"

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
    return roles


@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id)
    if user:
        return User(user_id, user.login)
    return None


@app.route('/')
def index():
    query = ("SELECT Users.ID as id, Users.Login as login, Users.LastName as last_name, "
             "Users.FirstName as first_name, Users.MiddleName as middle_name, Roles.Name as role_name "
             "FROM Users LEFT JOIN Roles ON Users.RoleID = Roles.ID")

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        data = cursor.fetchall()

    return render_template("index.html", users=data)


def get_form_data(required_fields):
    user = {}
    for field in required_fields:
        user[field] = request.form.get(field) or None
    return user


def validate_form(user, fields):
    regex = {'login': r'^[\da-zA-Z]{5,}$',
             'password': r'^(?=.*\d)(?=.*[A-ZА-Я])(?=.*[a-zа-я])(?=.*[\~\!\?\@\#\$\%\^'\
             r'\&\*\_\-\+\(\)\[\]\{\}\>\<\/\\\|\"\'\.\,\:\;]*)([^\s]){8,128}$',
             'spassword': r'^(?=.*\d)(?=.*[A-ZА-Я])(?=.*[a-zа-я])(?=.*[\~\!\?\@\#\$\%\^'\
             r'\&\*\_\-\+\(\)\[\]\{\}\>\<\/\\\|\"\'\.\,\:\;]*)([^\s]){8,128}$',
             'last_name': r'^[a-zA-Zа-яА-Я]+$',
             'first_name': r'^[a-zA-Zа-яА-Я]+$'}
    errors = {}
    is_error = False
    for field in fields:
        errors[field] = True
        if user.get(field):
            errors[field] = re.search(regex[field], user[field]) == None
            is_error = is_error or errors[field]
    return errors, is_error

@app.route('/<int:user_id>/info')
def user_info(user_id):
    user = get_user(user_id)
    return render_template("user_info.html", user=user)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def create_user():
    user = {}
    errors = {}
    roles = get_roles()
    if request.method == 'POST':
        user = get_form_data(CREATE_USER_FIELDS)
        errors, is_error = validate_form(user, CREATE_USER_FIELDS[:4])
        if is_error:
            flash(f'Ошибка создания пользователя!', category="danger")
            return render_template("user_form.html", user=user, roles=roles, errors=errors)

        query = ("INSERT INTO Users "
                 "(Login, PassHash, LastName, FirstName, MiddleName, RoleID) "
                 "VALUES (%(login)s, SHA2(%(password)s, 256), "
                 "%(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s)")
        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                db_connector.connect().commit()
            return redirect(url_for('index'))
        except DatabaseError as error:
            flash(f'Ошибка создания пользователя! {error}', category="danger")
            db_connector.connect().rollback()

    return render_template("user_form.html", user=user, roles=roles, errors=errors)


@app.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    roles = get_roles()
    user = get_user(user_id)
    errors = {}
    if request.method == "POST":
        user = get_form_data(EDIT_USER_FIELDS)
        errors, is_error = validate_form(user, EDIT_USER_FIELDS[:2])
        if is_error:
            flash(f'Ошибка изменения пользователя!', category="danger")
            return render_template("edit_user.html", user=user, roles=roles, errors=errors)

        user['user_id'] = user_id
        query = ("UPDATE Users "
                 "SET LastName=%(last_name)s, FirstName=%(first_name)s, "
                 "MiddleName=%(middle_name)s, RoleID=%(role_id)s "
                 "WHERE ID=%(user_id)s")

        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                db_connector.connect().commit()

            flash("Запись пользователя успешно обновлена", category="success")
            return redirect(url_for('index'))
        except DatabaseError as error:
            flash(
                f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()
    return render_template("edit_user.html", user=user, roles=roles, errors=errors)

@app.route('/editpass', methods=['GET', 'POST'])
@login_required
def edit_pass_user():
    user = get_user(current_user.id)
    errors = {}
    if request.method == "POST":
        user = get_form_data(EDIT_PASS_FIELDS)
        errors, is_error = validate_form(user, EDIT_PASS_FIELDS)

        if is_error:
            flash(f'Ошибка изменения пользователя!', category="danger")
            return render_template("edit_pass_user.html", user=user, errors=errors)

        if user['password'] != user['spassword']:
            flash(f'Пароли должны совпадать!', category="danger")
            return render_template("edit_pass_user.html", user=user, errors=errors)

        user['user_id'] = current_user.id
        query = "UPDATE Users SET PassHash=SHA2(%(password)s, 256) WHERE ID=%(user_id)s"

        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                db_connector.connect().commit()

            flash("Запись пользователя успешно обновлена", category="success")
            return redirect(url_for('index'))
        except DatabaseError as error:
            flash(
                f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()
    return render_template("edit_pass_user.html", user=user, errors=errors)


@app.route('/<int:user_id>/delete', methods=["POST"])
@login_required
def delete_user(user_id):
    query = "DELETE FROM Users WHERE ID=%s"
    try:
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (user_id, ))
            db_connector.connect().commit()

        flash("Запись пользователя успешно удалена", category="success")
    except DatabaseError as error:
        flash(f'Ошибка удаления пользователя! {error}', category="danger")
        db_connector.connect().rollback()

    return redirect(url_for('index'))


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
