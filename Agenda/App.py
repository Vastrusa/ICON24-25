from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import rdflib
from rdflib.namespace import RDF, RDFS, URIRef
import os
import calendar
from dateutil.relativedelta import relativedelta
import uuid

app = Flask(__name__)

#Percorso per il file OWL che contiene gli eventi
EVENTI_FILE = "Agenda.owl"

#Funzione per caricare l'ontologia
def carica_eventi():
    g = rdflib.Graph()
    g.parse(EVENTI_FILE, format='xml')

    #Esegui una query SPARQL per ottenere gli eventi
    query = """
    SELECT ?titolo ?data_inizio ?data_fine ?luogo ?priorita ?ricorrenza ?data_fine_ricorrenza
    WHERE {
        ?evento rdf:type <http://example.org/Evento> . 
        ?evento <http://example.org/titolo> ?titolo .
        ?evento <http://example.org/data_inizio> ?data_inizio .
        ?evento <http://example.org/data_fine> ?data_fine .
        ?evento <http://example.org/luogo> ?luogo .
        ?evento <http://example.org/priorita> ?priorita .
        ?evento <http://example.org/ricorrenza> ?ricorrenza .
        OPTIONAL { ?evento <http://example.org/data_fine_ricorrenza> ?data_fine_ricorrenza . }
    }
    """
    risultati = g.query(query)
    eventi = []

    for r in risultati:
        evento = {
            'titolo': str(r.titolo),
            'data_inizio': str(r.data_inizio),
            'data_fine': str(r.data_fine),
            'luogo': str(r.luogo),
            'priorita': str(r.priorita),
            'ricorrenza': str(r.ricorrenza),
            'data_fine_ricorrenza': str(r.data_fine_ricorrenza) if r.data_fine_ricorrenza else None
        }
        eventi.append(evento)

        #Aggiungi gli eventi ricorrenti se ci sono
        if r.ricorrenza:
            eventi_ricorrenti = genera_eventi_ricorrenti(evento, g)
            eventi.extend(eventi_ricorrenti)

    return eventi

#Funzione per aggiungere un nuovo evento nell'ontologia
def salva_nuovo_evento(titolo, data_inizio, data_fine, luogo, priorita, ricorrenza, data_fine_ricorrenza):
    g = rdflib.Graph()
    g.parse(EVENTI_FILE, format='xml')
    
    evento_uri = URIRef(f"http://example.org/{titolo}")
    evento = URIRef("http://example.org/Evento")
    
    # Aggiungi i dati dell'evento
    g.add((evento_uri, RDF.type, evento))
    g.add((evento_uri, URIRef("http://example.org/titolo"), rdflib.Literal(titolo)))
    g.add((evento_uri, URIRef("http://example.org/data_inizio"), rdflib.Literal(data_inizio)))
    g.add((evento_uri, URIRef("http://example.org/data_fine"), rdflib.Literal(data_fine)))
    g.add((evento_uri, URIRef("http://example.org/luogo"), rdflib.Literal(luogo)))
    g.add((evento_uri, URIRef("http://example.org/priorita"), rdflib.Literal(priorita)))
    g.add((evento_uri, URIRef("http://example.org/ricorrenza"), rdflib.Literal(ricorrenza)))
    g.add((evento_uri, URIRef("http://example.org/data_fine_ricorrenza"), rdflib.Literal(data_fine_ricorrenza)))  
    if data_fine_ricorrenza:
        g.add((evento_uri, URIRef("http://example.org/data_fine_ricorrenza"), rdflib.Literal(data_fine_ricorrenza)))
    
    #Salva l'ontologia aggiornata
    g.serialize(EVENTI_FILE, format='xml')

