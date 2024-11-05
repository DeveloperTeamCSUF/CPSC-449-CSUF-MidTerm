# Overview
This project is a RESTful API developed with Flask that handles error handling, JWT-based authentication, and secure file handling. It features public and protected routes, with role-based access control for certain functionalities.

### Team Members
- Ali Khaled - alikhaled@csu.fullerton.edu
- Hao Thai - hthai1@csu.fullerton.edu
- Manjari Bhavanasi

### Prerequisites
- Python 3.8+
- MySQL: Ensure MySQL is installed and running.


### Setup Instructions

#### Clone the Repository:
```bash
git clone https://github.com/DeveloperTeamCSUF/CPSC-449-CSUF-MidTerm.git
cd CPSC-449-CSUF-MidTerm-main
```

#### Create a Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies:
```bash
pip install -r requirements.txt
```
```bash
pip install Flask-JWT-Extended
```

### Configure Environment Variables:
Create a `.env` file with your database credentials and secret key:
```plaintext
DB_HOST=<your-database-host>
DB_USER=<your-database-username>
DB_PASSWORD=<your-database-password>
DB_NAME=<your-database-name>
SECRET_KEY=<your-secret-key>
```

### Initialize Database:
Set up the MySQL database using the configuration in `config.py`.

### Start the Application:
```bash
flask run
```
Access the app at http://127.0.0.1:5000.  

<br>
<br>

## API Endpoints and Testing with Postman
<br>
#### Authentication and User Management

**Register User (POST /register)**

Registers a new user with a role (admin or user).

**Request Body:**
```json
{
  "username": "user",
  "password": "password",
  "role": "user"  // or "admin"
}
```
**Response:** Confirmation or error if username exists.

<br>
<br>

**Login (POST /login)**

Authenticates and returns a JWT token.

**Request Body:**
```json
{
  "username": "user",
  "password": "password"
}
```
**Response:**
```json
{
  "access_token": "<jwt_token>"
}
```
<br>
<br>

### Public Routes

**List Routes (GET /routes)**

Lists all available routes and methods.

**Response:** JSON of available routes.

**Test Database Connection (GET /test_db_connection)**

Checks database connectivity.

**Response:** JSON status and tables list if successful.

<br>
<br>

### Movies Management (Protected Routes)
<br>

**Get All Movies (GET /movies)**

Lists all movies in the database.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** List of movies.

<br>
<br>

**Add Movie (POST /add_movie)**

Adds a new movie to the database.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "title": "Movie Title",
  "director": "Director Name",
  "release_year": 2021
}
```
**Response:** Confirmation of addition.

<br>
<br>

### Ratings Management (Protected Routes)
<br>

**Submit Rating (POST /submit_rating)**

Submits a rating for a movie.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "movie_id": 1,
  "rating": 4
}
```
**Response:** Rating submission confirmation.

<br>
<br>

**Get All Ratings (GET /ratings)**

Lists all ratings with related movie details.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** List of all ratings.

<br>
<br>

**Get Movie Details with Ratings (GET /movies/<int:movie_id>)**

Retrieves movie details along with ratings.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** Movie details and ratings.

<br>
<br>

**Update Rating (PUT /ratings/<int:movie_id>)**

Updates the current user’s rating for a movie.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "rating": 5
}
```
**Response:** Confirmation of updated rating.

<br>
<br>

**Delete Rating (DELETE /ratings/<int:rating_id>)**

Deletes a rating. Admin users can delete any rating, while regular users can delete only their own.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** Confirmation of rating deletion.

<br>
<br>

### File Management

**Upload File (POST /upload)**

Allows users to upload files with specific allowed extensions (jpg, jpeg, png, pdf, txt).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
Form Data: file (Choose a file to upload).

**Response:** Confirmation of successful upload.

<br>
<br>

### Error Handling

The API includes error handling for:

- **400:** Bad Request (e.g., missing or invalid data)
- **401:** Unauthorized (e.g., invalid JWT)
- **404:** Not Found (e.g., non-existent resource)
- **500:** Internal Server Error


