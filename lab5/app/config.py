import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

ADMIN_ROLE_ID = 1

# MSSQL_SERVER = 'localhost\sqlexpress'
# # MSSQL_SERVER = '95.165.152.146'
# MSSQL_USER = 'Remote'
# MSSQL_PASSWORD = '12345'
# MSSQL_DATABASE = 'RentCars'
# MSSQL_PORT =  '1433'


# MSSQL_SERVER = os.environ.get('MSSQL_SERVER')
# MSSQL_PORT = os.environ.get('MSSQL_PORT')
# MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE')
# MSSQL_USER = os.environ.get('MSSQL_USER')
# MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD')

MYSQL_USER = 'std_2443_lab4'
MYSQL_PASSWORD = '9257102455'
MYSQL_HOST = 'std-mysql.ist.mospolytech.ru'
MYSQL_DATABASE = 'std_2443_lab4'

# MYSQL_USER = os.environ.get('MYSQL_USER')
# MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
# MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
# MYSQL_HOST = os.environ.get('MYSQL_HOST')