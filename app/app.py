from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from app.models.db import init_db

# Unified import from routes
# Import blueprints
from app.routes.auth_routes import auth_bp
from app.routes.candidate_routes import candidate_bp
from app.routes.employer_routes import employer_bp
from app.routes.admin_routes import admin_bp
from app.routes.home_routes import home_bp
from app.routes import auth_bp, candidate_bp, employer_bp, admin_bp, home_bp  # ✅ all imported from __init__.py
from app.routes.candidate_routes import candidate_bp


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
