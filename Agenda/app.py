from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Lista di eventi
eventi = []

# Funzione per aggiungere un evento
def aggiungi_evento(titolo, data_inizio, data_fine, luogo, priorita):
    evento = {
        'titolo': titolo,
        'data_inizio': data_inizio,
        'data_fine': data_fine,
        'luogo': luogo,
        'priorita': priorita
    }
    eventi.append(evento)

# Funzione per ottenere gli eventi del mese corrente
def eventi_mese_corrente():
    # Qui puoi filtrare gli eventi per il mese corrente
    return eventi

# Route per la pagina principale
@app.route("/")
def index():
    # Passa gli eventi al template
    return render_template("index.html", eventi=eventi)

# Route per aggiungere un evento
@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    # Prendi i dati dal form
    titolo = request.form["titolo"]
    data_inizio = request.form["data_inizio"]
    data_fine = request.form["data_fine"]
    luogo = request.form["luogo"]
    priorita = request.form["priorita"]
    
    # Aggiungi l'evento
    aggiungi_evento(titolo, data_inizio, data_fine, luogo, priorita)
    
    # Ritorna alla pagina principale
    return redirect(url_for("index"))

# Route per la visualizzazione degli eventi del mese
@app.route("/eventi_mese")
def eventi_mese():
    # Ottieni gli eventi del mese corrente
    eventi_del_mese = eventi_mese_corrente()
    
    # Passa gli eventi del mese al template
    return render_template("index.html", eventi=eventi_del_mese)

if __name__ == "__main__":
    app.run(debug=True)
