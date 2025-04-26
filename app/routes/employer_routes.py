from flask import Blueprint, request, jsonify,render_template, redirect, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db
from app.utils.recommender import recommend_candidates_for_job

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

@employer_bp.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user or user.get('type', '').lower() != 'employer':
        flash('You must be logged in as an employer to view the dashboard.', 'danger')
        return redirect('/auth/login')

    return render_template('dashboard_employer.html', user=user)




# ----------------------------
# Post a Job
# ----------------------------
@employer_bp.route('/post-job', methods=['GET', 'POST'])
def post_job():
    user = session.get('user')
    if not user or user.get('type', '').lower() != 'employer':
        flash('You must be logged in as an employer to post jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        required_education = request.form.get('required_education')
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        job_type = request.form.get('job_type')
        location = request.form.get('location')

        cursor.execute("""
            INSERT INTO jobs (employer_id, title, description, required_skills, required_education,
                              salary_min, salary_max, job_type, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user['id'], title, description, required_skills, required_education,
              salary_min, salary_max, job_type, location))
        db.commit()

        flash('Job posted successfully!', 'success')
        return redirect('/employer/post-job')

    return render_template('post_job.html', user=user)

# ----------------------------
# View My Jobs
# ----------------------------
@employer_bp.route('/my-jobs')
def my_jobs():
    user = session.get('user')
    if not user or user.get('type', '').lower() != 'employer':
        flash('You must be logged in as an employer to view your posted jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs WHERE employer_id = %s ORDER BY posted_at DESC", (user['id'],))
    jobs = cursor.fetchall()

    return render_template('employer_my_jobs.html', jobs=jobs, user=user)


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


@employer_bp.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    user = session.get('user')
    if not user or user.get('type', '').lower() != 'employer':
        flash('You must be logged in as an employer to edit jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    # First fetch the job
    cursor.execute("SELECT * FROM jobs WHERE id = %s AND employer_id = %s", (job_id, user['id']))
    job = cursor.fetchone()

    if not job:
        flash('Job not found or you do not have permission to edit this job.', 'danger')
        return redirect('/employer/my-jobs')

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        required_education = request.form.get('required_education')
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        job_type = request.form.get('job_type')
        location = request.form.get('location')

        cursor.execute("""
            UPDATE jobs
            SET title = %s, description = %s, required_skills = %s, required_education = %s,
                salary_min = %s, salary_max = %s, job_type = %s, location = %s
            WHERE id = %s AND employer_id = %s
        """, (title, description, required_skills, required_education,
              salary_min, salary_max, job_type, location, job_id, user['id']))
        db.commit()

        flash('Job updated successfully!', 'success')
        return redirect('/employer/my-jobs')

    return render_template('edit_job.html', job=job, user=user)



@employer_bp.route('/match-candidates/<int:job_id>')
def match_candidates(job_id):
    user = session.get('user')
    if not user or user.get('type') != 'employer':
        flash('You must be logged in as an employer.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    # ✅ Step 1: Fetch job (must call fetchone before next execute)
    cursor.execute("SELECT * FROM jobs WHERE id = %s AND employer_id = %s", (job_id, user['id']))
    job = cursor.fetchone()

    if not job:
        flash('Job not found or not accessible.', 'danger')
        return redirect('/employer/my-jobs')

    # ✅ Step 2: Fetch matching candidates + email from users table
    cursor.execute("""
        SELECT cp.*, u.email
        FROM candidate_profiles cp
        JOIN users u ON cp.user_id = u.id
    """)
    candidates = cursor.fetchall()

    return render_template('match_candidates.html', job=job, candidates=candidates)



@employer_bp.route('/job-applications/<int:job_id>')
def job_applications(job_id):
    user = session.get('user')
    if not user or user.get('type') != 'employer':
        flash('You must be logged in as an employer.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    # Ensure job belongs to employer
    cursor.execute("SELECT * FROM jobs WHERE id = %s AND employer_id = %s", (job_id, user['id']))
    job = cursor.fetchone()
    if not job:
        flash('Job not found or access denied.', 'danger')
        return redirect('/employer/my-jobs')

    # Fetch applications and candidate info
    cursor.execute("""
    SELECT a.status, a.applied_at, cp.*, u.email
    FROM applications a
    JOIN candidate_profiles cp ON a.candidate_id = cp.user_id
    JOIN users u ON cp.user_id = u.id
    WHERE a.job_id = %s
    ORDER BY a.applied_at DESC
""", (job_id,))


    applications = cursor.fetchall()

    return render_template('job_applications.html', job=job, applications=applications)
