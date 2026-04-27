from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
from database.user_db import get_db_connection, get_next_user_id
from utils.verification import send_verification_email, verify_code

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    conn = get_db_connection()
    try:
        data = request.get_json()
        required = ['first_name', 'last_name', 'username', 'email', 'password', 'verification_code']
        
        # Validate required fields
        for field in required:
            if not data.get(field) or not data[field].strip():
                return jsonify({'success': False, 'message': f'{field.replace("_", " ").title()} required'}), 400

        cursor = conn.cursor()
        # Check for existing username or email
        cursor.execute(
            "SELECT user_id FROM user WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (data['username'].strip().lower(), data['email'].strip().lower())
        )
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 409
        
        # Verify the email code generated
        is_valid, v_message = verify_code(data['email'], data['verification_code'])
        if not is_valid:
            return jsonify({'success': False, 'message': v_message}), 400

        # Generate new user ID and create user
        user_id = get_next_user_id()
        full_name = f"{data['first_name'].strip()} {data['last_name'].strip()}"

        cursor.execute('''
            INSERT INTO user (user_id, first_name, last_name, full_name, username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['first_name'].strip(),
            data['last_name'].strip(),
            full_name,
            data['username'].strip().lower(),
            data['email'].strip().lower(),
            generate_password_hash(data['password']),
            datetime.now().isoformat()
        ))
        conn.commit()
        print(f"✅ CREATED: {user_id} - {full_name}")
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user_id': user_id,
            'full_name': full_name,
            'username': data['username'].strip().lower(),
            'email': data['email'].strip().lower()
        })

    except sqlite3.IntegrityError as e:
        print(f"❌ Duplicate key: {e}")
        return jsonify({'success': False, 'message': 'User ID conflict - try again'}), 409
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    conn = get_db_connection()
    try:
        data = request.get_json()
        username = data.get('username', '').strip().lower()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400

        user = conn.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if not user:
            print(f"❌ Login failed: User '{username}' not found")
            return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

        if check_password_hash(user['password_hash'], password):
            print(f"✅ Login successful: {user['user_id']} - {user['username']}")
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
        else:
            print(f"❌ Login failed: Invalid password for user '{username}'")
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': 'Login service unavailable'}), 500
    finally:
        conn.close()

@auth_bp.route('/api/send-verification', methods=['POST'])
def handle_send_code():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
        
    if send_verification_email(email):
        return jsonify({'success': True, 'message': 'Code sent successfully'})
    return jsonify({'success': False, 'message': 'Failed to send email'}), 500