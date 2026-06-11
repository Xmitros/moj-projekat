# 🏆 BARBER SHOP - HIGH END APLIKACIJA

Profesionalna web aplikacija za upravljanje barberskim salonom sa premium dizajnom i modernim funkcionalnostima.

---

## ✨ Glavne Osobine

### 👨‍💼 Za Korisnika
- ✅ Registracija i login
- ✅ Pregled svih barber-a sa slikama i specijalizacijama (Milan, Aleksa, Nemanja, Miloš)
- ✅ Interaktivni kalendar za zakazivanje (zeleno = slobodno, crveno = zauzeto)
- ✅ Izbor usluge i cijene
- ✅ Izbor valute (EUR ili RSD)
- ✅ Pregled svojih termina sa statusom
- ✅ Otkazivanje termina
- ✅ Preuzimanje PDF računa
- ✅ AI Chatbot podrška (često postavljana pitanja)

### 👨‍💼 Za Administratora
- ✅ Premium dashboard sa KPI karticama
- ✅ Upravljanje barber-ima i njihovim slikama
- ✅ **Odmori barber-a sa startnim i krajnjim datumom**
- ✅ Pregled svih termina sa pretragom
- ✅ Notifikacije sa crvenim kruživima (kao mobilna app)
- ✅ Sistem pomoći - "Help requests" sa admin interfaceom
- ✅ PDF profit izvještaji

---

## 🎨 Dizajn

- **Tema**: Crno-bijela (premium, moderno)
- **Font**: Calibri (sav tekst)
- **Ikone**: Custom ikone (bez emoji-ja)
- **Logo**: Barber Shop logo (crno-bijela verzija)
- **HTTPS**: Podrška za siguran protokol

---

## 🚀 Pokretanje

### 1. Instaliraj zavisnosti
```bash
cd barber
pip install -r requirements.txt
```

### 2. Pokreni aplikaciju
```bash
python3 app.py
```

### 3. Otvori u browser-u
```
https://localhost:5000
```

---

## 👥 Demo Nalozi

| Uloga | Korisničko ime | Lozinka |
|-------|---|---|
| Admin | `admin` | `admin123` |
| Korisnik | `korisnik` | `korisnik123` |

---

## 📁 Struktura Projekta

```
barber/
├── app.py                  # Glavni pokretač
├── database.py             # SQLite + inicijalizacija
├── requirements.txt        # Zavisnosti
├── routes/
│   ├── auth.py            # Login/Registracija
│   ├── user.py            # Korisničke stranice
│   ├── admin.py           # Admin panel
│   ├── api.py             # Calendar API
│   └── chatbot.py         # AI Chatbot
├── static/
│   ├── css/
│   │   └── style.css      # Premium CSS
│   ├── js/
│   │   └── chatbot.js     # Chatbot logika
│   └── slike/
│       ├── milan.jpg      # Barber Milan
│       ├── aleksa.jpg     # Barber Aleksa
│       ├── nemanja.jpg    # Barber Nemanja
│       ├── milos.jpg      # Barber Miloš
│       └── logo.png       # Barber Shop Logo
├── templates/
│   ├── base.html          # Layout
│   ├── index.html         # Početna stranica
│   ├── login.html         # Login/Registracija
│   ├── user/
│   │   ├── home.html      # Odabir barber-a
│   │   ├── schedule.html  # Zakazivanje
│   │   ├── appointments.html # Moji termini
│   │   └── profile.html   # Profil
│   └── admin/
│       ├── dashboard.html # Admin dashboard
│       ├── workers.html   # Upravljanje barber-ima
│       ├── worker_leaves.html # Odmori
│       ├── appointments.html # Svi termini
│       ├── notifications.html # Notifikacije
│       └── help_requests.html # Help zahtjevi
└── data/
    └── barber.db          # SQLite baza (auto-kreira se)
```

---

## 🤖 AI Chatbot

Chatbot automatski odgovara na:
- Kako se registrovati?
- Kako zakazati termin?
- Kako otkazati termin?
- Kako preuzeti račun?
- Koje valute su dostupne?
- Kako kontaktirati podršku?
- I još mnogo toga...

---

## 🔐 Sigurnost

- ✅ HTTPS podrška
- ✅ Heširanje lozinki (SHA256)
- ✅ Session management
- ✅ CSRF zaštita

---

## 📊 Baza Podataka

**Tabele:**
- `users` - Korisnici sa rolama
- `workers` - Barber-i sa slikama
- `appointments` - Zakazani termini
- `worker_leaves` - **Odmori sa start/end datumima**
- `admin_notifications` - Notifikacije
- `ai_faq` - AI Chatbot FAQ

---

## 🎯 Barber-i

1. **Milan** - Šišanje & Brijanje
2. **Aleksa** - Muški & Ženski
3. **Nemanja** - Boja & Frizure
4. **Miloš** - Šišanje

---

## 💳 Valute

- EUR (Evropski Eura)
- RSD (Srpski Dinar)

Korisnik i admin mogu da biraju valutu.

---

*Napravljena sa ❤️ za premium barber salon iskustvo*
