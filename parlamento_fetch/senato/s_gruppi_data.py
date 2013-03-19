# PREFIX osr: <http://dati.senato.it/osr/>
# PREFIX ocd: <http://dati.camera.it/ocd/>
# select distinct ?name ?surname ?gruppo ?datafine ?datainizio
# where
# {
# ?senatore a osr:Senatore.
# ?senatore foaf:firstName ?name.
# ?senatore foaf:lastName ?surname.
# ?senatore ocd:aderisce ?adesione.
#
# ?adesione a ocd:adesioneGruppo.
# ?adesione osr:inizio ?datainizio.
# ?adesione osr:fine ?datafine.
# ?adesione osr:legislatura ?leg.
# ?adesione osr:gruppo ?gruppo.
# #
# # ?gruppo osr:denominazione ?denominazione.
# # ?gruppo osr:dataCostituzione ?datac.
# # ?gruppo osr:dataCostituzione ?datac.
# # ?denominazione osr:titolo ?nomegruppo.
#
# FILTER(?leg=16).
# FILTER(str(?datafine) > '%s').
# FILTER(str(?datainizio) <= '%s')
# }
#
# ORDER BY ?surname


from SPARQLWrapper import SPARQLWrapper, JSON

#senatori attivi al tal giorno, non include il nome del gruppo x esteso perche' attualmente
# da' luogo a risultati ripetuti

day = "2012-03-15"

sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")

sparql.setQuery("""
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select distinct ?name ?surname ?gruppo ?datafine ?datainizio
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


FILTER(?leg=16).
FILTER(str(?datafine) > '%s').
FILTER(str(?datainizio) <= '%s')
}

ORDER BY ?surname
""" % (day, day))

sparql.setReturnFormat(JSON)
results = sparql.query().convert()


for result in results["results"]["bindings"]:

    # ?name ?surname ?nomegruppo ?datafine ?datainizio
    print "%s - %s " % (result["name"]['value'], result["surname"]['value'],)
    print "%s (%s - %s)" % (result["gruppo"]['value'], result["datafine"]['value'], result["datainizio"]['value'],)


