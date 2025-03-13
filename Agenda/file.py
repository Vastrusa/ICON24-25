# file.py
from ontologia_grafo import g  # Importa il grafo dal file ontologia.py

# Definisci la query SPARQL
query = """
    SELECT ?evento
    WHERE {
        ?evento a <http://www.example.com#EventoRicorrente>.
    }
"""

# Esegui la query
results = g.query(query)

# Stampa i risultati
for row in results:
    print(row.evento)

# Definisci un'altra query
query = """
    SELECT ?evento ?orario
    WHERE {
        ?evento <http://www.example.com#haOrario> ?orario.
    }
"""

# Esegui la seconda query
results = g.query(query)

# Stampa i risultati
if not results:
    print("Nessun risultato trovato.")
else:
    for row in results:
        print(row.evento, row.orario)
