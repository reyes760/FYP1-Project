from flask import Blueprint, jsonify
from database.user_db import get_db_connection

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - returns database status and user count"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM user")
        count = cursor.fetchone()['count']
        
        cursor.execute("SELECT user_id FROM user ORDER BY CAST(SUBSTR(user_id, 2) AS INTEGER) ASC LIMIT 1")
        first_id = cursor.fetchone()
        
        cursor.execute("SELECT user_id FROM user ORDER BY CAST(SUBSTR(user_id, 2) AS INTEGER) DESC LIMIT 1")
        last_id = cursor.fetchone()
        
        return jsonify({
            'status': 'OK',
            'db_status': 'Connected ✅',
            'users_count': count,
            'first_user_id': first_id['user_id'] if first_id else None,
            'last_user_id': last_id['user_id'] if last_id else None,
        })
    finally:
        conn.close()

@users_bp.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user ORDER BY CAST(SUBSTR(user_id, 2) AS INTEGER) ASC")
        users = [dict(row) for row in cursor.fetchall()]
        return jsonify(users)
    finally:
        conn.close()

@users_bp.route('/api/users/count', methods=['GET'])
def users_count():
    """Get total user count"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM user")
        count = cursor.fetchone()['count']
        return jsonify({'count': count})
    finally:
        conn.close()