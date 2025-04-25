from app.models.db import get_db


# ----------------------------
# Create a new user
# ----------------------------
def create_user(name, email, password, user_type):
    db, cursor = get_db()
    cursor.execute(
        "INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)",
        (name, email, password, user_type)
    )
    db.commit()
    return cursor.lastrowid


# ----------------------------
# Get user by email
# ----------------------------
def get_user_by_email(email):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    return cursor.fetchone()


# ----------------------------
# Get user by ID
# ----------------------------
def get_user_by_id(user_id):
    db, cursor = get_db()
    cursor.execute("SELECT id, name, email, user_type FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


# ----------------------------
# Delete user
# ----------------------------
def delete_user_by_id(user_id):
    db, cursor = get_db()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
