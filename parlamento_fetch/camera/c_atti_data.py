from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info
#estrae tutti gli atti della Camera da una certa data e
# per ogni atto estrae tutti i dettagli


sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery("""
   PREFIX ocd: <http://dati.camera.it/ocd/>
   PREFIX dc: <http://purl.org/dc/elements/1.1/>
   PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
   PREFIX persona: <http://dati.camera.it/ocd/persona>

SELECT DISTINCT ?atto ?date ?title ?creator ?nomeCreator WHERE
{
  ?atto ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
  ?atto a <http://dati.camera.it/ocd/atto> .
  ?atto dc:date ?date .
  ?atto dc:title ?title .
  ?atto creator: ?creator .


  FILTER(substr(?date, 1, 8) >= '20110101')
} LIMIT 100
""")

sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

for result in results["results"]["bindings"]:
    print('\n')
    print("Atto:" + result["atto"]["value"])
    print("Title:" + result["title"]["value"])
    print("Data:" + result["date"]["value"])
    print("creatore:" + result["creator"]["value"])
    # print("NomeCreatore:" + result["nomeCreator"]["value"])

    #dettagli delle leggi
    print('\n Legge Detail:')
    legge_detail = "SELECT DISTINCT ?p ?v WHERE {<" + result["atto"]["value"] + "> ?p ?v}"


    sparql.setQuery(legge_detail)
    sparql.setReturnFormat(JSON)
    detail_results = sparql.query().convert()

    for detail in detail_results["results"]["bindings"]:
        print(detail["p"]["value"] + " : " + detail["v"]["value"])



