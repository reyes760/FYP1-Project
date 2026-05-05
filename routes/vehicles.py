from flask import Blueprint, request, jsonify
import sqlite3
from database.vehicle_db import get_vehicle_db

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get vehicles belonging only to the logged-in user"""
    # 1. Get the user_id from the URL parameters
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required to fetch fleet'}), 400

    conn = get_vehicle_db()
    try:
        # 2. Filter the SQL query using a WHERE clause
        query = 'SELECT * FROM vehicles WHERE user_id = ? ORDER BY id ASC'
        vehicles = conn.execute(query, (user_id,)).fetchall()
        
        return jsonify({
            'success': True, 
            'vehicles': [dict(v) for v in vehicles]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@vehicles_bp.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    """Add new vehicle for a specific user"""
    data = request.get_json()
    user_id = data.get('user_id')
    plate = data['plate'].upper().strip()
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User session expired. Please log in again.'}), 401

    conn = get_vehicle_db()
    try:
        # ✅ FIX: Only check for duplicates BELONGING TO THIS USER
        existing = conn.execute(
            'SELECT id FROM vehicles WHERE plate = ? AND user_id = ?', 
            (plate, user_id)
        ).fetchone()

        if existing:
            return jsonify({'success': False, 'message': 'Plate number existed'})

        conn.execute('''
            INSERT INTO vehicles (user_id, plate, brand, model, year, color, status, mileage, last_service)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 
              plate, 
              data['brand'], 
              data['model'], 
              int(data['year']), 
              data.get('color'), 
              data.get('status'), 
              int(data.get('mileage', 0)), 
              data.get('last_service')
        ))
        conn.commit()
        return jsonify({'success': True, 'message': 'Vehicle added successfully'})
    except sqlite3.IntegrityError:
        # This catches the error if the database-level UNIQUE constraint is hit
        return jsonify({'success': False, 'message': 'Database Error: Plate number already exists.'})
    except Exception as e:
        # General catch-all for typos or connection issues
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        conn.close()

@vehicles_bp.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """Update vehicle details"""
    data = request.get_json()
    conn = get_vehicle_db()
    try:
        conn.execute('''
            UPDATE vehicles
            SET plate=?, brand=?, model=?, year=?, color=?, status=?, mileage=?, last_service=?
            WHERE id=?
        ''', (
            data['plate'].upper().strip(),
            data['brand'].strip(),
            data['model'].strip(),
            int(data['year']),
            data.get('color', '').strip(),
            data.get('status', 'Available'),
            int(data.get('mileage', 0)),
            data.get('last_service', ''),
            vehicle_id
        ))
        conn.commit()
        return jsonify({'success': True, 'message': 'Vehicle updated successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Plate number already exists'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@vehicles_bp.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Delete vehicle"""
    conn = get_vehicle_db()
    try:
        conn.execute('DELETE FROM vehicles WHERE id=?', (vehicle_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Vehicle deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()