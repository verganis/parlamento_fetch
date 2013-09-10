import re
from utils.sparql_tools import run_query, write_file, send_email
import glob, os
from settings_local import *
import time


# controlla le votazioni presenti sul sito del Senato e le confronta con i file gia' salvati
# nell'apposita cartella dati. se sono presenti nuove votazioni genera tre tipi di file:
# * file con tutti i dati della votazione
#  - votazione_LEGISLATURA_NUMEROSEDUTA_NUMEROVOTAZIONE.csv
# * aggiorna il file che mette in relazione la seduta con le relative votazioni
#  - votazioni_LEGISLATURA_NUMEROSEDUTA.csv
# * file con tutti i dati relativi alla seduta, se non e' gia presente
#  - seduta_LEGISLATURA_NUMEROSEDUTA.csv
#  nel caso in cui non si riesca a connettere allo sparql endpoint manda una mail alla lista di admin



# cerco il file che inizia con seduta_legislatura_*.csv e vedo qual e' l'ultima che
#  e' stata gia' importata

os.chdir(output_folder)
seduta_file_pattern = senato_prefix + prefix_separator + seduta_prefix + \
                      prefix_separator + legislatura_id + prefix_separator

n_last_seduta = '0'
sedute_file = sorted(glob.glob(seduta_file_pattern + "*.csv"), key=os.path.realpath)
if len(sedute_file)>0:
    last_seduta_filename = sedute_file[-1]

    seduta_reg_exp=re.compile('^'+seduta_file_pattern+'(.+).csv')
    n_last_seduta = seduta_reg_exp.match(last_seduta_filename).groups()[0]


# vedo su sparql se sono presenti sedute successive
print "query sedute"
query_sedute = """
    PREFIX osr: <http://dati.senato.it/osr/>
    PREFIX ocd: <http://dati.camera.it/ocd/>
    select ?seduta ?numero
    where
    {
    ?seduta a osr:SedutaAssemblea.
    ?seduta osr:numeroSeduta ?numero.
    ?seduta osr:legislatura """ + legislatura_id +"""
    FILTER( ?numero > """ + n_last_seduta +""")
    }
    ORDER BY ?numero
    """
results_sedute = run_query(sparql_senato, query_sedute)

if results_sedute != -1:
    # se sono presenti sedute non importate le importa
    if len(results_sedute)>0:
        for seduta in results_sedute:
            print "query seduta " + seduta['numero']
            time.sleep(0.01)
            # query per prendere tutti i dati della singola seduta
            query_seduta = """
                PREFIX osr: <http://dati.senato.it/osr/>
                PREFIX ocd: <http://dati.camera.it/ocd/>
                select ?seduta ?data ?tipoSeduta ?numero
                where
                {
                ?seduta a osr:SedutaAssemblea.
                ?seduta osr:legislatura ?legislatura.
                ?seduta osr:numeroSeduta ?numero.
                ?seduta osr:dataSeduta ?data.
                ?seduta osr:tipoSeduta ?tipoSeduta.
                FILTER( ?numero = """+seduta['numero'] +"""
                    and ?legislatura = """+legislatura_id +"""
                    )
                }
                """

            results_seduta = run_query(sparql_senato, query_seduta)
            if results_seduta != -1:
                # scrive il file seduta
                write_file(output_folder+
                           seduta_file_pattern+seduta['numero'],
                           results_seduta,fields=None,print_metadata=True
                    )

                #cerca tutte le votazioni per la presente seduta e se ce ne sono le importa

                query_seduta_votazioni = """
                    PREFIX osr: <http://dati.senato.it/osr/>
                    PREFIX ocd: <http://dati.camera.it/ocd/>
                    select ?numero
                    where
                    {
                    ?votazione a osr:Votazione.
                    ?votazione osr:seduta """+seduta['numero']+""".
                    ?votazione osr:numeroLegale ?numero.
                    }
                    ORDER BY ?numero

                    """




            else:
                send_email(smtp_server, notification_system,notification_list,"Sparql Senato: http error","Connection refused")

    else:
        print "nessuna nuova seduta"
        exit(1)
else:
    send_email(smtp_server, notification_system,notification_list,"Sparql Senato: http error","Connection refused")

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
