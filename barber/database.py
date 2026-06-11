"""
Barber Shop - SQLite Database
Inicijalizacija tabela sa novim poljima za odmor i valulu
"""

import sqlite3
import hashlib
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "barber.db")


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
            currency TEXT DEFAULT 'EUR',
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
            image_path TEXT,
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
            currency TEXT DEFAULT 'EUR',
            status TEXT DEFAULT 'zakazano',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
    """)

    # Odmori radnika - NOVO sa start_date i end_date
    cur.execute("""
        CREATE TABLE IF NOT EXISTS worker_leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            leave_start_date TEXT NOT NULL,
            leave_end_date TEXT NOT NULL,
            reason TEXT DEFAULT 'Odmor',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
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

    # Admin notifikacije - NOVO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'help_request',
            user_id INTEGER,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # AI Chat FAQ - NOVO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed: Admin korisnik
    admin_exists = cur.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not admin_exists:
        cur.execute(
            "INSERT INTO users (username, password, full_name, role, currency) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator", "admin", "EUR"),
        )

    # Seed: Test korisnik
    user_exists = cur.execute(
        "SELECT id FROM users WHERE username = 'korisnik'"
    ).fetchone()
    if not user_exists:
        cur.execute(
            "INSERT INTO users (username, password, full_name, phone, role, currency) VALUES (?, ?, ?, ?, ?, ?)",
            ("korisnik", hash_password("korisnik123"), "Marko Petrović", "065123456", "user", "EUR"),
        )

    # Seed: Radnici sa slikama
    workers_exist = cur.execute("SELECT COUNT(*) as c FROM workers").fetchone()["c"]
    if workers_exist == 0:
        workers = [
            ("Milan", "Šišanje & Brijanje", "065111222", "slike/milan.jpg"),
            ("Aleksa", "Muški & Ženski", "065333444", "slike/aleksa.jpg"),
            ("Nemanja", "Boja & Frizure", "065555666", "slike/nemanja.jpg"),
            ("Miloš", "Šišanje", "065777888", "slike/milos.jpg"),
        ]
        for w in workers:
            cur.execute(
                "INSERT INTO workers (name, specialty, phone, image_path) VALUES (?, ?, ?, ?)", w
            )

    # Seed: AI FAQ
    faq_exists = cur.execute("SELECT COUNT(*) as c FROM ai_faq").fetchone()["c"]
    if faq_exists == 0:
        faqs = [
            ("Kako da se registrujem?", "Kliknite na 'Registracija' dugme na početnoj stranici, unesite korisničko ime, lozinku i osnovne informacije. Tada ćete moći da koristite aplikaciju.", "registracija"),
            ("Kako da zakaživam termin?", "1. Prijavite se na aplikaciju\n2. Kliknite na 'Zakaži termin'\n3. Odaberite frizera\n4. Odaberite datum i vrijeme iz kalendara\n5. Odaberite uslugu i cijenu\n6. Potrdite termin", "zakazivanje"),
            ("Mogu li da otkazem termin?", "Da, možete da otkazete termin do 24 sata prije zakazanog vremena. Idite na 'Moji termini' i kliknite na 'Otkaži'.", "otkazivanje"),
            ("Kako da preuzimam račun?", "Nakon završenog termina, idite na 'Moji termini', pronađite termin i kliknite na 'Preuzmi račun' dugme.", "racun"),
            ("Koja je razlika između EUR i RSD?", "EUR je evropski eura, a RSD je srpski dinar. Možete da brate valutu u postavkama vašeg profila.", "valuta"),
            ("Šta ako trebam pomoć?", "Kliknite na AI Support chatbot u desnom uglu ekrana. Ako je problem ozbiljniji, kontaktirajte administratora direktno.", "podrska"),
        ]
        for faq in faqs:
            cur.execute(
                "INSERT INTO ai_faq (question, answer, category) VALUES (?, ?, ?)", faq
            )

    conn.commit()
    conn.close()
    print("✅ Baza inicijalizovana - Barber Shop")
