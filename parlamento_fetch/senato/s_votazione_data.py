from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info

#estrae tutti i voti di una votazione

nvotazione = "13-1055-1"

querystring = """
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select distinct ?votazione ?label ?favorevoli ?contrari ?astenuti ?presenti ?missione ?maggioranza ?nlegale ?esito
where
{
?votazione a osr:Votazione.
?votazione osr:favorevoli ?favorevoli.
?votazione osr:contrari ?contrari.
?votazione osr:astenuti ?astenuti.
?votazione osr:inCongedoMissione ?missione.
?votazione osr:presenti ?presenti.
?votazione osr:maggioranza ?maggioranza.
?votazione osr:numeroLegale ?nlegale.
?votazione osr:esito ?esito.
?votazione rdfs:label ?label.
FILTER(str(?votazione)='http://dati.senato.it/votazione/%s')
}

""" % nvotazione

sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")
sparql.setQuery(querystring)
sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

result = results["results"]["bindings"][0]
print("\nVotazione:" + nvotazione)
print("Valori numerici del record")
print("Titolo della votazione:" + result["label"]["value"])
print("Presenti:"+ result["presenti"]["value"])
print("Favorevoli:" + result["favorevoli"]["value"])
print("Contrari:" + result["contrari"]["value"])
print("Astenuti:"+ result["astenuti"]["value"])
print("In missione:" + result["missione"]["value"])
print("n.legale:"+ result["nlegale"]["value"])
print("Maggioranza:"+ result["maggioranza"]["value"])
print("Esito:" + result["esito"]["value"])


print("Valori aggregati")

val_aggregazione = ["favorevole", "contrario", "astenuto", "inCongedoMissione" ]

for val in val_aggregazione:
    query_aggregazione = """
    PREFIX osr: <http://dati.senato.it/osr/>
    PREFIX ocd: <http://dati.camera.it/ocd/>
    select COUNT(?%s) as ?%s
    where
    {
    ?votazione a osr:Votazione.
    ?votazione osr:%s ?%s.
    FILTER(str(?votazione)='http://dati.senato.it/votazione/%s').
    }
    """ % (val, val, val, val, nvotazione)

    sparql.setQuery(query_aggregazione)
    sparql.setReturnFormat(JSON)
    try:
        results_aggregazione = sparql.query().convert()
    except EndPointNotFound, err:
        print(query_aggregazione)
        error(err)
        sys.exit(1)

    result_aggregazione = results_aggregazione["results"]["bindings"][0][val]["value"]

    print(val + ":" + result_aggregazione)





