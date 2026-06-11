"""
Korisničke rute - početna, frizeri, zakazivanje, termini, račun
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify, make_response
)
from database import get_db
from utils.pdf_gen import generate_receipt
from datetime import datetime, date
import functools

user_bp = Blueprint("user", __name__)


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated


@user_bp.route("/")
@login_required
def home():
    conn = get_db()
    workers = conn.execute(
        "SELECT * FROM workers WHERE active = 1 ORDER BY name"
    ).fetchall()
    conn.close()
    return render_template("user/home.html", workers=workers)


@user_bp.route("/worker/<int:worker_id>")
@login_required
def worker_calendar(worker_id):
    conn = get_db()
    worker = conn.execute(
        "SELECT * FROM workers WHERE id = ? AND active = 1", (worker_id,)
    ).fetchone()
    if not worker:
        flash("Radnik nije pronađen.", "error")
        return redirect(url_for("user.home"))

    # Uzmi sve zakazane termine za ovog radnika
    booked = conn.execute(
        """SELECT appointment_date, appointment_time FROM appointments
           WHERE worker_id = ? AND status != 'otkazano'""",
        (worker_id,),
    ).fetchall()

    # Uzmi odmore radnika
    leaves = conn.execute(
        "SELECT leave_date FROM worker_leaves WHERE worker_id = ?", (worker_id,)
    ).fetchall()

    conn.close()

    booked_slots = {}
    for b in booked:
        d = b["appointment_date"]
        if d not in booked_slots:
            booked_slots[d] = []
        booked_slots[d].append(b["appointment_time"])

    leave_dates = [l["leave_date"] for l in leaves]

    return render_template(
        "user/calendar.html",
        worker=worker,
        booked_slots=booked_slots,
        leave_dates=leave_dates,
        today=date.today().isoformat(),
    )


@user_bp.route("/book", methods=["POST"])
@login_required
def book():
    worker_id = request.form.get("worker_id")
    appt_date = request.form.get("date")
    appt_time = request.form.get("time")
    service = request.form.get("service", "Šišanje")
    price = float(request.form.get("price", 10.0))

    if not all([worker_id, appt_date, appt_time]):
        flash("Nedostaju podaci za zakazivanje!", "error")
        return redirect(url_for("user.home"))

    # Provjera da datum nije u prošlosti
    try:
        chosen = datetime.strptime(appt_date, "%Y-%m-%d").date()
        if chosen < date.today():
            flash("Ne možete zakazati termin u prošlosti!", "error")
            return redirect(url_for("user.worker_calendar", worker_id=worker_id))
    except ValueError:
        flash("Neispravan datum!", "error")
        return redirect(url_for("user.home"))

    conn = get_db()

    # Provjera odmora
    leave = conn.execute(
        "SELECT id FROM worker_leaves WHERE worker_id = ? AND leave_date = ?",
        (worker_id, appt_date),
    ).fetchone()
    if leave:
        conn.close()
        flash("Radnik je na odmoru tog dana!", "error")
        return redirect(url_for("user.worker_calendar", worker_id=worker_id))

    # Provjera dvostrukog termina
    existing = conn.execute(
        """SELECT id FROM appointments
           WHERE worker_id = ? AND appointment_date = ? AND appointment_time = ?
           AND status != 'otkazano'""",
        (worker_id, appt_date, appt_time),
    ).fetchone()
    if existing:
        conn.close()
        flash("Taj termin je već zauzet! Odaberite drugo vrijeme.", "error")
        return redirect(url_for("user.worker_calendar", worker_id=worker_id))

    conn.execute(
        """INSERT INTO appointments
           (user_id, worker_id, appointment_date, appointment_time, service, price, status)
           VALUES (?, ?, ?, ?, ?, ?, 'zakazano')""",
        (session["user_id"], worker_id, appt_date, appt_time, service, price),
    )
    conn.commit()
    conn.close()

    flash(f"Termin uspješno zakazan za {appt_date} u {appt_time}!", "success")
    return redirect(url_for("user.appointments"))


@user_bp.route("/appointments")
@login_required
def appointments():
    conn = get_db()
    appts = conn.execute(
        """SELECT a.*, w.name as worker_name
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           WHERE a.user_id = ?
           ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("user/appointments.html", appointments=appts)


@user_bp.route("/cancel/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    conn = get_db()
    appt = conn.execute(
        "SELECT * FROM appointments WHERE id = ? AND user_id = ?",
        (appointment_id, session["user_id"]),
    ).fetchone()
    if appt:
        conn.execute(
            "UPDATE appointments SET status = 'otkazano' WHERE id = ?",
            (appointment_id,),
        )
        conn.commit()
        flash("Termin otkazan.", "success")
    conn.close()
    return redirect(url_for("user.appointments"))


@user_bp.route("/receipt/<int:appointment_id>")
@login_required
def receipt(appointment_id):
    conn = get_db()
    appt = conn.execute(
        """SELECT a.*, w.name as worker_name, u.full_name as user_name
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           JOIN users u ON a.user_id = u.id
           WHERE a.id = ? AND a.user_id = ?""",
        (appointment_id, session["user_id"]),
    ).fetchone()
    conn.close()

    if not appt:
        flash("Termin nije pronađen!", "error")
        return redirect(url_for("user.appointments"))

    pdf_bytes = generate_receipt(appt)
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=racun_{appointment_id}.pdf"
    )
    return response
