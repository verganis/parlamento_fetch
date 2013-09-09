from utils.sparql_tools import run_query, write_file
import glob, os
from settings_local import *


# controlla le votazioni presenti sul sito del Senato e le confronta con i file gia' salvati
# nell'apposita cartella dati. se sono presenti nuove votazioni genera tre tipi di file:
# * file con tutti i dati della votazione
#  - votazione_LEGISLATURA_NUMEROSEDUTA_NUMEROVOTAZIONE.csv
# * aggiorna il file che mette in relazione la seduta con le relative votazioni
#  - votazioni_LEGISLATURA_NUMEROSEDUTA.csv
# * file con tutti i dati relativi alla seduta, se non e' gia presente
#  - seduta_LEGISLATURA_NUMEROSEDUTA.csv
#  nel caso in cui non si riesca a connettere allo sparql endpoint manda una mail alla lista di admin



# cerco il file che inizia con seduta_legislatura_*.csv e vedo qual e' l'ultima importata
# vedo su sparql qual e' l'ultima seduta presente

os.chdir(output_folder)
for files in glob.glob("S_seduta_" + legislatura_id +"*.csv"):
    print files


#
# query_votazioni = """
# PREFIX osr: <http://dati.senato.it/osr/>
# PREFIX ocd: <http://dati.camera.it/ocd/>
# select ?votazione ?seduta
# where
# {
# ?seduta a osr:SedutaAssemblea.
# ?seduta osr:dataSeduta ?dataSeduta.
# ?seduta osr:legislatura ?legislatura.
#
# ?votazione a osr:Votazione.
# ?votazione osr:seduta ?seduta.
#
# FILTER(str(?legislatura)="%s")
#
# }
# ORDER BY ?seduta
# """ % settings.legislatura_id
#
#
# results_votazioni = run_query(settings.sparql_senato, query_votazioni)
#
# # per ogni seduta estrae il numero delle votazioni relative
# for votazioni in results_votazioni:
#
#     nvotazione = votazioni["votazione"]
#
#
#     query_votazione = """
#     PREFIX osr: <http://dati.senato.it/osr/>
#     PREFIX ocd: <http://dati.camera.it/ocd/>
#     select distinct ?votazione ?label ?favorevoli ?contrari ?astenuti ?presenti ?missione ?maggioranza ?nlegale ?esito ?votanti
#     where
#     {
#     ?votazione a osr:Votazione.
#     ?votazione osr:favorevoli ?favorevoli.
#     ?votazione osr:contrari ?contrari.
#     ?votazione osr:astenuti ?astenuti.
#     ?votazione osr:inCongedoMissione ?missione.
#     ?votazione osr:presenti ?presenti.
#     ?votazione osr:votanti ?votanti.
#     ?votazione osr:maggioranza ?maggioranza.
#     ?votazione osr:numeroLegale ?nlegale.
#     ?votazione osr:esito ?esito.
#     ?votazione rdfs:label ?label.
#     FILTER(str(?votazione)='%s')
#     }
#
#     """ % nvotazione
#
#
#     fields_votazione = ["votazione","label","favorevoli","contrari","astenuti","presenti","missione","maggioranza","nlegale","esito","votanti"]
#     results_votazione = run_query(sparql_senato, query_votazione, fields_votazione)
#     write_file(output_folder+"s_votazioni_"+today+"_"+nvotazione,fields_votazione, results_votazione)

    # TODO: tirare giu tutti i dati rispettivi ai VOTI singoli e metterli in un file

    # val_aggregazione = ["favorevole", "contrario", "astenuto", "inCongedoMissione"]
    #
    # for val in val_aggregazione:
    #     query_aggregazione = """
    #     PREFIX osr: <http://dati.senato.it/osr/>
    #     PREFIX ocd: <http://dati.camera.it/ocd/>
    #     select COUNT(?%s) as ?%s
    #     where
    #     {
    #     ?votazione a osr:Votazione.
    #     ?votazione osr:%s ?%s.
    #     FILTER(str(?votazione)='%s').
    #     }
    #     """ % (val, val, val, val, nvotazione)
    #
    #     fields_aggregazione = ["s"]
    #     results_aggregazione = run_query(sparql_senato, query_aggregazione, fields_aggregazione)
    #     write_to_file(output_folder+"s_votazioni_"+today+"_"+nvotazione,fields_votazione, results_votazione)
    #
    #
    #     sparql.setQuery(query_aggregazione)
    #     sparql.setReturnFormat(JSON)
    #     try:
    #         results_aggregazione = sparql.query().convert()
    #     except EndPointNotFound, err:
    #         print(query_aggregazione)
    #         error(err)
    #         sys.exit(1)
    #
    #     result_aggregazione = results_aggregazione["results"]["bindings"][0][val]["value"]
    #
    #     print(val + ":" + result_aggregazione)
    #



