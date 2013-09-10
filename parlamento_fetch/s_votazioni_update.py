import re
from utils.sparql_tools import run_query, write_file, send_email
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



# cerco il file che inizia con seduta_legislatura_*.csv e vedo qual e' l'ultima che
#  e' stata gia' importata

os.chdir(output_folder)
seduta_file_pattern = senato_prefix + prefix_separator + seduta_prefix + \
                      prefix_separator + legislatura_id + prefix_separator

votazioni_file_pattern = senato_prefix + prefix_separator + votazioni_prefix + \
                         prefix_separator + legislatura_id + prefix_separator


votazione_file_pattern = senato_prefix + prefix_separator + votazione_prefix + \
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
    select ?seduta_id ?numero
    where
    {
    ?seduta_id a osr:SedutaAssemblea.
    ?seduta_id osr:numeroSeduta ?numero.
    ?seduta_id osr:legislatura """ + legislatura_id +"""
    FILTER( ?numero > """ + n_last_seduta +""")
    }
    ORDER BY ?numero
    """
results_sedute = run_query(sparql_senato, query_sedute,query_delay)

if results_sedute != -1:
    # se sono presenti sedute non importate le importa
    if len(results_sedute)>0:
        for seduta in results_sedute:
            print "query seduta " + seduta['numero']

            # query per prendere tutti i dati della singola seduta
            query_seduta = """
                PREFIX osr: <http://dati.senato.it/osr/>
                PREFIX ocd: <http://dati.camera.it/ocd/>
                select ?seduta_id ?data ?tipoSeduta ?numero
                where
                {
                ?seduta_id a osr:SedutaAssemblea.
                ?seduta_id osr:legislatura ?legislatura.
                ?seduta_id osr:numeroSeduta ?numero.
                ?seduta_id osr:dataSeduta ?data.
                ?seduta_id osr:tipoSeduta ?tipoSeduta.
                FILTER( ?numero = """+seduta['numero'] +"""
                    and ?legislatura = """+legislatura_id +"""
                    )
                }
                """

            results_seduta = run_query(sparql_senato, query_seduta,query_delay)
            if results_seduta != -1:
                # scrive il file seduta
                write_file(output_folder+
                           seduta_file_pattern+seduta['numero']+".csv",
                           results_seduta,
                           fields=['seduta_id','data','tipoSeduta','numero'],
                           print_metadata=True
                    )

                #cerca tutte le votazioni per la presente seduta e se ce ne sono le importa

                query_seduta_votazioni = """
                    PREFIX osr: <http://dati.senato.it/osr/>
                    PREFIX ocd: <http://dati.camera.it/ocd/>
                    select ?votazione ?numero
                    where
                    {
                    ?votazione a osr:Votazione.
                    ?votazione osr:numero ?numero.
                    ?votazione osr:seduta ?seduta.
                    filter( str(?seduta) = str(\""""+seduta['seduta_id']+"""\"))
                    }
                    ORDER BY ?numero
                    """

                results_votazioni = run_query(sparql_senato, query_seduta_votazioni,query_delay)
                if results_votazioni!=-1:
                    # scrive il file votazioni
                    write_file(output_folder+
                               votazioni_file_pattern+seduta['numero']+".csv",
                               results_votazioni,
                               fields=['votazione','numero'],
                               print_metadata=True
                        )

                    for votazione in results_votazioni:
                        print "query sed:" +seduta['numero']+", votazione:"+votazione['votazione']
                        query_votazione = """
                            PREFIX osr: <http://dati.senato.it/osr/>
                            PREFIX ocd: <http://dati.camera.it/ocd/>
                            select ?votazione ?field ?value
                            where
                            {
                            ?votazione a osr:Votazione.
                            ?votazione ?field ?value.
                            filter( str(?votazione) = str(\""""+votazione['votazione']+"""\"))
                            }
                            ORDER BY ?field
                            """
                        results_votazione = run_query(sparql_senato, query_votazione,query_delay)
                        if results_votazione!=-1:
                            # scrive il file votazioni
                            write_file(output_folder+
                                       votazione_file_pattern+
                                       seduta['numero']+prefix_separator+
                                       votazione['numero']+".csv",
                                       results_votazione,
                                       fields=['votazione','field','value'],
                                       print_metadata=True
                            )

                        else:
                            send_email(smtp_server, notification_system,notification_list,"Sparql Senato: http error","Connection refused")


                    else:
                        send_email(smtp_server, notification_system,notification_list,"Sparql Senato: http error","Connection refused")


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
