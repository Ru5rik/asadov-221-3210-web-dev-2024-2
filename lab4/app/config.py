import os

SECRET_KEY = os.environ.get('SECRET_KEY')

MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_HOST = os.environ.get('MYSQL_HOST')