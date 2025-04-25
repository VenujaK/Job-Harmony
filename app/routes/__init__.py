# app/routes/__init__.py

from .auth_routes import auth_bp
from .candidate_routes import candidate_bp
from .employer_routes import employer_bp
from .admin_routes import admin_bp
from .home_routes import home_bp  # ✅ ADD THIS

__all__ = ['auth_bp', 'candidate_bp', 'employer_bp', 'admin_bp', 'home_bp']
