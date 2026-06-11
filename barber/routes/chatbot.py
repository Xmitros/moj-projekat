"""
AI Chatbot route za Barber Shop
Odgovara na često postavljana pitanja
"""

from flask import Blueprint, request, jsonify, session
from database import get_db
import re

chatbot_bp = Blueprint('chatbot', __name__)

# AI FAQ baza
AI_RESPONSES = {
    'registracija': "Za registraciju: 1) Kliknite 'Registracija' 2) Unesite korisničko ime i lozinku 3) Potrdite. Tada ćete moći pristupiti aplikaciji.",
    'zakazivanje': "Kako zakazati termin:\n1. Prijavite se\n2. Kliknite 'Zakaži termin'\n3. Odaberite frizera\n4. Izaberite datum iz kalendara (zeleno = slobodno)\n5. Odaberite uslugu\n6. Potrdite",
    'otkazivanje': "Termin možete otkazati do 24 sata prije vremena. Idite na 'Moji termini' > Termin > 'Otkaži'",
    'racun': "Račun preuzimate nakon završenog termina: Moji termini > odaberite termin > 'Preuzmi račun (PDF)'",
    'valuta': "U postavkama profila možete izabrati valutu: EUR (Eura) ili RSD (Srpski dinar).",
    'podrska': "Za brza pitanja koristi AI chatbot. Za ozbiljnije probleme, kontaktiraj admin direktno ili koristi 'Pomoć' dugme.",
    'slike': "Slike radnika vidite na početnoj stranici. Svaki frizer ima svoju specijalizaciju i dostupnost.",
    'termin_nemoguc': "Ako datum nije dostupan, to znači da je frizer zauzet ili na odmoru. Odaberite drugi datum.",
    'lozinka': "Lozinku možete resetovati klikom na 'Zaboravljena lozinka' na login stranici.",
    'profile': "U profilu možete promijeniti podatke, valutu i vidjeti sve svoje termine.",
}

def extract_intent(text):
    """Izvuci intenciju iz korisničkog poruke"""
    text_lower = text.lower()
    
    keywords = {
        'registracija': ['registracija', 'registruj', 'sign up', 'novi račun', 'napravi'],
        'zakazivanje': ['zakaži', 'booking', 'termin', 'appointment', 'kada', 'slobodno'],
        'otkazivanje': ['otkaži', 'cancel', 'otkažem'],
        'racun': ['račun', 'invoice', 'preuzmi', 'pdf'],
        'valuta': ['valuta', 'eure', 'dinare', 'novac', 'cijena'],
        'podrska': ['pomoć', 'problem', 'greška', 'support', 'help'],
        'slike': ['slike', 'frizer', 'radnik', 'ko'],
        'termin_nemoguc': ['nije dostupan', 'zauzet', 'odmor', 'ne mogu zakazati'],
        'lozinka': ['lozinka', 'zaboravio', 'reset', 'login'],
        'profile': ['profil', 'podatci', 'informacije', 'moj račun'],
    }
    
    for intent, keywords_list in keywords.items():
        for keyword in keywords_list:
            if keyword in text_lower:
                return intent
    
    return 'general'

@chatbot_bp.route('/ask', methods=['POST'])
def ask_chatbot():
    """
    Endpoint za AI chatbot
    Request: {"message": "Kako da se registrujem?"}
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'Molim unesite pitanje.'
            }), 400
        
        # Izvuci intenciju
        intent = extract_intent(user_message)
        
        # Pronađi odgovor
        response = AI_RESPONSES.get(intent, 
            "Izvinjavam se, nisam siguran. Molim kontaktirajte administratora za detaljnu pomoć.")
        
        # Sacuva u bazu ako je zalogovan korisnik
        if 'user_id' in session:
            conn = get_db()
            conn.execute(
                "INSERT INTO ai_chat_logs (user_id, question, answer, category) VALUES (?, ?, ?, ?)",
                (session['user_id'], user_message, response, intent)
            )
            conn.commit()
            conn.close()
        
        return jsonify({
            'status': 'success',
            'answer': response,
            'category': intent,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@chatbot_bp.route('/faq', methods=['GET'])
def get_faq():
    """Dobij sve FAQ"""
    try:
        conn = get_db()
        faqs = conn.execute("SELECT id, question, answer, category FROM ai_faq ORDER BY category").fetchall()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'faqs': [dict(faq) for faq in faqs]
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Kreiraj tabelu ako ne postoji
def init_chatbot_table():
    """Kreiraj ai_chat_logs tabelu"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_chatbot_table()
