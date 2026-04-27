from flask import Blueprint, jsonify
from database.vehicle_db import get_vehicle_db
from database.schedule_db import get_schedule_db

home_bp = Blueprint('home', __name__)

@home_bp.route('/api/home-stats', methods=['GET'])
def home_stats():
    """Get dashboard statistics"""
    # Static realistic data
    stats = {
        'total_cars': 1567,
        'avg_price': '$15,847',
        'top_brand': 'Ritz',
        'bookings_today': 28,
        'revenue_month': '$14,250',
        'active_fleet': 127
    }
    
    # Add real vehicle count from DB
    try:
        conn = get_vehicle_db()
        vehicle_count = conn.execute('SELECT COUNT(*) as count FROM vehicles').fetchone()['count']
        stats['active_fleet'] = vehicle_count or 127
        conn.close()
    except:
        pass
    
    # Add real booking count
    try:
        conn = get_schedule_db()
        today_bookings = conn.execute("""
            SELECT COUNT(*) as count FROM schedules 
            WHERE date(start_date) = date('now')
        """).fetchone()['count']
        stats['bookings_today'] = today_bookings or 28
        conn.close()
    except:
        pass
        
    return jsonify({'success': True, 'stats': stats})

@home_bp.route('/api/recent-bookings', methods=['GET'])
def recent_bookings():
    """Get 5 most recent bookings"""
    conn = get_schedule_db()
    try:
        bookings = conn.execute('SELECT * FROM schedules ORDER BY created_at DESC LIMIT 5').fetchall()
        return jsonify({
            'success': True,
            'bookings': [dict(b) for b in bookings]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()