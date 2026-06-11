"""
API route za kalendar i termine
"""

from flask import Blueprint, request, jsonify, session
from database import get_db
from datetime import datetime
import functools

api_bp = Blueprint('api', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return view(**kwargs)
    return wrapped_view

@api_bp.route('/calendar/<int:worker_id>/<year>/<month>', methods=['GET'])
@login_required
def calendar(worker_id, year, month):
    """Dobij dostupne termine za radnika"""
    try:
        conn = get_db()
        
        # Pronađi zauzete termine
        booked_dates = conn.execute(
            """SELECT appointment_date FROM appointments 
               WHERE worker_id = ? AND status = 'zakazano'
               AND strftime('%Y-%m', appointment_date) = ?""",
            (worker_id, f"{year}-{month:02d}")
        ).fetchall()
        
        # Pronađi odmor
        leaves = conn.execute(
            """SELECT leave_start_date, leave_end_date FROM worker_leaves 
               WHERE worker_id = ?""",
            (worker_id,)
        ).fetchall()
        
        conn.close()
        
        booked = [d['appointment_date'] for d in booked_dates]
        leave_dates = []
        for leave in leaves:
            # Generiši sve datume između start i end
            start = datetime.strptime(leave['leave_start_date'], '%Y-%m-%d')
            end = datetime.strptime(leave['leave_end_date'], '%Y-%m-%d')
            current = start
            while current <= end:
                leave_dates.append(current.strftime('%Y-%m-%d'))
                current = datetime.fromordinal(current.toordinal() + 1)
        
        return jsonify({
            'status': 'success',
            'booked': booked,
            'leaves': leave_dates
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    """Zakaži termin"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        date = data.get('date')
        time = data.get('time')
        service = data.get('service', 'Šišanje')
        price = data.get('price', 10.0)
        currency = data.get('currency', 'EUR')
        notes = data.get('notes', '')
        
        conn = get_db()
        conn.execute(
            """INSERT INTO appointments 
               (user_id, worker_id, appointment_date, appointment_time, service, price, currency, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session['user_id'], worker_id, date, time, service, price, currency, notes)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Termin zakazan'}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Otkaži termin"""
    try:
        conn = get_db()
        conn.execute(
            "UPDATE appointments SET status = 'otkazano' WHERE id = ? AND user_id = ?",
            (appointment_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Termin otkazan'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
