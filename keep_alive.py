from flask import Flask
from threading import Thread
import os  # <-- Ajout pour récupérer le port

app = Flask('')

@app.route('/')
def home():
    return "Je suis en Ligne"

def run():
    port = int(os.getenv("PORT", 8080))  # <-- Utilise le port défini par Render
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
