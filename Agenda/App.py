from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

# Percorso per il file JSON che contiene gli eventi
EVENTI_FILE = "eventi.json"

# Funzione per caricare gli eventi dal file JSON
def carica_eventi():
    if not os.path.exists(EVENTI_FILE):
        return []
    with open(EVENTI_FILE, "r") as file:
        eventi = json.load(file)

        # Aggiungi un controllo per evitare errori nella conversione
        for evento in eventi:
            try:
                # Prova a fare la conversione della data nel formato giusto
                evento['data_inizio'] = datetime.strptime(evento['data_inizio'], "%Y-%m-%dT%H:%M")
                evento['data_fine'] = datetime.strptime(evento['data_fine'], "%Y-%m-%dT%H:%M")
            except ValueError:
                # Se la conversione fallisce, lascia la data come stringa o logga l'errore
                print(f"Errore nel formato della data per l'evento: {evento['titolo']}")
                evento['data_inizio'] = evento.get('data_inizio', '')
                evento['data_fine'] = evento.get('data_fine', '')
        
        return eventi

# Funzione per salvare gli eventi nel file JSON
def salva_eventi(eventi):
    with open(EVENTI_FILE, "w") as file:
        json.dump(eventi, file, default=str)

# Funzione per salvare un nuovo evento
def salva_nuovo_evento(titolo, data_inizio, data_fine, luogo, priorita):
    evento = {
        'titolo': titolo,
        'data_inizio': datetime.strptime(data_inizio, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M"),
        'data_fine': datetime.strptime(data_fine, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M"),
        'luogo': luogo,
        'priorita': priorita
    }
    eventi = carica_eventi()
    eventi.append(evento)
    salva_eventi(eventi)


# Route per la pagina principale
@app.route("/")
def index():
    eventi = carica_eventi()  
    # Passa gli eventi al template
    return render_template("index.html", eventi=eventi)

# Route per aggiungere un evento
@app.route("/aggiungi", methods=["POST"])
def aggiungi_evento():
    titolo = request.form.get("titolo")
    data_inizio = request.form["data_inizio"]
    data_fine = request.form["data_fine"]
    luogo = request.form["luogo"]
    priorita = request.form["priorita"]

    salva_nuovo_evento(titolo, data_inizio, data_fine, luogo, priorita)

    # Ritorna alla pagina principale
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
