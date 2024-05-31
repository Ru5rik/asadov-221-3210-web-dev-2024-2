# import mysql.connector
from pyodbc import connect
from flask import g

class DBConnector:
    def __init__(self, app):
        self.app = app
        app.teardown_appcontext(self.close)

    def get_config(self):
        config = {
            'driver': 'SQL Server',
            'server' : self.app.config['MSSQL_SERVER'],
            'port' : self.app.config['MSSQL_PORT'],
            'uid' : self.app.config['MSSQL_USER'],
            'pwd' : self.app.config['MSSQL_PASSWORD'],
            'database' : self.app.config['MSSQL_DATABASE'],
        }

        return config

    def connect(self):
        if 'db' not in g:
            g.db = connect(**self.get_config())
        
        return g.db

    def close(self, e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()