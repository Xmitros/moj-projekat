"""
Barber Shop - HIGH END Aplikacija
Pokretanje: python3 app.py
Otvoriti browser: https://localhost:5000
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from database import init_db, get_db, hash_password
from datetime import datetime

app = Flask(__name__)
app.secret_key = "barber_shop_premium_2024"

# Konfiguracija za HTTPS
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Import routes
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.api import api_bp
from routes.chatbot import chatbot_bp

# Registracija Blueprint-ova
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")

@app.context_processor
def inject_user():
    """Dostavi korisnika u sve template-e"""
    if 'user_id' in session:
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
        return dict(current_user=user)
    return dict(current_user=None)

@app.route('/')
def index():
    """Početna stranica"""
    if 'user_id' in session:
        user_role = session.get('user_role')
        if user_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.home'))
    return render_template('index.html')

@app.route('/about')
def about():
    """O nama stranica"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Kontakt stranica"""
    return render_template('contact.html')

@app.errorhandler(404)
def not_found(e):
    """404 greška"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500 greška"""
    return render_template('500.html'), 500

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("  🏆 BARBER SHOP - HIGH END APLIKACIJA 🏆")
    print("  Pokrenut!")
    print("  Otvorite: https://localhost:5000")
    print("=" * 60)
    
    # Za development
    app.run(debug=True, host="0.0.0.0", port=5000)
