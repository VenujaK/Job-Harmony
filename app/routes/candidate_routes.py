from flask import Blueprint, request, jsonify, render_template, session, redirect, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import get_db
from app.utils.recommender import recommend_jobs_for_candidate

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')


# ----------------------------
# Update Candidate Profile
# ----------------------------
@candidate_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user = session.get('user')
    if not user or user.get('type', '').lower() != 'candidate':
        flash('You must be logged in as a candidate.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()
    user_id = user['id']

    if request.method == 'POST':
        # Get form data
        experience = request.form.get('experience')
        education = request.form.get('education')
        skills = request.form.get('skills')
        salary = request.form.get('salary')

        # Check if profile exists
        cursor.execute("SELECT * FROM candidate_profiles WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE candidate_profiles
                SET years_experience = %s,
                    education_level = %s,
                    technical_skills = %s,
                    salary_expectations = %s
                WHERE user_id = %s
            """, (experience, education, skills, salary, user_id))
        else:
            cursor.execute("""
                INSERT INTO candidate_profiles (user_id, years_experience, education_level, technical_skills, salary_expectations)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, experience, education, skills, salary))
        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect('/candidate/profile')

    return render_template('dashboard_candidate.html', user=user)

# ----------------------------
# View Recommended Jobs
# ----------------------------
@candidate_bp.route('/recommendations')
def recommendations():
    if 'user' not in session or session['user']['type'] != 'candidate':
        flash('Login as a candidate to access recommendations.', 'danger')
        return redirect('/auth/login')

    user_id = session['user']['id']

    # use your recommender function or query your DB directly
    jobs = recommend_jobs_for_candidate(user_id, top_n=5)

    return render_template('recommendations.html', jobs=jobs, user=session['user'])

# ----------------------------
# Track Applied Jobs
# ----------------------------
@candidate_bp.route('/my-applications')
def my_applications():
    user = session.get('user')
    if not user or user.get('type') != 'candidate':
        flash('You must be logged in as a candidate to view your applications.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()
    cursor.execute("""
    SELECT j.title, j.location, j.job_type, j.required_skills,
           j.salary_min, j.salary_max, a.status
    FROM applications a
    JOIN jobs j ON a.job_id = j.id
    WHERE a.candidate_id = %s
    ORDER BY a.applied_at DESC
""", (user['id'],))

    applications = cursor.fetchall()

    return render_template('my_applications.html', applications=applications)



# ----------------------------
# Save Job for Later
# ----------------------------
@candidate_bp.route('/save-job/<int:job_id>', methods=['GET'])
def save_job(job_id):
    user = session.get('user')
    if not user or user.get('type') != 'candidate':
        flash('You must be logged in as a candidate to save jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    # Check if the job is already saved
    cursor.execute("SELECT * FROM saved_jobs WHERE candidate_id = %s AND job_id = %s", (user['id'], job_id))
    if cursor.fetchone():
        flash('Job is already saved.', 'info')
    else:
        cursor.execute("INSERT INTO saved_jobs (candidate_id, job_id) VALUES (%s, %s)", (user['id'], job_id))
        db.commit()
        flash('Job saved successfully!', 'success')

    return redirect('/jobs')



# ----------------------------
# View Saved Jobs
# ----------------------------
@candidate_bp.route('/saved-jobs')
def saved_jobs():
    user = session.get('user')
    if not user or user.get('type') != 'candidate':
        flash('You must be logged in as a candidate to view saved jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()
    cursor.execute("SELECT * FROM saved_jobs WHERE id = %s", (user['id'],))
    jobs = cursor.fetchall()

    return render_template('saved_jobs.html', jobs=jobs)


# ----------------------------
# Apply for Jobs
# ----------------------------
@candidate_bp.route('/apply/<int:job_id>')
def apply_for_job(job_id):
    user = session.get('user')
    if not user or user.get('type') != 'candidate':
        flash('You must be logged in as a candidate to apply for jobs.', 'danger')
        return redirect('/auth/login')

    db, cursor = get_db()

    # Check if the application already exists
    cursor.execute("SELECT * FROM applications WHERE candidate_id = %s AND job_id = %s", (user['id'], job_id))
    if cursor.fetchone():
        flash('You have already applied to this job.', 'info')
        return redirect('/candidate/my-applications')

    # Insert application
    cursor.execute("INSERT INTO applications (candidate_id, job_id) VALUES (%s, %s)", (user['id'], job_id))
    db.commit()

    flash('Application submitted successfully!', 'success')
    return redirect('/candidate/my-applications')

