import mysql.connector
from flask import g, current_app

# Initialize MySQL connection and store it in Flask's application context
def init_db(app):
    @app.before_request
    def connect_db():
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DATABASE']
            )
            g.cursor = g.db.cursor(dictionary=True)

    @app.teardown_request
    def close_db(exception=None):
        db = g.pop('db', None)
        cursor = g.pop('cursor', None)
        if cursor:
            cursor.close()
        if db:
            db.close()

# Utility function to get the current connection (to use in other files)
def get_db():
    return g.get('db'), g.get('cursor')
