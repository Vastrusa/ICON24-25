import rdflib
from datetime import datetime

# Creiamo il grafo RDF
g = rdflib.Graph()

# Carichiamo l'ontologia OWL
g.parse("Agenda.owl", format="xml")

# Funzione per aggiungere un evento all'ontologia
def aggiungi_evento(titolo, data_inizio, data_fine, luogo, priorita, utente):
    print("Funzione aggiungi_evento chiamata")
    evento_uri = rdflib.URIRef(f"http://www.example.com#{titolo}")
    orario_uri = rdflib.URIRef(f"http://www.example.com#{titolo}_orario")
    luogo_uri = rdflib.URIRef(f"http://www.example.com#{luogo}")
    utente_uri = rdflib.URIRef(f"http://www.example.com#{utente}")

    # Aggiungi le informazioni sull'evento
    g.add((evento_uri, rdflib.RDFS.label, rdflib.Literal(titolo)))
    g.add((evento_uri, rdflib.RDF.type, rdflib.URIRef("http://www.example.com#EventoRicorrente")))
    g.add((evento_uri, rdflib.URIRef("http://www.example.com#dataInizio"), rdflib.Literal(data_inizio)))
    g.add((evento_uri, rdflib.URIRef("http://www.example.com#dataFine"), rdflib.Literal(data_fine)))
    g.add((evento_uri, rdflib.URIRef("http://www.example.com#haOrario"), orario_uri))
    g.add((evento_uri, rdflib.URIRef("http://www.example.com#haLuogo"), luogo_uri))
    g.add((evento_uri, rdflib.URIRef("http://www.example.com#haUtente"), utente_uri))
    g.add((orario_uri, rdflib.RDFS.label, rdflib.Literal(f"{data_inizio} - {data_fine}")))
    g.add((luogo_uri, rdflib.RDFS.label, rdflib.Literal(luogo)))
    g.add((utente_uri, rdflib.RDFS.label, rdflib.Literal(utente)))
    
    # Salva il grafo con il nuovo evento
    g.serialize("Agenda.owl", format="xml")

# Funzione per ottenere gli eventi del mese corrente
def eventi_mese_corrente():
    oggi = datetime.today()
    mese_corrente = oggi.month
    anno_corrente = oggi.year

    query = """
        SELECT ?evento ?data_inizio ?data_fine
        WHERE {
            ?evento a <http://www.example.com#EventoRicorrente> .
            ?evento <http://www.example.com#dataInizio> ?data_inizio .
            ?evento <http://www.example.com#dataFine> ?data_fine .
            FILTER (MONTH(?data_inizio) = %d && YEAR(?data_inizio) = %d)
        }
    """ % (mese_corrente, anno_corrente)
    
    results = g.query(query)
    eventi = []
    for row in results:
        eventi.append({
            'evento': row.evento,
            'data_inizio': row.data_inizio,
            'data_fine': row.data_fine
        })
    return eventi

