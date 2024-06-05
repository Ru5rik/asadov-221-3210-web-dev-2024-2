import os

SECRET_KEY = 'bc4c54c7519d1619a97d210b40fe519556efc7714ea61a1d369758bc9468b771'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2443_lab6:9257102455@std-mysql.ist.mospolytech.ru/std_2443_lab6'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
