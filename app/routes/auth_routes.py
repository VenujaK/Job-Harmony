from app.models.user_model import create_user, get_user_by_email
from flask import Blueprint, render_template, request, redirect, flash, session, jsonify
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
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not name or not email or not password or not user_type:
            flash('All fields are required.', 'danger')
            return redirect('/auth/register')

        if get_user_by_email(email):
            flash('Email already registered.', 'warning')
            return redirect('/auth/register')

        hashed_pw = generate_password_hash(password)
        create_user(name, email, hashed_pw, user_type)

        flash('Account created! You can now log in.', 'success')
        return redirect('/auth/login')

    return render_template('register.html')


# ----------------------------
# User Login
# ----------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect('/auth/login')

        user = get_user_by_email(email)
        if not user or not check_password_hash(user['password'], password):
            flash('Invalid credentials.', 'danger')
            return redirect('/auth/login')

        # Set user in session
        session['user'] = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'type': user['user_type']
        }

        flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect('/')

    return render_template('login.html')


# ----------------------------
# Protected Test Route
# ----------------------------
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def profile():
    identity = get_jwt_identity()
    return jsonify({'logged_in_as': identity}), 200

@auth_bp.route('/logout')
def logout():
    session.clear()  # ✅ Clears all session data
    flash('You have been logged out.', 'info')
    return redirect('/')