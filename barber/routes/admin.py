"""
Admin route sa notifikacijama i pomoćnim interfaceom
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database import get_db
from datetime import datetime, timedelta
import functools

admin_bp = Blueprint('admin', __name__)

def login_required(view):
    """Provjeri da li je korisnik ulogovan i admin"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    conn = get_db()
    
    # KPI karti
    today = datetime.now().strftime('%Y-%m-%d')
    appointments_today = conn.execute(
        "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ? AND status = 'zakazano'",
        (today,)
    ).fetchone()['count']
    
    total_revenue = conn.execute(
        "SELECT SUM(price) as total FROM appointments WHERE status = 'zakazano'"
    ).fetchone()['total'] or 0
    
    workers_count = conn.execute(
        "SELECT COUNT(*) as count FROM workers WHERE active = 1"
    ).fetchone()['count']
    
    # Notifikacije
    notifications = conn.execute(
        "SELECT * FROM admin_notifications WHERE admin_id = ? ORDER BY created_at DESC LIMIT 5",
        (session['user_id'],)
    ).fetchall()
    
    unread_notifications = conn.execute(
        "SELECT COUNT(*) as count FROM admin_notifications WHERE admin_id = ? AND is_read = 0",
        (session['user_id'],)
    ).fetchone()['count']
    
    conn.close()
    
    return render_template('admin/dashboard.html',
        appointments_today=appointments_today,
        total_revenue=total_revenue,
        workers_count=workers_count,
        notifications=notifications,
        unread_count=unread_notifications
    )

@admin_bp.route('/workers')
@login_required
def workers():
    """Upravljanje radnicima"""
    conn = get_db()
    workers_list = conn.execute(
        "SELECT id, name, specialty, phone, email, image_path, active, created_at FROM workers"
    ).fetchall()
    conn.close()
    
    return render_template('admin/workers.html', workers=workers_list)

@admin_bp.route('/worker/<int:worker_id>/leaves')
@login_required
def worker_leaves(worker_id):
    """Upravljanje odmorima radnika - NOVO SA START/END DATUMIMA"""
    conn = get_db()
    
    worker = conn.execute("SELECT * FROM workers WHERE id = ?", (worker_id,)).fetchone()
    leaves = conn.execute(
        "SELECT id, leave_start_date, leave_end_date, reason FROM worker_leaves WHERE worker_id = ? ORDER BY leave_start_date DESC",
        (worker_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/worker_leaves.html', worker=worker, leaves=leaves)

@admin_bp.route('/api/worker/<int:worker_id>/add-leave', methods=['POST'])
@login_required
def add_leave(worker_id):
    """Dodaj odmor sa start i end datumom"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        reason = data.get('reason', 'Odmor')
        
        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': 'Nedostaju datumi'}), 400
        
        conn = get_db()
        conn.execute(
            "INSERT INTO worker_leaves (worker_id, leave_start_date, leave_end_date, reason) VALUES (?, ?, ?, ?)",
            (worker_id, start_date, end_date, reason)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Odmor dodan'}), 201
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/notifications')
@login_required
def notifications():
    """Sve notifikacije sa pomoćima"""
    conn = get_db()
    
    notifications = conn.execute(
        "SELECT * FROM admin_notifications WHERE admin_id = ? ORDER BY created_at DESC",
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/notifications.html', notifications=notifications)

@admin_bp.route('/api/notification/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    """Označi notifikaciju kao pročitanu"""
    try:
        conn = get_db()
        conn.execute(
            "UPDATE admin_notifications SET is_read = 1 WHERE id = ? AND admin_id = ?",
            (notif_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/appointments')
@login_required
def appointments():
    """Svi termini sa pretragom"""
    conn = get_db()
    
    appointments = conn.execute(
        """SELECT a.id, a.appointment_date, a.appointment_time, a.service, a.price, a.currency, a.status,
                  u.full_name as user_name, w.name as worker_name
           FROM appointments a
           JOIN users u ON a.user_id = u.id
           JOIN workers w ON a.worker_id = w.id
           ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/appointments.html', appointments=appointments)

@admin_bp.route('/help-requests')
@login_required
def help_requests():
    """Help zahtjevi od korisnika"""
    conn = get_db()
    
    help_requests = conn.execute(
        """SELECT n.id, n.message, n.user_id, n.created_at, n.is_read, u.full_name
           FROM admin_notifications n
           LEFT JOIN users u ON n.user_id = u.id
           WHERE n.type = 'help_request' AND n.admin_id = ?
           ORDER BY n.is_read ASC, n.created_at DESC""",
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/help_requests.html', help_requests=help_requests)
