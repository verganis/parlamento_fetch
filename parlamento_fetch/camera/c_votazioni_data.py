from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info
from unicodedata import normalize

#estrae tutte le sedute e votazioni di un certo giorno
# per ogni votazione estrae tutti i singoli voti

today = "20110203"

querystring = """

PREFIX seduta: <http://dati.camera.it/ocd/seduta/>
PREFIX legislatura: <http://dati.camera.it/ocd/legislatura.rdf/>

SELECT  ?date ?seduta ?titlevotazione ?idvotazione ?votazione ?presenti ?votanti ?magg ?favorevoli ?contrari ?ast ?approvato
FROM <http://dati.camera.it/ocd/>
WHERE {
?seduta a ocd:seduta .
?seduta ocd:rif_leg legislatura:repubblica_16 .
?seduta dc:date	?date.

?votazione a ocd:votazione.
?votazione ocd:rif_seduta ?seduta.
?votazione dc:title ?titlevotazione.
?votazione dc:identifier ?idvotazione.
?votazione ocd:votanti ?votanti.
?votazione ocd:favorevoli ?favorevoli.
?votazione ocd:contrari ?contrari.
?votazione ocd:astenuti ?ast.
?votazione ocd:presenti ?presenti.
?votazione ocd:maggioranza ?magg.
?votazione ocd:approvato ?approvato.

FILTER(str(?date) = '%s').
}
""" % (today)

sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery(querystring)

sparql.setReturnFormat(JSON)
try:
    results = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)

for result in results["results"]["bindings"]:
    #dettagli delle votazioni
    votazione_detail = """
                       SELECT ?voto ?titleVoto ?tipo
                       WHERE {
                        ?voto a ocd:voto.
                        ?voto ocd:rif_votazione ?rv.
                        ?voto dc:title ?titleVoto.
                        ?voto dc:type ?tipo.

                        FILTER(str(?rv) = "%s").
                       }
                       ORDER BY ?tipo

                       """ % (result["votazione"]["value"])

    sparql.setQuery(votazione_detail)
    sparql.setReturnFormat(JSON)
    detail_results = sparql.query().convert()

    #verifica che il n. di astenuti/contrari/ favorevoli/ assenti ed astenuti
    # coincida col valore presente nel record votazione corrispondente
    votazione_control = """
                      SELECT ?tipo COUNT(?tipo )AS ?ctipo
                        WHERE
                        {
                        ?voto a ocd:voto.
                        ?voto ocd:rif_votazione ?rv.
                        ?voto dc:type ?tipo.
                        FILTER(str(?rv) = "%s").
                        }
                        GROUP BY ?tipo
                       """ % (result["votazione"]["value"])

    sparql.setQuery(votazione_control)
    sparql.setReturnFormat(JSON)
    control_results = sparql.query().convert()

    try:
        for detail in detail_results["results"]["bindings"]:
            s = u"%s: %s" % (detail["voto"]["value"], detail["titleVoto"]["value"])
            #normalize('NFKD', s).encode('ASCII', 'ignore')
            print(s)
    except  UnicodeEncodeError, err:
        error(err)


    print("\nSeduta di riferimento:" + result["seduta"]["value"])
    print("Valori nel record VOTAZIONE")
    print("Titolo della votazione:" + result["titlevotazione"]["value"])
    print("ID della votazione:" + result["idvotazione"]["value"])
    print("Data:" + result["date"]["value"])
    print("Votanti:" + result["votanti"]["value"])
    print("Favorevoli:" + result["favorevoli"]["value"])
    print("Contrari:" + result["contrari"]["value"])
    print("Astenuti:" + result["ast"]["value"])
    print("Maggioranza:" + result["magg"]["value"])
    print("Approvato:" + result["approvato"]["value"])


    print("\nValori calcolati dai voti dei Deputati")
    for control in control_results['results']['bindings']:
        print(control["tipo"]["value"] + ":" + control["ctipo"]["value"])





