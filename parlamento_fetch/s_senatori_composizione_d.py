# a partire da due date verifica le differenze fra i senatori in carica a data1 e data2 e salva due file
# AAAAMMGG-senatori_added e AAAAMMGG-senatori_removed con le differenze

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import logging
from logging import debug, error, info
from utils.sparql import *




outputfolder = "/home/nishant/workspace/parlamento_fetch/parlamento_fetch/output"
today = "2013-03-13"
last_update = "2010-05-06"

senatori_added = []
senatori_removed = []

# sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")

query_composizione = """
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select distinct ?senatore ?name ?surname ?gruppo ?datafine ?datainizio
where
{
?senatore a osr:Senatore.
?senatore foaf:firstName ?name.
?senatore foaf:lastName ?surname.
?senatore ocd:aderisce ?adesione.

?adesione a ocd:adesioneGruppo.
?adesione osr:inizio ?datainizio.
?adesione osr:fine ?datafine.
?adesione osr:legislatura ?leg.
?adesione osr:gruppo ?gruppo.

FILTER(str(?datafine) > '%s').
FILTER(str(?datainizio) <= '%s')
}

ORDER BY ?surname
LIMIT 5
"""

query_composizione_today = query_composizione % (today, today)
query_composizione_lastupdate = query_composizione % (last_update, last_update)

fields = ["senatore","name","surname", "gruppo", "datafine", "datainizio"]
results = run_query("http://dati.senato.it/sparql-query", query_composizione_today, fields )



# sparql.setQuery(query_composizione_today)
# sparql.setReturnFormat(JSON)
# results_today = sparql.query().convert()

# sparql.setQuery(query_composizione_lastupdate)
# sparql.setReturnFormat(JSON)
# results_last_update = sparql.query().convert()
#
# for senatore in results_today["results"]["bindings"]:
#     #trova i senatori aggiunti
#     trovato = False
#     for senatore_last in results_last_update["results"]["bindings"]:
#         if senatore["senatore"]["value"] == senatore_last["senatore"]["value"]:
#             trovato = True
#             break
#     if not trovato:
#         senatori_added.append(senatore)
#
#
# for senatore in results_last_update["results"]["bindings"]:
#
#     #trova i senatori rimossi
#     trovato = False
#     for senatore_today in results_today["results"]["bindings"]:
#         if senatore["senatore"]["value"] == senatore_today["senatore"]["value"]:
#             trovato = True
#             break
#     if not trovato:
#         senatori_removed.append(senatore)
#
#
#
# # stampa senatori aggiunti
#
# print "\nSENATORI AGGIUNTI tra %s e %s \n" %( last_update, today)
# for result in senatori_added:
#     print "%s - %s - %s - %s (%s - %s)" \
#           % (result["senatore"]['value'],
#              result["name"]['value'],
#              result["surname"]['value'],
#              result["gruppo"]['value'],
#              result["datafine"]['value'],
#              result["datainizio"]['value'])
#
#
# # stampa senatori rimossi
#
# print"\nSENATORI RIMOSSI tra %s e %s \n" %( last_update, today)
# for result in senatori_removed:
#     print "%s - %s - %s - %s (%s - %s)" \
#           % (result["senatore"]['value'],
#              result["name"]['value'],
#              result["surname"]['value'],
#              result["gruppo"]['value'],
#              result["datafine"]['value'],
#              result["datainizio"]['value'])
#
# # output su file
# outputfile = open( outputfolder +"/"+ today + "_s_composizione_added",'w')
# #stampa i metadati
# for index, variable in enumerate(results_last_update["head"]["vars"]):
#     outputfile.write('"%s"' % variable)
#     if index < len(results_last_update["head"]):
#         outputfile.write(",")
#
#     outputfile.write("\n")
#
# #stampa i valori
# for senatore in senatori_added:
#     for field in senatore:
#         outputfile.write('"%s",' % field)
#
#     outputfile.write("\n")
#
# outputfile.close()

