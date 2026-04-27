from flask import Blueprint, request, jsonify
import sqlite3
from database.vehicle_db import get_vehicle_db

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicles"""
    conn = get_vehicle_db()
    try:
        vehicles = conn.execute('SELECT * FROM vehicles ORDER BY id ASC').fetchall()
        return jsonify({'success': True, 'vehicles': [dict(v) for v in vehicles]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@vehicles_bp.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    """Add new vehicle"""
    data = request.get_json()
    conn = get_vehicle_db()
    try:
        conn.execute('''
            INSERT INTO vehicles (plate, brand, model, year, color, status, mileage, last_service)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['plate'].upper().strip(),
            data['brand'].strip(),
            data['model'].strip(),
            int(data['year']),
            data.get('color', '').strip(),
            data.get('status', 'Available'),
            int(data.get('mileage', 0)),
            data.get('last_service', '')
        ))
        conn.commit()
        return jsonify({'success': True, 'message': 'Vehicle added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Plate number already exists'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
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