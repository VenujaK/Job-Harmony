from flask_jwt_extended import get_jwt_identity
from flask import jsonify

# ----------------------------
# Role Check: Admin
# ----------------------------
def admin_required():
    identity = get_jwt_identity()
    if identity['type'] != 'admin':
        return jsonify({'error': 'Admins only'}), 403
    return None


# ----------------------------
# Role Check: Employer
# ----------------------------
def employer_required():
    identity = get_jwt_identity()
    if identity['type'] != 'employer':
        return jsonify({'error': 'Employers only'}), 403
    return None


# ----------------------------
# Role Check: Candidate
# ----------------------------
def candidate_required():
    identity = get_jwt_identity()
    if identity['type'] != 'candidate':
        return jsonify({'error': 'Candidates only'}), 403
    return None
