"""
API rute - JSON odgovori za AJAX pozive
"""

from flask import Blueprint, jsonify, session, request
from database import get_db
from datetime import datetime, date, timedelta

api_bp = Blueprint("api", __name__)


@api_bp.route("/booked_slots/<int:worker_id>/<string:month>")
def booked_slots(worker_id, month):
    """Vrati zauzete termine za radnika u datom mjesecu (YYYY-MM)."""
    conn = get_db()

    booked = conn.execute(
        """SELECT appointment_date, appointment_time
           FROM appointments
           WHERE worker_id = ? AND strftime('%Y-%m', appointment_date) = ?
           AND status != 'otkazano'""",
        (worker_id, month),
    ).fetchall()

    leaves = conn.execute(
        """SELECT leave_date FROM worker_leaves
           WHERE worker_id = ?
           AND strftime('%Y-%m', leave_date) = ?""",
        (worker_id, month),
    ).fetchall()

    conn.close()

    result = {}
    for b in booked:
        d = b["appointment_date"]
        if d not in result:
            result[d] = {"booked": [], "leave": False}
        result[d]["booked"].append(b["appointment_time"])

    for l in leaves:
        d = l["leave_date"]
        if d not in result:
            result[d] = {"booked": [], "leave": False}
        result[d]["leave"] = True

    return jsonify(result)


@api_bp.route("/available_times/<int:worker_id>/<string:appt_date>")
def available_times(worker_id, appt_date):
    """Vrati slobodne termine za odabrani dan."""
    all_times = [
        "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
        "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
        "17:00", "17:30", "18:00",
    ]

    # Provjera odmora
    conn = get_db()
    leave = conn.execute(
        "SELECT id FROM worker_leaves WHERE worker_id = ? AND leave_date = ?",
        (worker_id, appt_date),
    ).fetchone()

    if leave:
        conn.close()
        return jsonify({"leave": True, "times": []})

    booked = conn.execute(
        """SELECT appointment_time FROM appointments
           WHERE worker_id = ? AND appointment_date = ? AND status != 'otkazano'""",
        (worker_id, appt_date),
    ).fetchall()
    conn.close()

    booked_times = {b["appointment_time"] for b in booked}

    # Filter prošlih termina za danas
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")

    free_times = []
    for t in all_times:
        if t in booked_times:
            continue
        if appt_date == today and t <= now_time:
            continue
        free_times.append(t)

    return jsonify({"leave": False, "times": free_times})
