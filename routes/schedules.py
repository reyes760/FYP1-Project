from flask import Blueprint, request, jsonify
from datetime import datetime
from database.schedule_db import get_schedule_db

schedules_bp = Blueprint('schedules', __name__)

# schedules.py
@schedules_bp.route('/api/schedules', methods=['GET'])
def get_schedules():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID missing'}), 400

    conn = get_schedule_db()
    try:
        # Filter by the user_id string (e.g., 'U001')
        schedules = conn.execute(
            'SELECT * FROM schedules WHERE user_id = ? ORDER BY start_date ASC', 
            (user_id,)
        ).fetchall()
        return jsonify({'success': True, 'schedules': [dict(row) for row in schedules]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@schedules_bp.route('/api/schedules', methods=['POST'])
def add_schedule():
    # Add new schedule
    data = request.get_json()

    user_id = data.get('user_id')
    plate = data.get('plate')
    new_start = data.get('start_date')
    new_end = data.get('end_date')

    if not user_id:
        return jsonify({'success': False, 'message': 'Session expired. Please try again.'}), 401
    
    conn = get_schedule_db()

    query = '''
        SELECT id FROM schedules 
        WHERE plate = ? 
        AND (? <= end_date AND ? >= start_date)
    '''
    existing = conn.execute(query, (plate, new_start, new_end)).fetchone()

    if existing:
        conn.close()
        return jsonify({
            'success': False, 
            'message': f'Vehicle {plate} is already reserved.'
        }), 409
    
    try:
        conn.execute('''
            INSERT INTO schedules (
                user_id, title, vehicle_id, plate, type, 
                customer, start_date, end_date, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['title'].strip(),
            data.get('vehicle_id'),
            data.get('plate', '').strip(),
            data.get('type', 'Booking'),
            data.get('customer', '').strip(),
            data['start_date'],
            data['end_date'],
            data.get('notes', '').strip(),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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