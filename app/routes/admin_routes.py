from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ----------------------------
# Check Admin Access
# ----------------------------
def is_admin():
    identity = get_jwt_identity()
    return identity['type'] == 'admin'


# ----------------------------
# View All Users
# ----------------------------
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def view_users():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db, cursor = get_db()
    cursor.execute("SELECT id, name, email, user_type, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()

    return jsonify(users)


# ----------------------------
# Delete User by ID
# ----------------------------
@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db, cursor = get_db()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()

    return jsonify({'message': f'User {user_id} deleted successfully.'})


# ----------------------------
# View All Job Postings
# ----------------------------
@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
def view_jobs():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db, cursor = get_db()
    cursor.execute("""
        SELECT j.id, j.title, j.required_skills, j.salary_min, j.salary_max,
               j.location, j.job_type, j.posted_at, u.name AS employer_name
        FROM jobs j
        JOIN users u ON j.employer_id = u.id
        ORDER BY j.posted_at DESC
    """)
    jobs = cursor.fetchall()

    return jsonify(jobs)


# ----------------------------
# Delete Job by ID
# ----------------------------
@admin_bp.route('/delete-job/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db, cursor = get_db()
    cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
    db.commit()

    return jsonify({'message': f'Job {job_id} deleted successfully.'})
