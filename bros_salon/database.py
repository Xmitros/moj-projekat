"""
Baza podataka - SQLite
Inicijalizacija tabela i seed podaci
"""

import sqlite3
import hashlib
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bros.db")


def get_db():
    """Dobij konekciju ka bazi."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Kreira sve tabele i ubacuje pocetne podatke."""
    conn = get_db()
    cur = conn.cursor()

    # Korisnici
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Radnici (frizeri)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT DEFAULT 'Frizer',
            phone TEXT,
            email TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Termini
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            worker_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            service TEXT DEFAULT 'Šišanje',
            price REAL DEFAULT 10.0,
            status TEXT DEFAULT 'zakazano',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
    """)

    # Odmori radnika
    cur.execute("""
        CREATE TABLE IF NOT EXISTS worker_leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            leave_date TEXT NOT NULL,
            reason TEXT DEFAULT 'Odmor',
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
    """)

    # Napomene admina za radnike
    cur.execute("""
        CREATE TABLE IF NOT EXISTS worker_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
    """)

    conn.commit()

    # Seed: Admin korisnik
    admin_exists = cur.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not admin_exists:
        cur.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator", "admin"),
        )

    # Seed: Test korisnik
    user_exists = cur.execute(
        "SELECT id FROM users WHERE username = 'korisnik'"
    ).fetchone()
    if not user_exists:
        cur.execute(
            "INSERT INTO users (username, password, full_name, phone, role) VALUES (?, ?, ?, ?, ?)",
            ("korisnik", hash_password("korisnik123"), "Marko Petrović", "065123456", "user"),
        )

    # Seed: Radnici
    workers_exist = cur.execute("SELECT COUNT(*) as c FROM workers").fetchone()["c"]
    if workers_exist == 0:
        workers = [
            ("Marko", "Šišanje & Brijanje", "065111222"),
            ("Janko", "Muški & Ženski", "065333444"),
            ("Petar", "Boja & Frizure", "065555666"),
            ("Stefan", "Šišanje", "065777888"),
        ]
        for w in workers:
            cur.execute(
                "INSERT INTO workers (name, specialty, phone) VALUES (?, ?, ?)", w
            )

    conn.commit()
    conn.close()
    print("Baza inicijalizovana.")
