# ✂ BROS — Frizerski Salon Aplikacija

Potpuna web aplikacija za upravljanje frizerskim salonom, napravljena u Pythonu (Flask).

---

## Pokretanje

### 1. Instaliraj zavisnosti
```bash
pip install Flask reportlab
```

### 2. Pokreni server
```bash
python3 app.py
```

### 3. Otvori u browseru
```
http://localhost:5000
```

---

## Demo nalozi

| Uloga | Korisničko ime | Lozinka |
|-------|---------------|---------|
| Admin | `admin` | `admin123` |
| Korisnik | `korisnik` | `korisnik123` |

---

## Struktura projekta

```
bros_salon/
├── app.py              # Glavni pokretač
├── database.py         # Baza (SQLite) + inicijalizacija
├── requirements.txt    # Zavisnosti
├── routes/
│   ├── auth.py         # Login, registracija, logout
│   ├── user.py         # Korisničke stranice
│   ├── admin.py        # Admin panel
│   └── api.py          # JSON API za kalendar
├── utils/
│   └── pdf_gen.py      # Generisanje PDF-ova
├── templates/
│   ├── base.html       # Zajednički layout
│   ├── login.html      # Login/registracija
│   ├── user/
│   │   ├── home.html       # Odabir frizera
│   │   ├── calendar.html   # Kalendar za zakazivanje
│   │   └── appointments.html # Moji termini
│   └── admin/
│       ├── dashboard.html  # Admin pregled
│       ├── workers.html    # Upravljanje radnicima
│       └── appointments.html # Svi termini
└── data/
    └── bros.db         # SQLite baza (kreira se automatski)
```

---

## Funkcionalnosti

### Korisnik
- ✅ Registracija i login
- ✅ Pregled svih aktivnih frizera
- ✅ Kalendar sa bojama (crvena = zauzeto/odmor, zelena = slobodno)
- ✅ Odabir termina i usluge
- ✅ Pregled mojih termina sa filterima
- ✅ Otkazivanje termina
- ✅ Preuzimanje fiskalnog računa (PDF)
- ✅ Browser notifikacije (podsjetnik)

### Admin
- ✅ Dashboard sa KPI karticama (termini danas, prihod, radnici)
- ✅ Statistike po radniku sa progress bar-om
- ✅ PDF profit izvještaj (po izboru mjeseca)
- ✅ Pregled svih termina sa pretragom
- ✅ Dodavanje novih radnika
- ✅ Uklanjanje/aktivacija radnika
- ✅ Odmori radnika (po datumu, sa razlogom)
- ✅ Napomene za radnike
- ✅ Tabovi i pod-tabovi u panelu radnika

---

## Baza podataka (SQLite)

Tabele:
- `users` — Korisnici (admin/user role)
- `workers` — Radnici (frizeri)
- `appointments` — Termini
- `worker_leaves` — Odmori radnika
- `worker_notes` — Napomene za radnike

---

*Aplikacija koristi: Python 3, Flask, SQLite, ReportLab, Vanilla JS*