#Funzione per generare eventi ricorrenti e aggiungerli all'ontologia
def genera_eventi_ricorrenti(evento, g):
    eventi_ricorrenti = []
    #Otteniamo i dati dell'evento
    data_inizio = datetime.strptime(evento['data_inizio'], "%Y-%m-%dT%H:%M")
    data_fine = datetime.strptime(evento['data_fine'], "%Y-%m-%dT%H:%M")
    ricorrenza = evento['ricorrenza']
    data_fine_ricorrenza = datetime.strptime(evento['data_fine_ricorrenza'], "%Y-%m-%dT%H:%M")
    giorno_mese_iniziale = data_inizio.day
    
    #Ricorrenza Giornaliera
    if ricorrenza == 'giornaliera':
        i = 1
        while data_inizio + timedelta(days=i) <= data_fine_ricorrenza:
            nuova_data_inizio = data_inizio + timedelta(days=i)
            nuova_data_fine = data_fine + timedelta(days=i)
            nuovo_evento = evento.copy()
            nuovo_evento['data_inizio'] = nuova_data_inizio.strftime("%Y-%m-%dT%H:%M")
            nuovo_evento['data_fine'] = nuova_data_fine.strftime("%Y-%m-%dT%H:%M")
            
            #Aggiungiamo l'evento ricorrente nell'ontologia
            evento_uri = rdflib.URIRef(f"http://example.org/event/{nuovo_evento['titolo'].replace(' ', '_')}")
            g.add((evento_uri, rdflib.RDF.type, rdflib.URIRef("http://example.org/Event")))
            g.add((evento_uri, rdflib.URIRef("http://example.org/titolo"), rdflib.Literal(nuovo_evento['titolo'])))
            g.add((evento_uri, rdflib.URIRef("http://example.org/data_inizio"), rdflib.Literal(nuovo_evento['data_inizio'])))
            g.add((evento_uri, rdflib.URIRef("http://example.org/data_fine"), rdflib.Literal(nuovo_evento['data_fine'])))
            g.add((evento_uri, rdflib.URIRef("http://example.org/luogo"), rdflib.Literal(nuovo_evento['luogo'])))
            g.add((evento_uri, rdflib.URIRef("http://example.org/priorita"), rdflib.Literal(nuovo_evento['priorita'])))
            g.add((evento_uri, rdflib.URIRef("http://example.org/ricorrenza"), rdflib.Literal(nuovo_evento['ricorrenza'])))

            eventi_ricorrenti.append(nuovo_evento)
            i += 1

    #Ricorrenza Settimanale
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
                
                #Aggiungiamo l'evento ricorrente nell'ontologia
                evento_uri = rdflib.URIRef(f"http://example.org/event/{nuovo_evento['titolo'].replace(' ', '_')}")
                g.add((evento_uri, rdflib.RDF.type, rdflib.URIRef("http://example.org/Event")))
                g.add((evento_uri, rdflib.URIRef("http://example.org/titolo"), rdflib.Literal(nuovo_evento['titolo'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/data_inizio"), rdflib.Literal(nuovo_evento['data_inizio'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/data_fine"), rdflib.Literal(nuovo_evento['data_fine'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/luogo"), rdflib.Literal(nuovo_evento['luogo'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/priorita"), rdflib.Literal(nuovo_evento['priorita'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/ricorrenza"), rdflib.Literal(nuovo_evento['ricorrenza'])))

                eventi_ricorrenti.append(nuovo_evento)
            i += 1

    #Ricorrenza Mensile
    elif ricorrenza == 'mensile':
        i = 1
        while data_inizio + relativedelta(months=i) <= data_fine_ricorrenza:
            nuova_data_inizio = data_inizio + relativedelta(months=i)
            nuova_data_fine = data_fine + relativedelta(months=i)

            if nuova_data_inizio <= data_fine_ricorrenza:
                nuovo_evento = evento.copy()
                nuovo_evento['data_inizio'] = nuova_data_inizio.strftime("%Y-%m-%dT%H:%M")
                nuovo_evento['data_fine'] = nuova_data_fine.strftime("%Y-%m-%dT%H:%M")

                #Genera un ID univoco per l'evento ricorrente
                evento_id = str(uuid.uuid4())
                evento_uri = rdflib.URIRef(f"http://example.org/event/{evento_id}")

                #Aggiungiamo l'evento ricorrente nell'ontologia
                g.add((evento_uri, rdflib.RDF.type, rdflib.URIRef("http://example.org/Event")))
                g.add((evento_uri, rdflib.URIRef("http://example.org/titolo"), rdflib.Literal(nuovo_evento['titolo'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/data_inizio"), rdflib.Literal(nuovo_evento['data_inizio'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/data_fine"), rdflib.Literal(nuovo_evento['data_fine'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/luogo"), rdflib.Literal(nuovo_evento['luogo'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/priorita"), rdflib.Literal(nuovo_evento['priorita'])))
                g.add((evento_uri, rdflib.URIRef("http://example.org/ricorrenza"), rdflib.Literal(nuovo_evento['ricorrenza'])))

                eventi_ricorrenti.append(nuovo_evento)
            i += 1

    return eventi_ricorrenti

  #Salva l'ontologia aggiornata
    g.serialize(EVENTI_FILE, format='xml')
    
#Funzione per eliminare un evento dall'ontologia
def elimina_evento(titolo):
    g = rdflib.Graph()
    g.parse(EVENTI_FILE, format='xml')
    
    evento_uri = URIRef(f"http://example.org/{titolo}")
    
    #Rimuovi l'evento
    g.remove((evento_uri, None, None))
    
    #Salva l'ontologia aggiornata
    g.serialize(EVENTI_FILE, format='xml')

#Route per la pagina principale
@app.route("/")
def index():
    eventi = carica_eventi()  
    # Passa gli eventi al template
    return render_template("index.html", eventi=eventi)

#Route per aggiungere un evento
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

#Route per eliminare un evento
@app.route("/elimina", methods=["POST"])
def elimina():
    titolo = request.form.get("titolo")
    elimina_evento(titolo)

 #Ritorna alla pagina principale
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
