import sqlite3

def init_db():
    conn = sqlite3.connect('car_rental_dss.db')
    cursor = conn.cursor()
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create the price/revenue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenue_management (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_type TEXT NOT NULL,
            daily_rate REAL NOT NULL,
            deposit REAL NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            user_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_revenue_record(data):
    conn = sqlite3.connect('car_rental_dss.db')
    cursor = conn.cursor()
    sql = '''INSERT INTO revenue_management 
             (title, price_type, daily_rate, deposit, start_date, end_date, user_id, vehicle_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(sql, (
        data['title'], data['price_type'], data['daily_rate'], 
        data['deposit'], data['start_date'], data['end_date'], 
        data['user_id'], data['vehicle_id']
    ))
    conn.commit()
    conn.close()

def get_all_revenue():
    conn = sqlite3.connect('car_rental_dss.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM revenue_management")
    rows = cursor.fetchall()
    conn.close()
    return rows