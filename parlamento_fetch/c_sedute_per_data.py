from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info
#estrae tutti gli atti della Camera da una certa data e
# per ogni atto estrae tutti i dettagli

querystring = """PREFIX seduta: <http://dati.camera.it/ocd/seduta/>
        PREFIX legislatura: <http://dati.camera.it/ocd/legislatura.rdf/>

        SELECT DISTINCT ?seduta ?date
        FROM <http://dati.camera.it/ocd/>
        WHERE {
        ?seduta a ocd:seduta .
        ?seduta ocd:rif_leg legislatura:repubblica_16 .
        ?seduta dc:date	?date.
        FILTER(str(?date) = '20121111').
        }
        ORDER BY ?date
        """

sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery(querystring)

sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

for result in results["results"]["bindings"]:
    print("seduta:" + result["seduta"]["value"])
    print("Data:" + result["date"]["value"])





