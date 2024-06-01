import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

ADMIN_ROLE_ID = 1
QL_PASSWORD = os.environ.get('MSSQL_PASSWORD')

MYSQL_USER = 'std_2443_lab4'
MYSQL_PASSWORD = '9257102455'
MYSQL_HOST = 'std-mysql.ist.mospolytech.ru'
MYSQL_DATABASE = 'std_2443_lab4'