import sqlite3
from config import VEHICLE_DB_PATH

def init_vehicle_db():
    """Initialize vehicle database with schema"""
    conn = sqlite3.connect(VEHICLE_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plate        TEXT NOT NULL UNIQUE,
            brand        TEXT NOT NULL,
            model        TEXT NOT NULL,
            year         INTEGER NOT NULL,
            color        TEXT,
            status       TEXT DEFAULT 'Available',
            mileage      INTEGER DEFAULT 0,
            last_service TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ vehicle.db ready")

def get_vehicle_db():
    """Get connection to vehicle database"""
    conn = sqlite3.connect(VEHICLE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn