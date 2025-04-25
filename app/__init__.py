from flask import Flask
from flask_jwt_extended import JWTManager
import mysql.connector
from app.models.db import init_db
from app.routes.auth_routes import auth_bp
from app.routes.candidate_routes import candidate_bp
from app.routes.employer_routes import employer_bp
from app.routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # replace with env var in prod
    app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''  # Set your MySQL password
    app.config['MYSQL_DATABASE'] = 'flask_job_recommendation'

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize MySQL connection
    init_db(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    return app
