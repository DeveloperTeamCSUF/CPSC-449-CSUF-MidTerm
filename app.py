from flask import Flask, request, jsonify
from config import init_db, mysql
from models import add_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
jwt = JWTManager(app)

# Initialize the database
init_db(app)

@app.route('/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)




@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        # Open a cursor to perform database operations
        cursor = mysql.connection.cursor()
        # Execute a simple query
        cursor.execute("SHOW TABLES;")
        # Fetch the results
        tables = cursor.fetchall()
        # Close the cursor
        cursor.close()
        return jsonify({"status": "success", "tables": tables}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500






# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # Validate the role - only "admin" or "user" allowed
    if role not in ["admin", "user"]:
        return jsonify({"message": "Invalid role. Only 'admin' or 'user' are allowed."}), 400

    try:
        # Register the new user with the provided role
        add_user(username, password, role)
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to register user'}), 500
    

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    # First, get the user
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()

    # Verify password using check_password_hash
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message="Invalid credentials"), 401

    
@app.route('/movies', methods=['GET'])
@jwt_required()
def get_all_movies():
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT id, title, director, release_year FROM movies"
        cursor.execute(query)
        movies = cursor.fetchall()
        cursor.close() 

        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve movies", "error": str(e)}), 500

@app.route('/add_movie', methods=['POST'])
@jwt_required()
def add_movie():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO movies (title, director, release_year) VALUES (%s, %s, %s)"
        cursor.execute(query, (data['title'], data['director'], data['release_year']))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Movie added successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add movie", "error": str(e)}), 500

@app.route('/submit_rating', methods=['POST'])
@jwt_required()
def submit_rating():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    try:
        cursor = mysql.connection.cursor()
        # Get user_id
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        query = "INSERT INTO ratings (user_id, movie_id, rating, username) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user['id'], data['movie_id'], data['rating'], current_user))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Rating submitted successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to submit rating", "error": str(e)}), 500

@app.route('/ratings', methods=['GET'])
@jwt_required()
def get_all_ratings():
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT 
                r.id AS rating_id,
                r.username,
                r.rating,
                m.title AS movie_title,
                m.director,
                m.release_year
            FROM 
                ratings r
            JOIN 
                movies m ON r.movie_id = m.id
        """
        cursor.execute(query)
        ratings = cursor.fetchall()
        cursor.close()

        if not ratings:
            return jsonify({"message": "No ratings found"}), 404

        return jsonify(ratings), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve ratings", "error": str(e)}), 500


@app.route('/movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie_details(movie_id):
    current_user = get_jwt_identity()

    try:
        # Fetch movie details from the 'movies' table
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
        movie = cursor.fetchone()

        if not movie:
            return jsonify({"message": "Movie not found"}), 404

        # Fetch all ratings for the given movie from the 'ratings' table
        cursor.execute("SELECT username, rating FROM ratings WHERE movie_id = %s", (movie_id,))
        ratings = cursor.fetchall()

        # Combine movie details with ratings
        movie_details = {
            "id": movie['id'],
            "title": movie['title'],
            "description": movie['description'],
            "ratings": ratings
        }

        return jsonify(movie_details), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Failed to fetch movie details"}), 500


@app.route('/ratings/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_rating(movie_id):
    current_user = get_jwt_identity()

    # Get the new rating from the request body
    data = request.get_json()
    new_rating = data.get('rating')

    if new_rating is None:
        return jsonify({"message": "New rating is required"}), 400

    try:
        # Check if the rating exists for the current user and movie
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM ratings WHERE username = %s AND movie_id = %s"
        cursor.execute(query, (current_user, movie_id))
        rating = cursor.fetchone()

        if not rating:
            return jsonify({"message": "No existing rating found for this movie"}), 404

        # Update the user's rating for the movie
        update_query = "UPDATE ratings SET rating = %s WHERE username = %s AND movie_id = %s"
        cursor.execute(update_query, (new_rating, current_user, movie_id))
        mysql.connection.commit()

        return jsonify({"message": "Rating updated successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Failed to update rating"}), 500
    
@app.route('/ratings/<int:rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    current_user = get_jwt_identity()  # Get the username from JWT token

    try:
        # Retrieve the user's role from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT role FROM users WHERE username = %s", (current_user,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        # If the user is an admin, they can delete any rating
        if user['role'] == 'admin':
            delete_query = "DELETE FROM ratings WHERE id = %s"
            cursor.execute(delete_query, (rating_id,))
            mysql.connection.commit()
            return jsonify({"message": "Rating deleted successfully (Admin)!"}), 200

        # If the user is not an admin, check if the rating belongs to them
        query = "SELECT * FROM ratings WHERE id = %s AND username = %s"
        cursor.execute(query, (rating_id, current_user))
        rating = cursor.fetchone()

        if not rating:
            return jsonify({"message": "No rating found or unauthorized to delete"}), 404

        # If the rating belongs to the user, delete it
        delete_query = "DELETE FROM ratings WHERE id = %s"
        cursor.execute(delete_query, (rating_id,))
        mysql.connection.commit()
        return jsonify({"message": "Rating deleted successfully (User)!"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Failed to delete rating"}), 500

# Set of allowed extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File upload endpoint
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({
            "message": "File type not allowed",
            "allowed_types": list(ALLOWED_EXTENSIONS)
        }), 400
    
    try:
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        # Add username prefix to avoid filename conflicts
        safe_filename = f"{current_user}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        # Save file info to database
        cursor = mysql.connection.cursor()
        query = "INSERT INTO files (username, filename, filepath) VALUES (%s, %s, %s)"
        cursor.execute(query, (current_user, filename, file_path))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename
        }), 201
        
    except Exception as e:
        return jsonify({
            "message": "Failed to upload file",
            "error": str(e)
        }), 500

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)
