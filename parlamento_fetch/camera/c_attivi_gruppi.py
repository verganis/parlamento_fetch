

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info


sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery("""
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT DISTINCT ?name ?surname ?nomegruppo  ?dateade
WHERE
{
?item a ocd:deputato.
?item ocd:aderisce ?ade.
?ade dc:date ?dateade.
OPTIONAL{

?item foaf:firstName ?name.
?item foaf:surname ?surname.
}
?item ocd:rif_incarico ?incarico.
?incarico ocd:rif_gruppoParlamentare ?gruppo.
?gruppo dc:title ?nomegruppo.

}
ORDER BY ?surname

""")


sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

for result in results["results"]["bindings"]:
    print('\n')
    print(result["name"]["value"] + " " + result["surname"]["value"] + " - " + result["nomegruppo"]["value"] + " - " + result["date"]["value"])






