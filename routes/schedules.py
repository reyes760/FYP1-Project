from flask import Blueprint, request, jsonify
from datetime import datetime
from database.schedule_db import get_schedule_db

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules"""
    conn = get_schedule_db()
    try:
        schedules = conn.execute('SELECT * FROM schedules ORDER BY start_date ASC').fetchall()
        return jsonify({'success': True, 'schedules': [dict(s) for s in schedules]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@schedules_bp.route('/api/schedules', methods=['POST'])
def add_schedule():
    """Add new schedule"""
    data = request.get_json()
    conn = get_schedule_db()
    try:
        conn.execute('''
            INSERT INTO schedules (title, vehicle_id, plate, type, customer, start_date, end_date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'].strip(),
            data.get('vehicle_id'),
            data.get('plate', '').strip(),
            data.get('type', 'Booking'),
            data.get('customer', '').strip(),
            data['start_date'],
            data['end_date'],
            data.get('notes', '').strip(),
            datetime.now().isoformat()
        ))
        conn.commit()
        return jsonify({'success': True, 'message': 'Schedule added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update schedule"""
    data = request.get_json()
    conn = get_schedule_db()
    try:
        conn.execute('''
            UPDATE schedules
            SET title=?, vehicle_id=?, plate=?, type=?, customer=?, start_date=?, end_date=?, notes=?
            WHERE id=?
        ''', (
            data['title'].strip(),
            data.get('vehicle_id'),
            data.get('plate', '').strip(),
            data.get('type', 'Booking'),
            data.get('customer', '').strip(),
            data['start_date'],
            data['end_date'],
            data.get('notes', '').strip(),
            schedule_id
        ))
        conn.commit()
        return jsonify({'success': True, 'message': 'Schedule updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@schedules_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete schedule"""
    conn = get_schedule_db()
    try:
        conn.execute('DELETE FROM schedules WHERE id=?', (schedule_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Schedule deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()