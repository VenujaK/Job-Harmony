from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db
from app.utils.recommender import recommend_jobs_for_candidate

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')


# ----------------------------
# Update Candidate Profile
# ----------------------------
@candidate_bp.route('/profile', methods=['POST'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    if identity['type'] != 'candidate':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    user_id = identity['id']
    experience = data.get('experience')
    education = data.get('education')
    skills = data.get('skills')
    salary = data.get('salary')

    db, cursor = get_db()
    cursor.execute("SELECT * FROM candidate_profiles WHERE user_id = %s", (user_id,))
    if cursor.fetchone():
        cursor.execute("""
            UPDATE candidate_profiles
            SET years_experience=%s, education_level=%s, technical_skills=%s, salary_expectations=%s
            WHERE user_id=%s
        """, (experience, education, skills, salary, user_id))
    else:
        cursor.execute("""
            INSERT INTO candidate_profiles (user_id, years_experience, education_level, technical_skills, salary_expectations)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, experience, education, skills, salary))
    db.commit()

    return jsonify({'message': 'Profile updated'}), 200


# ----------------------------
# View Recommended Jobs
# ----------------------------
@candidate_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def job_recommendations():
    identity = get_jwt_identity()
    if identity['type'] != 'candidate':
        return jsonify({'error': 'Unauthorized'}), 403

    recommended = recommend_jobs_for_candidate(identity['id'])  # Uses your trained model
    return jsonify(recommended)


# ----------------------------
# Track Applied Jobs
# ----------------------------
@candidate_bp.route('/my-applications', methods=['GET'])
@jwt_required()
def my_applications():
    identity = get_jwt_identity()
    user_id = identity['id']

    db, cursor = get_db()
    cursor.execute("""
        SELECT j.title, j.company, j.location, a.status, a.applied_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.candidate_id = %s
        ORDER BY a.applied_at DESC
    """, (user_id,))
    applications = cursor.fetchall()

    return jsonify(applications)


# ----------------------------
# Save Job for Later
# ----------------------------
@candidate_bp.route('/save-job', methods=['POST'])
@jwt_required()
def save_job():
    identity = get_jwt_identity()
    user_id = identity['id']
    job_id = request.json.get('job_id')

    db, cursor = get_db()
    cursor.execute("SELECT * FROM saved_jobs WHERE candidate_id = %s AND job_id = %s", (user_id, job_id))
    if cursor.fetchone():
        return jsonify({'message': 'Job already saved'}), 409

    cursor.execute("INSERT INTO saved_jobs (candidate_id, job_id) VALUES (%s, %s)", (user_id, job_id))
    db.commit()
    return jsonify({'message': 'Job saved'}), 200


# ----------------------------
# View Saved Jobs
# ----------------------------
@candidate_bp.route('/saved-jobs', methods=['GET'])
@jwt_required()
def view_saved_jobs():
    identity = get_jwt_identity()
    user_id = identity['id']

    db, cursor = get_db()
    cursor.execute("""
        SELECT j.id, j.title, j.company, j.location, j.salary_min, j.salary_max
        FROM saved_jobs s
        JOIN jobs j ON s.job_id = j.id
        WHERE s.candidate_id = %s
    """, (user_id,))
    saved = cursor.fetchall()

    return jsonify(saved)
