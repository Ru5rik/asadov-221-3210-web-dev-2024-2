import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

ADMIN_ROLE_ID = 1
QL_PASSWORD = os.environ.get('MSSQL_PASSWORD')

