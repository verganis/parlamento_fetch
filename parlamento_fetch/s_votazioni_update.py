import json
import pprint
import re
from utils.sparql_tools import run_query
from utils.utils import send_email, write_file
import glob, os
from settings_local import *
import logging

# controlla le votazioni presenti sul sito del Senato e le confronta con i file gia' salvati
# nell'apposita cartella dati. se sono presenti nuove votazioni genera tre tipi di file:
# * file con tutti i dati della votazione
#  - votazione_LEGISLATURA_NUMEROSEDUTA_NUMEROVOTAZIONE.json
# * aggiorna il file che mette in relazione la seduta con le relative votazioni
#  - votazioni_LEGISLATURA_NUMEROSEDUTA.json
# * file con tutti i dati relativi alla seduta, se non e' gia presente
#  - seduta_LEGISLATURA_NUMEROSEDUTA.json
#  nel caso in cui non si riesca a connettere allo sparql endpoint manda una mail alla lista di admin

# cerco il file che inizia con seduta_legislatura_*.json e vedo qual e' l'ultima che
#  e' stata gia' importata

error_messages = []

os.chdir(output_path)
seduta_file_pattern = senato_prefix + prefix_separator + seduta_prefix + \
                      prefix_separator + legislatura_id + prefix_separator

votazioni_file_pattern = senato_prefix + prefix_separator + votazioni_prefix + \
                         prefix_separator + legislatura_id + prefix_separator


votazione_file_pattern = senato_prefix + prefix_separator + votazione_prefix + \
                         prefix_separator + legislatura_id + prefix_separator

n_last_seduta = '0'
sedute_file = sorted(glob.glob(seduta_file_pattern + "*.json"), key=os.path.realpath)
if len(sedute_file)>0:
    last_seduta_filename = sedute_file[-1]

    seduta_reg_exp=re.compile('^'+seduta_file_pattern+'(.+).json')
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
            # total result will be the comprehensive collection of data about a seduta and
            # all its votazioni
            total_result = {}
            print "query seduta " + seduta['numero']

            # query per prendere tutti i dati della singola seduta
            query_seduta = """
                PREFIX osr: <http://dati.senato.it/osr/>
                PREFIX ocd: <http://dati.camera.it/ocd/>
                select ?data ?tipoSeduta ?numero
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

            results_seduta = run_query(sparql_senato, query_seduta,query_delay, Json=False)
            if results_seduta != -1:

                # aggiunge i metadati della seduta al dizionario totale
                total_result['metadata'] = results_seduta

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
                    total_result['votazioni']={}

                    for votazione in results_votazioni:
                        print "query sed:" +seduta['numero']+", votazione:"+votazione['votazione']
                        query_votazione = """
                            PREFIX osr: <http://dati.senato.it/osr/>
                            PREFIX ocd: <http://dati.camera.it/ocd/>
                            select ?field ?value
                            where
                            {
                            ?votazione a osr:Votazione.
                            ?votazione ?field ?value.
                            filter( str(?votazione) = str(\""""+votazione['votazione']+"""\"))
                            }
                            ORDER BY ?field
                            """
                        results_votazione = run_query(sparql_senato, query_votazione,query_delay,Json=True)

                        if results_votazione!=-1:
                            total_result['votazioni'][votazione['votazione']] = results_votazione

                        else:
                            error_messages.append("Connection refused for query vot: %s" % query_votazione)

                else:
                    error_messages.append("Connection refused for query seduta vot: %s" % query_seduta_votazioni)


                write_file(output_path+
                           seduta_file_pattern+
                           seduta['numero']+".json",
                           total_result,
                           fields=None,
                           print_metadata=False,
                           Json=True
                )

            else:
                error_messages.append("Connection refused for query seduta: %s" % query_seduta)


    else:
        print "nessuna nuova seduta"
        exit(1)
else:
    error_messages.append("Connection refused for query sedute: %s" % query_sedute)

# se ci sono stati errori manda una singola email con tutti gli errori
if len(error_messages)>0:
    error_message='<BR>'.join(error_messages)
    send_email(smtp_server, notification_system,notification_list,"Sparql Senato: http error",error_message)
