from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info
#estrae tutte le sedute e votazioni di un certo giorno
# per ogni votazione estrae tutti i singoli voti

today = "2011-09-14"

query_votazioni = """
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select ?votazione ?seduta
where
{
?seduta a osr:SedutaAssemblea.
?seduta osr:dataSeduta ?dataSeduta.
?seduta osr:legislatura ?legislatura.

?votazione a osr:Votazione.
?votazione osr:seduta ?seduta.

FILTER(str(?dataSeduta)="%s")

}
ORDER BY ?dataSeduta
""" % today


sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")
sparql.setQuery(query_votazioni)
sparql.setReturnFormat(JSON)
try:
    results_votazioni = sparql.query().convert()
except EndPointNotFound, err:
    error(err)
    sys.exit(1)


# per ogni seduta estrae il numero delle votazioni relative
for votazioni in results_votazioni["results"]["bindings"]:

    nvotazione = votazioni["votazione"]["value"]


    query_votazione = """
    PREFIX osr: <http://dati.senato.it/osr/>
    PREFIX ocd: <http://dati.camera.it/ocd/>
    select distinct ?votazione ?label ?favorevoli ?contrari ?astenuti ?presenti ?missione ?maggioranza ?nlegale ?esito ?votanti
    where
    {
    ?votazione a osr:Votazione.
    ?votazione osr:favorevoli ?favorevoli.
    ?votazione osr:contrari ?contrari.
    ?votazione osr:astenuti ?astenuti.
    ?votazione osr:inCongedoMissione ?missione.
    ?votazione osr:presenti ?presenti.
    ?votazione osr:votanti ?votanti.
    ?votazione osr:maggioranza ?maggioranza.
    ?votazione osr:numeroLegale ?nlegale.
    ?votazione osr:esito ?esito.
    ?votazione rdfs:label ?label.
    FILTER(str(?votazione)='%s')
    }

    """ % nvotazione

    sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")
    sparql.setQuery(query_votazione)
    sparql.setReturnFormat(JSON)
    try:
        results_votazione = sparql.query().convert()
    except EndPointNotFound, err:
        error(err)
        sys.exit(1)

    result_votazione = results_votazione["results"]["bindings"][0]
    print("\nVOTAZIONE:" + nvotazione)
    print("Valori numerici del record")
    print("Titolo della votazione:" + result_votazione["label"]["value"])
    print("Presenti:"+ result_votazione["presenti"]["value"])
    print("Votanti:"+ result_votazione["votanti"]["value"])
    print("Favorevoli:" + result_votazione["favorevoli"]["value"])
    print("Contrari:" + result_votazione["contrari"]["value"])
    print("Astenuti:"+ result_votazione["astenuti"]["value"])
    print("In missione:" + result_votazione["missione"]["value"])
    print("n.legale:"+ result_votazione["nlegale"]["value"])
    print("Maggioranza:"+ result_votazione["maggioranza"]["value"])
    print("Esito:" + result_votazione["esito"]["value"])


    print("\nVALORI AGGREGATI\n")

    val_aggregazione = ["favorevole", "contrario", "astenuto", "inCongedoMissione"]

    for val in val_aggregazione:
        query_aggregazione = """
        PREFIX osr: <http://dati.senato.it/osr/>
        PREFIX ocd: <http://dati.camera.it/ocd/>
        select COUNT(?%s) as ?%s
        where
        {
        ?votazione a osr:Votazione.
        ?votazione osr:%s ?%s.
        FILTER(str(?votazione)='%s').
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





