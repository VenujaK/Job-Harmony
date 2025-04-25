import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.db import get_db

# Load AI artifacts
model = joblib.load('models/best_model.pkl')
tfidf = joblib.load('models/tfidf_vectorizer.pkl')
le = joblib.load('models/label_encoder.pkl')


# ----------------------------
# Recommend Jobs for Candidate
# ----------------------------
def recommend_jobs_for_candidate(user_id, top_n=3):
    db, cursor = get_db()

    # Get candidate profile
    cursor.execute("SELECT * FROM candidate_profiles WHERE user_id = %s", (user_id,))
    candidate = cursor.fetchone()
    if not candidate:
        return []

    # Load job data
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    if not jobs:
        return []

    # Compute skill similarity
    candidate_vec = tfidf.transform([candidate['technical_skills']])
    job_skills = [job['required_skills'] for job in jobs]
    job_vecs = tfidf.transform(job_skills)
    similarities = cosine_similarity(candidate_vec, job_vecs).flatten()

    # Predict salary
    edu_encoded = le.transform([candidate['education_level']])[0]
    features = {
        'experience': candidate['years_experience'],
        'education_level': edu_encoded,
        'skill_match_score': np.max(similarities)
    }
    predicted_salary = model.predict(np.array([[features['experience'], features['education_level'], features['skill_match_score']]]))[0]
    salary_min = predicted_salary * 0.85
    salary_max = predicted_salary * 1.15

    # Filter and score jobs
    matched = []
    for idx, job in enumerate(jobs):
        mid_salary = (job['salary_min'] + job['salary_max']) / 2
        if salary_min <= mid_salary <= salary_max:
            matched.append({
                'job_id': job['id'],
                'title': job['title'],
                'company': job['description'][:30] + '...',
                'location': job['location'],
                'salary_range': f"${job['salary_min']} - ${job['salary_max']}",
                'match_score': float(similarities[idx])
            })

    matched_sorted = sorted(matched, key=lambda x: (x['match_score']), reverse=True)
    return matched_sorted[:top_n]


# ----------------------------
# Recommend Candidates for Job
# ----------------------------
def recommend_candidates_for_job(job_id, top_n=3):
    db, cursor = get_db()

    # Get job info
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    if not job:
        return []

    # Get all candidate profiles
    cursor.execute("SELECT * FROM candidate_profiles cp JOIN users u ON cp.user_id = u.id")
    candidates = cursor.fetchall()
    if not candidates:
        return []

    # Compute similarity and predict salary fit
    job_vec = tfidf.transform([job['required_skills']])
    candidate_skills = [c['technical_skills'] for c in candidates]
    candidate_vecs = tfidf.transform(candidate_skills)
    similarities = cosine_similarity(job_vec, candidate_vecs).flatten()

    results = []
    for idx, candidate in enumerate(candidates):
        edu_encoded = le.transform([candidate['education_level']])[0]
        features = [
            candidate['years_experience'],
            edu_encoded,
            similarities[idx]
        ]
        predicted_salary = model.predict([features])[0]
        mid_salary = (job['salary_min'] + job['salary_max']) / 2

        if mid_salary * 0.9 <= predicted_salary <= mid_salary * 1.1:
            results.append({
                'candidate_id': candidate['user_id'],
                'name': candidate['name'],
                'experience': candidate['years_experience'],
                'education': candidate['education_level'],
                'skills': candidate['technical_skills'],
                'salary_expectations': candidate['salary_expectations'],
                'match_score': float(similarities[idx])
            })

    sorted_results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    return sorted_results[:top_n]
