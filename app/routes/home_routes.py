from flask import Blueprint, render_template
from app.models.db import get_db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cursor.fetchall()
    return render_template("home.html", jobs=jobs)


@home_bp.route('/jobs')
def jobs():
    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cursor.fetchall()
    return render_template('job_listing.html', jobs=jobs)
