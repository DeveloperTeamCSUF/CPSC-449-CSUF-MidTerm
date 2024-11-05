from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'movie_user'
    app.config['MYSQL_PASSWORD'] = 'Datta@14'
    app.config['MYSQL_DB'] = 'mydb'  # Corrected key
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)
