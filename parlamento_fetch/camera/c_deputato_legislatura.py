


from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info


sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery("""
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
PREFIX persona: <http://dati.camera.it/ocd/persona>
PREFIX deputato: <http://dati.camera.it/ocd/deputato.rdf/>


SELECT ?a ?b ?c WHERE
{
?a a <http://dati.camera.it/ocd/deputato> .
?a <http://dati.camera.it/ocd/rif_leg> <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
?a ?b ?c

}
""")

sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

for result in results["results"]["bindings"]:
    print('\n')
    print("id_deputato:" + result["a"]["value"])
    print(result["b"]["value"] + ":" + result["c"]["value"] )





