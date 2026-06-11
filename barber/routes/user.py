"""
Korisničke rute - Home, Zakazivanje, Moji termini
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database import get_db
from datetime import datetime, timedelta
import functools

user_bp = Blueprint('user', __name__)

def login_required(view):
    """Provjera prijave"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@user_bp.route('/home')
@login_required
def home():
    """Početna stranica korisnika"""
    conn = get_db()
    workers = conn.execute("SELECT * FROM workers WHERE active = 1").fetchall()
    conn.close()
    
    return render_template('user/home.html', workers=workers)

@user_bp.route('/schedule/<int:worker_id>')
@login_required
def schedule(worker_id):
    """Zakazivanje termina"""
    conn = get_db()
    worker = conn.execute("SELECT * FROM workers WHERE id = ?", (worker_id,)).fetchone()
    conn.close()
    
    if not worker:
        return redirect(url_for('user.home'))
    
    return render_template('user/schedule.html', worker=worker)

@user_bp.route('/appointments')
@login_required
def appointments():
    """Moji termini"""
    conn = get_db()
    appointments = conn.execute(
        """SELECT a.id, a.appointment_date, a.appointment_time, a.service, a.price, a.currency, a.status, a.notes,
                  w.name as worker_name
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           WHERE a.user_id = ?
           ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('user/appointments.html', appointments=appointments)

@user_bp.route('/profile')
@login_required
def profile():
    """Profil korisnika"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('user/profile.html', user=user)

@user_bp.route('/api/update-currency', methods=['POST'])
@login_required
def update_currency():
    """Ažuriranje valute"""
    try:
        data = request.get_json()
        currency = data.get('currency')
        
        conn = get_db()
        conn.execute("UPDATE users SET currency = ? WHERE id = ?", (currency, session['user_id']))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
