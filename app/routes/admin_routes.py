from flask import Blueprint, request, jsonify, render_template, session, redirect, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ----------------------------
# Check Admin Access
# ----------------------------
def is_admin():
    identity = get_jwt_identity()
    return identity['type'] == 'admin'

@admin_bp.route('/dashboard')
def admin_dashboard():
    user = session.get('user')
    if not user or user.get('type') != 'admin':
        flash('You must be logged in as an admin.', 'danger')
        return redirect('/auth/login')

    return render_template('dashboard_admin.html', user=user)


# ----------------------------
# View All Users
# ----------------------------
@admin_bp.route('/users')
def view_all_users():
    user = session.get('user')
    if not user or user.get('type') != 'admin':
        flash('You must be logged in as an admin to view this page.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()
    cursor.execute("SELECT id, name, email, user_type FROM users ORDER BY id DESC")


    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    users = [dict(zip(colnames, row)) for row in rows]

    return render_template('admin_users.html', users=users)  # ✅ aligned correctly



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
@admin_bp.route('/jobs')
def view_all_jobs():
    db, cursor = get_db()

    cursor.execute("""
        SELECT j.id, j.title, j.location, j.job_type, j.posted_at, u.name AS employer_name, u.email AS employer_email
        FROM jobs j
        JOIN users u ON j.employer_id = u.id
        ORDER BY j.posted_at DESC
    """)
    
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    jobs = [dict(zip(columns, row)) for row in rows]  # ✅ MUST BE HERE

    return render_template('admin_jobs.html', jobs=jobs)






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


