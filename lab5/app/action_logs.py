import math
import io
from flask import Blueprint,  render_template, request, send_file
from flask_login import login_required, current_user
from app import db_connector
from mysql.connector.errors import DatabaseError


logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

PAGE_COUNT = 10

def generate_file(fields, records):
    result = ','.join(fields) + '\n'
    for record in records:
        line = ','.join([str(getattr(record, field, '') or '')
                        for field in fields]) + '\n'
        result += line
    return io.BytesIO(result.encode())

@logs_bp.route('/')
@login_required
def index():
    logs = []
    page_number = request.args.get('page_number', 1, type=int)
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            flt = '' if current_user.is_admin() else f'Where u.ID = {current_user.id}'
            query = ("SELECT l.id, u.Login as login, l.path, created_at "
                     "FROM visit_logs as l LEFT JOIN Users as u ON l.user_id = u.ID "
                     f"{flt} "
                     "ORDER BY created_at desc "
                     f"LIMIT {PAGE_COUNT} OFFSET {PAGE_COUNT*(page_number - 1)} ")
            cursor.execute(query)
            logs = cursor.fetchall()

            query = ("SELECT COUNT(*) as count FROM visit_logs")
            cursor.execute(query)
            total_count = cursor.fetchone().count
            all_page = math.ceil(total_count / PAGE_COUNT)
            start_page = max(page_number - 3, 1)
            end_page = min(page_number + 3, all_page)
            return render_template("action_logs.html", logs=logs, start_page=start_page, end_page=end_page, page_number=page_number)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")

    return render_template("action_logs.html", logs={}, start_page=1, end_page=1, page_number=1)

@logs_bp.route('/users_stat')
@login_required
def users_stat():
    logs = []    
    page_number = request.args.get('page_number', 1, type=int)
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            flt = '' if current_user.is_admin() else f'Where visit_logs.user_id = {current_user.id}'
            query = ("SELECT u.Login as login, COUNT(*) as visit_count "
            "FROM visit_logs LEFT JOIN Users as u on visit_logs.user_id = u.ID "
            f"{flt} "
            "GROUP BY u.ID ORDER BY visit_count desc "
            f"LIMIT {PAGE_COUNT} OFFSET {PAGE_COUNT*(page_number - 1)} ")
            cursor.execute(query)
            logs = cursor.fetchall()

            if request.args.get('download'):
                file = generate_file(['login', 'visit_count'], logs)
                return send_file(file, mimetype='text/csv', as_attachment=True, download_name='logs.csv')
            
            query = (f"SELECT user_id FROM visit_logs {flt} GROUP BY user_id")
            cursor.execute(query)
            total_count = len(cursor.fetchall())
            all_page = math.ceil(total_count / PAGE_COUNT)
            start_page = max(page_number - 3, 1)
            end_page = min(page_number + 3, all_page)
            return render_template("users_stat.html", logs=logs, start_page=start_page, end_page=end_page, page_number=page_number)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")  
    return render_template("users_stat.html", start_page=1, end_page=1, page_number=1) 

@logs_bp.route('/pages_stat')
@login_required
def pages_stat():
    logs = []    
    page_number = request.args.get('page_number', 1, type=int)
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            flt = '' if current_user.is_admin() else f'Where visit_logs.user_id = {current_user.id}'
            query = ("SELECT path, COUNT(*) as visit_count FROM visit_logs "
            f"{flt} "
            "GROUP BY path ORDER BY visit_count desc "
            f"LIMIT {PAGE_COUNT} OFFSET {PAGE_COUNT*(page_number - 1)} ")
            cursor.execute(query)
            logs = cursor.fetchall()

            if request.args.get('download'):
                file = generate_file(['path', 'visit_count'], logs)
                return send_file(file, mimetype='text/csv', as_attachment=True, download_name='logs.csv')

            query = (f"SELECT path FROM visit_logs {flt} GROUP BY path")
            cursor.execute(query)
            total_count = len(cursor.fetchall())
            all_page = math.ceil(total_count / PAGE_COUNT)
            start_page = max(page_number - 3, 1)
            end_page = min(page_number + 3, all_page)
            print(total_count, all_page, start_page, end_page)
            return render_template("pages_stat.html", logs=logs, start_page=start_page, end_page=end_page, page_number=page_number)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")  
    return render_template("pages_stat.html", start_page=1, end_page=1, page_number=1) 