"""
Autentifikacija route - Login, Registracija, Logout
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database import get_db, hash_password
import functools

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login stranica"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        
        if user and user['password'] == hash_password(password):
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['full_name']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
        else:
            return render_template('login.html', error='Pogrešno korisničko ime ili lozinka')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registracija"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        currency = request.form.get('currency', 'EUR')
        
        conn = get_db()
        
        # Provjera da li korisnik postoji
        if conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            conn.close()
            return render_template('register.html', error='Korisničko ime već postoji')
        
        conn.execute(
            "INSERT INTO users (username, password, full_name, phone, currency, role) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, phone, currency, 'user')
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('auth.login', message='Registracija uspješna! Prijavite se.'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))
