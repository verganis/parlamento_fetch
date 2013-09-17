import json
import pprint
import re
from utils.sparql_tools import run_query, write_file, send_email
import glob, os
from settings_local import *
import logging

# controlla le votazioni presenti sul sito del Senato e le confronta con quelle
# gia' importate tramite le API di Open Parlamento
# se sono presenti nuove votazioni le prende dallo sparql end point,
# le controlla e le inserisce in Open Parlamento tramite le API.
# nel caso vengano riscontrati errori, li notifica.


error_messages={
    'connection_fail':'http error: Connection refused'
}

campi_controllo_somme=[
    # lista di id,totale
    ('astenuto','astenuti'),
    ('inCongedoMissione','congedoMissione'),
    ('contrario','contrari'),
    ('favorevole','favorevoli'),
    ('votante','votanti'),
    ('presente','presenti'),
]

seduta_file_pattern = senato_prefix + prefix_separator + seduta_prefix + \
                      prefix_separator + legislatura_id + prefix_separator

votazioni_file_pattern = senato_prefix + prefix_separator + votazioni_prefix + \
                         prefix_separator + legislatura_id + prefix_separator


votazione_file_pattern = senato_prefix + prefix_separator + votazione_prefix + \
                         prefix_separator + legislatura_id + prefix_separator

n_last_seduta = '7'
# TODO: legge le api di Open parlamento per vedere qual e' l'ultima seduta importata


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

                            #     controlla la correttezza dei dati della votazione
                            check_campi = []
                            for k, campi in campi_controllo_somme:
                                if osr_prefix+campi[0] in results_votazione.keys() and osr_prefix+campi[1] in results_votazione.keys():
                                    if len(results_votazione[osr_prefix+campi[0]]) == int(results_votazione[osr_prefix+campi[1]][0]):
                                        print campi[0] + " ok"
                                        check_campi[k] = True
                                    else:
                                        print campi[1] + " ko: %s != %s" % (len(results_votazione[osr_prefix+campi[0]]), results_votazione[osr_prefix+campi[1]][0])
                                        check_campi[k] = False
                                else:
                                    check_campi[k] = False

                            #


                        else:
                            error_type = "connection_fail"
                            send_email(smtp_server,
                                       notification_system,
                                       notification_list,
                                       subject= script_name + " - " +error_type,
                                       content= error_messages[error_type]
                            )


                    else:
                        error_type = "connection_fail"
                        send_email(smtp_server,
                                   notification_system,
                                   notification_list,
                                   subject= script_name + " - " +error_type,
                                   content= error_messages[error_type]
                        )
                write_file(output_folder+
                           seduta_file_pattern+
                           seduta['numero']+".json",
                           total_result,
                           fields=None,
                           print_metadata=False,
                           Json=True
                    )

            else:
                error_type = "connection_fail"
                send_email(smtp_server,
                           notification_system,
                           notification_list,
                           subject= script_name + " - " +error_type,
                           content= error_messages[error_type]
                )

    else:
        print "nessuna nuova seduta"
        exit(1)
else:
    error_type = "connection_fail"
    send_email(smtp_server,
               notification_system,
               notification_list,
               subject= script_name + " - " +error_type,
               content= error_messages[error_type]
    )
