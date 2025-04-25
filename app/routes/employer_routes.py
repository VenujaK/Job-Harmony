from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db
from app.utils.recommender import recommend_candidates_for_job

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')


# ----------------------------
# Post a Job
# ----------------------------
@employer_bp.route('/post-job', methods=['POST'])
@jwt_required()
def post_job():
    identity = get_jwt_identity()
    if identity['type'] != 'employer':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    employer_id = identity['id']

    title = data.get('title')
    description = data.get('description')
    required_skills = data.get('required_skills')
    required_education = data.get('required_education')
    salary_min = data.get('salary_min')
    salary_max = data.get('salary_max')
    job_type = data.get('job_type')
    location = data.get('location')

    if not all([title, required_skills, required_education, salary_min, salary_max, job_type, location]):
        return jsonify({'error': 'All fields are required'}), 400

    db, cursor = get_db()
    cursor.execute("""
        INSERT INTO jobs (employer_id, title, description, required_skills, required_education,
        salary_min, salary_max, job_type, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (employer_id, title, description, required_skills, required_education, salary_min, salary_max, job_type, location))
    db.commit()

    return jsonify({'message': 'Job posted successfully'}), 201


# ----------------------------
# View My Jobs
# ----------------------------
@employer_bp.route('/my-jobs', methods=['GET'])
@jwt_required()
def my_jobs():
    identity = get_jwt_identity()
    employer_id = identity['id']

    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs WHERE employer_id = %s ORDER BY posted_at DESC", (employer_id,))
    jobs = cursor.fetchall()

    return jsonify(jobs)


# ----------------------------
# Get Top Candidates for a Job
# ----------------------------
@employer_bp.route('/recommend-candidates/<int:job_id>', methods=['GET'])
@jwt_required()
def recommend_candidates(job_id):
    identity = get_jwt_identity()
    if identity['type'] != 'employer':
        return jsonify({'error': 'Unauthorized'}), 403

    top_candidates = recommend_candidates_for_job(job_id)
    return jsonify(top_candidates)


# ----------------------------
# View Applications to a Job
# ----------------------------
@employer_bp.route('/applications/<int:job_id>', methods=['GET'])
@jwt_required()
def view_applications(job_id):
    identity = get_jwt_identity()
    employer_id = identity['id']

    db, cursor = get_db()
    cursor.execute("""
        SELECT u.name, u.email, a.status, a.applied_at
        FROM applications a
        JOIN users u ON a.candidate_id = u.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.job_id = %s AND j.employer_id = %s
        ORDER BY a.applied_at DESC
    """, (job_id, employer_id))
    applications = cursor.fetchall()

    return jsonify(applications)
