from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from app.models.db import init_db

# Unified import from routes
from app.routes import auth_bp, candidate_bp, employer_bp, admin_bp, home_bp  # ✅ all imported from __init__.py

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    JWTManager(app)
    init_db(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    return app
