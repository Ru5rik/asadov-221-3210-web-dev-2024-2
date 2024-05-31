import re
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from mysql.connector.errors import DatabaseError
from app import db_connector
from authorization import check_rights

bp = Blueprint('users', __name__, url_prefix='/users')

CREATE_USER_FIELDS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
EDIT_USER_FIELDS = ['last_name', 'first_name', 'middle_name', 'role_id']
EDIT_PASS_FIELDS = ['oldpassword','password', 'spassword']

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

@bp.route('/')
def index():
    query = ("SELECT Users.ID as id, Users.Login as login, Users.LastName as last_name, "
             "Users.FirstName as first_name, Users.MiddleName as middle_name, Roles.Name as role_name "
             "FROM Users LEFT JOIN Roles ON Users.RoleID = Roles.ID")

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    current = 0
    is_admin = False
    if current_user.is_authenticated:
        current = int(current_user.id)
        is_admin = current_user.is_admin()
    return render_template("users.html", users=data, current_id=current, is_admin=is_admin)

def get_form_data(required_fields):
    user = {}

    for field in required_fields:
        user[field] = request.form.get(field) or None

    return user

@bp.route('/<int:user_id>/info')
def info(user_id):
    user = get_user(user_id)
    return render_template("user_info.html", user=user)

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights('edit')
def edit(user_id):
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
            return redirect(url_for('users.index'))
        except DatabaseError as error:
            flash(
                f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()
    return render_template("edit_user.html", user=user, roles=roles, errors=errors, is_admin=current_user.is_admin())

@bp.route('/<int:user_id>/delete', methods=["POST"])
@login_required
@check_rights('delete')
def delete(user_id):
    query = "DELETE FROM Users WHERE ID=%s"
    try:
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (user_id, ))
            db_connector.connect().commit()

        flash("Запись пользователя успешно удалена", category="success")
    except DatabaseError as error:
        flash(f'Ошибка удаления пользователя! {error}', category="danger")
        db_connector.connect().rollback()

    return redirect(url_for('users.index'))

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@check_rights('create')
def create():
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
            return redirect(url_for('users.index'))
        except DatabaseError as error:
            flash(f'Ошибка создания пользователя! {error}', category="danger")
            db_connector.connect().rollback()

    return render_template("user_form.html", user=user, roles=roles, errors=errors)

@bp.route('/editpass', methods=['GET', 'POST'])
@login_required
def edit_pass_user():
    errors = {}
    if request.method == "POST":
        form_data = get_form_data(EDIT_PASS_FIELDS)
        errors, is_error = validate_form(form_data, EDIT_PASS_FIELDS[1:])
        form_data['user_id'] = current_user.id

        query = ("SELECT ID as id FROM Users WHERE ID=%(user_id)s AND PassHash = SHA2(%(oldpassword)s, 256)")
        
        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, form_data)
                if cursor.fetchone() is None:
                    errors['oldpassword'] = True
                    is_error = True

            if is_error:
                flash(f'Ошибка изменения пароля!', category="danger")
                return render_template("edit_pass_user.html", errors=errors)

            if form_data['password'] != form_data['spassword']:
                flash(f'Пароли должны совпадать!', category="danger")
                return render_template("edit_pass_user.html", errors=errors)

            query = "UPDATE Users SET PassHash=SHA2(%(password)s, 256) WHERE ID=%(user_id)s"

            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, form_data)
                db_connector.connect().commit()

            flash("Запись пользователя успешно обновлена", category="success")
            return redirect(url_for('users.index'))
        except DatabaseError as error:
            flash(
                f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()
    return render_template("edit_pass_user.html", errors=errors)