"""
Admin rute - dashboard, upravljanje radnicima, profit izvještaj
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, make_response
)
from database import get_db, hash_password
from utils.pdf_gen import generate_profit_report
from datetime import datetime, date
import functools

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            return redirect(url_for("user.home"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    conn = get_db()

    # Statistike po radniku
    stats = conn.execute(
        """SELECT w.id, w.name, w.specialty,
                  COUNT(a.id) as total_appointments,
                  SUM(CASE WHEN a.status = 'zakazano' THEN 1 ELSE 0 END) as upcoming,
                  SUM(CASE WHEN a.status = 'zakazano' THEN a.price ELSE 0 END) as revenue
           FROM workers w
           LEFT JOIN appointments a ON w.id = a.worker_id
             AND a.appointment_date >= date('now')
           WHERE w.active = 1
           GROUP BY w.id ORDER BY w.name""",
    ).fetchall()

    # Ukupno danas
    today_count = conn.execute(
        """SELECT COUNT(*) as c FROM appointments
           WHERE appointment_date = date('now') AND status = 'zakazano'"""
    ).fetchone()["c"]

    # Ukupni prihod ovog mjeseca
    month_revenue = conn.execute(
        """SELECT COALESCE(SUM(price), 0) as total FROM appointments
           WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', 'now')
           AND status = 'zakazano'"""
    ).fetchone()["total"]

    conn.close()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        today_count=today_count,
        month_revenue=month_revenue,
    )


@admin_bp.route("/workers")
@admin_required
def workers():
    conn = get_db()
    workers_list = conn.execute(
        "SELECT * FROM workers ORDER BY active DESC, name"
    ).fetchall()

    worker_data = []
    for w in workers_list:
        notes = conn.execute(
            "SELECT * FROM worker_notes WHERE worker_id = ? ORDER BY created_at DESC",
            (w["id"],),
        ).fetchall()
        leaves = conn.execute(
            "SELECT * FROM worker_leaves WHERE worker_id = ? ORDER BY leave_date",
            (w["id"],),
        ).fetchall()
        worker_data.append({"worker": w, "notes": notes, "leaves": leaves})

    conn.close()
    return render_template("admin/workers.html", worker_data=worker_data)


@admin_bp.route("/workers/add", methods=["POST"])
@admin_required
def add_worker():
    name = request.form.get("name", "").strip()
    specialty = request.form.get("specialty", "Frizer").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()

    if not name:
        flash("Ime radnika je obavezno!", "error")
        return redirect(url_for("admin.workers"))

    conn = get_db()
    conn.execute(
        "INSERT INTO workers (name, specialty, phone, email) VALUES (?, ?, ?, ?)",
        (name, specialty, phone, email),
    )
    conn.commit()
    conn.close()
    flash(f"Radnik {name} uspješno dodan!", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/deactivate/<int:worker_id>", methods=["POST"])
@admin_required
def deactivate_worker(worker_id):
    conn = get_db()
    conn.execute("UPDATE workers SET active = 0 WHERE id = ?", (worker_id,))
    conn.commit()
    conn.close()
    flash("Radnik uklonjen iz aktivnih.", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/activate/<int:worker_id>", methods=["POST"])
@admin_required
def activate_worker(worker_id):
    conn = get_db()
    conn.execute("UPDATE workers SET active = 1 WHERE id = ?", (worker_id,))
    conn.commit()
    conn.close()
    flash("Radnik aktiviran.", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/add_leave", methods=["POST"])
@admin_required
def add_leave():
    worker_id = request.form.get("worker_id")
    leave_date = request.form.get("leave_date")
    reason = request.form.get("reason", "Odmor").strip()

    if not worker_id or not leave_date:
        flash("Nedostaju podaci!", "error")
        return redirect(url_for("admin.workers"))

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM worker_leaves WHERE worker_id = ? AND leave_date = ?",
        (worker_id, leave_date),
    ).fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO worker_leaves (worker_id, leave_date, reason) VALUES (?, ?, ?)",
            (worker_id, leave_date, reason),
        )
        conn.commit()
        flash("Odmor/odsutnost dodan!", "success")
    else:
        flash("Taj datum već postoji za ovog radnika.", "warning")

    conn.close()
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/delete_leave/<int:leave_id>", methods=["POST"])
@admin_required
def delete_leave(leave_id):
    conn = get_db()
    conn.execute("DELETE FROM worker_leaves WHERE id = ?", (leave_id,))
    conn.commit()
    conn.close()
    flash("Odmor obrisan.", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/add_note", methods=["POST"])
@admin_required
def add_note():
    worker_id = request.form.get("worker_id")
    note_text = request.form.get("note", "").strip()

    if not worker_id or not note_text:
        flash("Nedostaju podaci!", "error")
        return redirect(url_for("admin.workers"))

    conn = get_db()
    conn.execute(
        "INSERT INTO worker_notes (worker_id, note) VALUES (?, ?)",
        (worker_id, note_text),
    )
    conn.commit()
    conn.close()
    flash("Napomena dodata!", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/workers/delete_note/<int:note_id>", methods=["POST"])
@admin_required
def delete_note(note_id):
    conn = get_db()
    conn.execute("DELETE FROM worker_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    flash("Napomena obrisana.", "success")
    return redirect(url_for("admin.workers"))


@admin_bp.route("/appointments")
@admin_required
def all_appointments():
    conn = get_db()
    appts = conn.execute(
        """SELECT a.*, w.name as worker_name, u.full_name as user_name
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           JOIN users u ON a.user_id = u.id
           ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
    ).fetchall()
    conn.close()
    return render_template("admin/appointments.html", appointments=appts)


@admin_bp.route("/profit_report")
@admin_required
def profit_report():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))

    conn = get_db()
    appointments = conn.execute(
        """SELECT a.*, w.name as worker_name, u.full_name as user_name
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           JOIN users u ON a.user_id = u.id
           WHERE strftime('%Y-%m', a.appointment_date) = ?
           AND a.status = 'zakazano'
           ORDER BY a.appointment_date, a.appointment_time""",
        (month,),
    ).fetchall()

    by_worker = conn.execute(
        """SELECT w.name,
                  COUNT(a.id) as count,
                  SUM(a.price) as total
           FROM appointments a
           JOIN workers w ON a.worker_id = w.id
           WHERE strftime('%Y-%m', a.appointment_date) = ?
           AND a.status = 'zakazano'
           GROUP BY w.id ORDER BY w.name""",
        (month,),
    ).fetchall()

    total = sum(r["total"] or 0 for r in by_worker)
    conn.close()

    pdf_bytes = generate_profit_report(appointments, by_worker, total, month)
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=profit_{month}.pdf"
    return response
