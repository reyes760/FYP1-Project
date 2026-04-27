import sqlite3
from config import USER_DB_PATH

def init_user_db():
    """Initialize user database with schema"""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            user_id       TEXT PRIMARY KEY,
            first_name    TEXT NOT NULL,
            last_name     TEXT NOT NULL,
            full_name     TEXT NOT NULL,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ user.db ready")

def get_db_connection():
    """Get connection to user database"""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_next_user_id():
    """Generate next user ID (U001, U002, etc.)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM user")
        count = cursor.fetchone()['count'] + 1
        user_id = f"U{count:03d}"
        print(f"🆕 Next ID: {user_id} (#{count})")
        return user_id
    finally:
        conn.close()