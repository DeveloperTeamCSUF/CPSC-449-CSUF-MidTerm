from config import mysql
from werkzeug.security import generate_password_hash, check_password_hash

# Add a new user
def add_user(username, password, role):
    hashed_password = generate_password_hash(password)
    cursor = mysql.connection.cursor()
    query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, hashed_password, role))
    mysql.connection.commit()
    cursor.close()

def verify_user(username, password):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user['password'], password):
        return user
    return None
