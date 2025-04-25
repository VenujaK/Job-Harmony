from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.db import get_db
from flask import render_template
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def home():
    return render_template('home.html')

# ----------------------------
# User Registration (Signup)
# ----------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type')  # candidate, employer

    if not all([name, email, password, user_type]):
        return jsonify({'error': 'All fields are required.'}), 400

    db, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({'error': 'Email already exists.'}), 409

    hashed_pw = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)",
        (name, email, hashed_pw, user_type)
    )
    db.commit()

    return jsonify({'message': 'User registered successfully.'}), 201


# ----------------------------
# User Login
# ----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': user['id'], 'type': user['user_type']})
    return jsonify({'access_token': access_token, 'user': {'name': user['name'], 'type': user['user_type']}})


# ----------------------------
# Protected Test Route
# ----------------------------
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def profile():
    identity = get_jwt_identity()
    return jsonify({'logged_in_as': identity}), 200
