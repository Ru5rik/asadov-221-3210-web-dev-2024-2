import re
from flask import Flask, render_template, make_response, url_for, redirect, request, session, flash
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required, current_user
# from sqldb import DBConnector
from mysqldb import DBConnector
from mysql.connector.errors import DatabaseError


app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db_connector = DBConnector(app)

from authorization import auth_bp, init_login_manager
app.register_blueprint(auth_bp)
init_login_manager(app)

from users import bp as users_bp
app.register_blueprint(users_bp)

from action_logs import logs_bp
app.register_blueprint(logs_bp)

@app.before_request
def user_actions_logger():
    if request.endpoint == 'static' or request.path == '/favicon.ico':
        return
    url = request.path
    user_id = current_user.id if current_user.is_authenticated else None
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            cursor.execute("INSERT INTO visit_logs (user_id, path) VALUES (%s, %s)", (user_id, url))
            db_connection.commit()
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")
        if db_connection:
            db_connection.rollback()

@app.route('/')
def index():
    return render_template("index.html")