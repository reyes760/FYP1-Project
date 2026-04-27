import sqlite3
from config import SCHEDULE_DB_PATH

def init_schedule_db():
    """Initialize schedule database with schema"""
    conn = sqlite3.connect(SCHEDULE_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            vehicle_id INTEGER,
            plate      TEXT,
            type       TEXT NOT NULL DEFAULT 'Booking',
            customer   TEXT,
            start_date TEXT NOT NULL,
            end_date   TEXT NOT NULL,
            notes      TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ schedule.db ready")

def get_schedule_db():
    """Get connection to schedule database"""
    conn = sqlite3.connect(SCHEDULE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn