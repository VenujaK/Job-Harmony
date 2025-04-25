from app.models.db import get_db


# ----------------------------
# Post a New Job
# ----------------------------
def create_job(employer_id, title, description, required_skills, required_education, salary_min, salary_max, job_type, location):
    db, cursor = get_db()
    cursor.execute("""
        INSERT INTO jobs (employer_id, title, description, required_skills, required_education,
                          salary_min, salary_max, job_type, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (employer_id, title, description, required_skills, required_education, salary_min, salary_max, job_type, location))
    db.commit()
    return cursor.lastrowid


# ----------------------------
# Get Jobs by Employer
# ----------------------------
def get_jobs_by_employer(employer_id):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs WHERE employer_id = %s ORDER BY posted_at DESC", (employer_id,))
    return cursor.fetchall()


# ----------------------------
# Get Job by ID
# ----------------------------
def get_job_by_id(job_id):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    return cursor.fetchone()


# ----------------------------
# Delete Job by ID
# ----------------------------
def delete_job(job_id):
    db, cursor = get_db()
    cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
    db.commit()
