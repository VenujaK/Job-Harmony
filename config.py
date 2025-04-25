import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"

    # JWT settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret"

    # MySQL (phpMyAdmin - local)
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""  # Update with your MySQL password
    MYSQL_DATABASE = "flask_job_recommendation"

    # Other configs (optional)
    DEBUG = True
