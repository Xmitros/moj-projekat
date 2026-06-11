"""
BROS - Frizerski Salon Aplikacija
Pokretanje: python3 app.py
Otvoriti browser: http://localhost:5000
"""

from flask import Flask
from database import init_db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.api import api_bp

app = Flask(__name__)
app.secret_key = "bros_salon_secret_key_2024"

# Registracija Blueprint-ova
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(api_bp, url_prefix="/api")

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  BROS Frizerski Salon - Pokrenut!")
    print("  Otvorite: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
