from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os
import calendar
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

#Percorso per il file JSON che contiene gli eventi
EVENTI_FILE = "eventi.json"

#Funzione per caricare gli eventi dal file JSON
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
                
        eventi_espansi = []
        for evento in eventi:
            if 'ricorrenza' in evento and evento['ricorrenza'] != 'no' and evento.get('data_fine_ricorrenza'):
                eventi_espansi.extend(genera_eventi_ricorrenti(evento))
            else:
                eventi_espansi.append(evento)

        return eventi_espansi
def genera_eventi_ricorrenti(evento):
    eventi_ricorrenti = []
    data_inizio = evento['data_inizio']
    data_fine = evento['data_fine']
    ricorrenza = evento['ricorrenza']
    data_fine_ricorrenza = datetime.strptime(evento['data_fine_ricorrenza'], "%Y-%m-%dT%H:%M")
    giorno_mese_iniziale = data_inizio.day

    if ricorrenza == 'giornaliera':
        i = 1
        while data_inizio + timedelta(days=i) <= data_fine_ricorrenza:
            nuova_data_inizio = data_inizio + timedelta(days=i)
            nuova_data_fine = data_fine + timedelta(days=i)
            nuovo_evento = evento.copy()
            nuovo_evento['data_inizio'] = nuova_data_inizio.strftime("%Y-%m-%dT%H:%M")
            nuovo_evento['data_fine'] = nuova_data_fine.strftime("%Y-%m-%dT%H:%M")
            eventi_ricorrenti.append(nuovo_evento)
            i += 1
    elif ricorrenza == 'settimanale':
        giorno_settimana_iniziale = data_inizio.weekday()
        i = 1
        while data_inizio + timedelta(weeks=i) <= data_fine_ricorrenza:
            nuova_data_inizio = data_inizio + timedelta(weeks=i)
            nuova_data_inizio = nuova_data_inizio + timedelta(days=(giorno_settimana_iniziale - nuova_data_inizio.weekday()))
            nuova_data_fine = data_fine + timedelta(weeks=i)
            nuova_data_fine = nuova_data_fine + timedelta(days=(giorno_settimana_iniziale - nuova_data_fine.weekday()))
            if nuova_data_inizio <= data_fine_ricorrenza:
                nuovo_evento = evento.copy()
                nuovo_evento['data_inizio'] = nuova_data_inizio.strftime("%Y-%m-%dT%H:%M")
                nuovo_evento['data_fine'] = nuova_data_fine.strftime("%Y-%m-%dT%H:%M")
                eventi_ricorrenti.append(nuovo_evento)
            i += 1
    elif ricorrenza == 'mensile':
        nuova_data_inizio = data_inizio
        nuova_data_fine = data_fine
        while nuova_data_inizio <= data_fine_ricorrenza:
            nuovo_evento = evento.copy()
            nuovo_evento['data_inizio'] = nuova_data_inizio.strftime("%Y-%m-%dT%H:%M")
            nuovo_evento['data_fine'] = nuova_data_fine.strftime("%Y-%m-%dT%H:%M")
            eventi_ricorrenti.append(nuovo_evento)

            nuova_data_inizio += relativedelta(months=1)
            nuova_data_fine += relativedelta(months=1)

            try:
                nuova_data_inizio = nuova_data_inizio.replace(day=giorno_mese_iniziale)
                nuova_data_fine = nuova_data_fine.replace(day=giorno_mese_iniziale)
            except ValueError:
                nuova_data_inizio = nuova_data_inizio.replace(day=calendar.monthrange(nuova_data_inizio.year, nuova_data_inizio.month)[1])
                nuova_data_fine = nuova_data_fine.replace(day=calendar.monthrange(nuova_data_fine.year, nuova_data_fine.month)[1])

    return eventi_ricorrenti

# Funzione per salvare gli eventi nel file JSON
def salva_eventi(eventi):
    with open(EVENTI_FILE, "w") as file:
        json.dump(eventi, file, default=str)

# Funzione per salvare un nuovo evento
def salva_nuovo_evento(titolo, data_inizio, data_fine, luogo, priorita, ricorrenza, data_fine_ricorrenza):
    evento = {
        'titolo': titolo,
        'data_inizio': datetime.strptime(data_inizio, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M"),
        'data_fine': datetime.strptime(data_fine, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M"),
        'luogo': luogo,
        'priorita': priorita
        'ricorrenza': ricorrenza,
        'data_fine_ricorrenza': datetime.strptime(data_fine_ricorrenza, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M") if data_fine_ricorrenza else None        
    }
    eventi = carica_eventi()
    eventi.append(evento)
    salva_eventi(eventi)

# Funzione per eliminare un evento
def elimina_evento(titolo):
    eventi = carica_eventi()
    eventi = [evento for evento in eventi if evento['titolo'] != titolo]
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
    ricorrenza = request.form["ricorrenza"]
    data_fine_ricorrenza = request.form.get("data_fine_ricorrenza")

    salva_nuovo_evento(titolo, data_inizio, data_fine, luogo, priorita, ricorrenza, data_fine_ricorrenza)

    # Ritorna alla pagina principale
    return redirect(url_for("index"))

# Route per eliminare un evento
@app.route("/elimina", methods=["POST"])
def elimina():
    titolo = request.form.get("titolo")
    elimina_evento(titolo)

 # Ritorna alla pagina principale
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
