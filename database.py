import sqlite3
import os
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "fitplan.db")

def init_database():
    """Initialize the SQLite database with users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            profile_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # add profile_json column if missing (for existing DBs)
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'profile_json' not in cols:
        cursor.execute('ALTER TABLE users ADD COLUMN profile_json TEXT')
    
    conn.commit()
    conn.close()

def user_exists(email):
    """Check if a user with the given email already exists."""
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(name, email, password_hash, profile=None):
    """Register a new user in the database. Optionally include serialized profile data."""
    email = email.strip().lower()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if profile is not None:
            import json
            profile_json = json.dumps(profile)
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, profile_json)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, profile_json))
        else:
            cursor.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (name, email, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")
        return False

def get_user_by_email(email):
    """Retrieve user data by email."""
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash, profile_json FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        data = {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "password_hash": user[3]
        }
        if user[4]:
            import json
            try:
                data["profile"] = json.loads(user[4])
            except Exception:
                data["profile"] = None
        else:
            data["profile"] = None
        return data
    return None

def get_user_by_name_email(name, email):
    """Retrieve user data by name and email."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash FROM users WHERE name = ? AND email = ?', (name, email))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "password_hash": user[3]
        }
    return None

def update_user_profile(email, profile):
    """Store serialized profile data for a given user."""
    import json
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET profile_json = ?, updated_at = CURRENT_TIMESTAMP WHERE email = ?',
                   (json.dumps(profile), email))
    conn.commit()
    conn.close()


def get_all_users():
    """Debug: Get all users in database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users')
    users = cursor.fetchall()
    conn.close()
    return users
