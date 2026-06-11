"""
Autentifikacija - login, registracija, logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db, hash_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.home"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hash_password(password)),
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.home"))
        flash("Pogrešno korisničko ime ili lozinka!", "error")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not username or not password or not full_name:
            flash("Sva polja su obavezna!", "error")
            return render_template("register.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing:
            conn.close()
            flash("Korisničko ime već postoji!", "error")
            return render_template("register.html")

        conn.execute(
            "INSERT INTO users (username, password, full_name, phone, role) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, phone, "user"),
        )
        conn.commit()
        conn.close()
        flash("Registracija uspješna! Možete se prijaviti.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
