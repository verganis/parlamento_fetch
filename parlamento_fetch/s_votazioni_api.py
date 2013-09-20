import json
import pprint
import re
from utils.sparql_tools import run_query, write_file, send_email
import glob, os
from settings_local import *
import logging
import requests

# controlla le votazioni presenti sul sito del Senato e le confronta con quelle
# gia' importate tramite le API di Open Parlamento
# se sono presenti nuove votazioni le prende dallo sparql end point,
# le controlla e le inserisce in Open Parlamento tramite le API.
# nel caso vengano riscontrati errori, li notifica.


error_messages={
    'connection_fail':'http error: Connection refused for the query: %s',
    'somma_votanti': "Somma votanti non corretta: %s != %s",
    'somma_presenti': "Somma presenti non corretta: %s != %s"
}


error_mail_body= {'connection': []}

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


# legge le api di Open parlamento per vedere qual e' l'ultima seduta importata correttamente

n_last_seduta = 0
seduta_day = ""

parlamento_api_sedute = parlamento_api_host  +parlamento_api_url +"/" + parlamento_api_leg_prefix + "/" +\
                        parlamento_api_sedute_prefix +"/"+\
                        "?ramo=S&ordering=-numero&page_size=500&format=json"


r_incarica_list = requests.get(parlamento_api_sedute)
r_incarica_json = r_incarica_list.json()
n_last_seduta = r_incarica_json['results'][0]['numero']

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
    FILTER( ?numero > """ +str(n_last_seduta) +""")
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
                # prende il giorno della seduta per verificare i senatori in carica quel giorno
                # il booleano seduta_new_day evita di rifare piu' volte la query sui sen.in carica quando stiamo
                # trattando sedute diverse avvenute nello stesso giorno
                seduta_new_day = False
                if seduta_day != results_seduta[0]['data']:
                    seduta_new_day = True
                    seduta_day = results_seduta[0]['data']




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

                        error_mail_body[votazione['votazione']]=[]

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

                        print "tipo votazione: "+results_votazione[osr_prefix+'tipoVotazione'][0]

                        if results_votazione!=-1:
                            total_result['votazioni'][votazione['votazione']] = results_votazione

                            #     controlla la correttezza dei dati della votazione
                            check_campi = []

                            # se la votazione non e' segreta
                            if results_votazione[osr_prefix+'tipoVotazione'][0] != 'segreta':

                                # per ogni campo da controllare controlla che esista il totale numerico.
                                # se il totale e' maggiore di 0 allora deve esistere anche la lista con gli id riferiti al campo
                                # se la lista esiste allora il numero di id deve essere = al totale numerico
                                for (k, campi) in enumerate(campi_controllo_somme):
                                    if osr_prefix+campi[1] in results_votazione.keys():
                                        if int(results_votazione[osr_prefix+campi[1]][0])>0:
                                            if osr_prefix+campi[0] in results_votazione.keys():
                                                if len(results_votazione[osr_prefix+campi[0]]) == \
                                                        int(results_votazione[osr_prefix+campi[1]][0]):
                                                    campo_validation=True
                                                else:
                                                    campo_validation=False

                                            else:
                                                campo_validation=False

                                        else:
                                            if int(results_votazione[osr_prefix+campi[1]][0])==0:
                                                campo_validation=True
                                            else:
                                                campo_validation=False
                                    else:
                                        campo_validation=False

                                    check_campi.append(campo_validation)
                                    if not campo_validation:
                                        print campi[0]+" : "+str(campo_validation)

                            else:
                                # se la votazione e' segreta controlla che ci siano i totali numerici dei campi indicati
                                for (k, campi) in enumerate(campi_controllo_somme):
                                    if osr_prefix+campi[1] not in results_votazione.keys():
                                        campo_validation=False
                                    else:
                                        campo_validation= True

                                    check_campi.append(campo_validation)
                                    if not campo_validation:
                                        print campi[0]+" : "+str(campo_validation)

                            # effettua controlli sulle somme
                            # votanti= favorevoli + contrari + astenuti
                            somma_votanti = int(results_votazione[osr_prefix+"favorevoli"][0]) +\
                                int(results_votazione[osr_prefix+"contrari"][0])+ \
                                int(results_votazione[osr_prefix+"astenuti"][0])
                            if int(results_votazione[osr_prefix+"votanti"][0]) != somma_votanti:
                                print "Somma votanti non corretta: %s != %s" % (somma_votanti, results_votazione[osr_prefix+"votanti"][0])
                                error_type = "somma_votanti"
                                error_mail_body[votazione['votazione']].append(error_messages[error_type]% (somma_votanti, results_votazione[osr_prefix+"votanti"][0]))


                            # presenti = votanti + presidente +  richiedenteNonVotante
                            somma_presenti = int(results_votazione[osr_prefix+"votanti"][0])
                            if osr_prefix+"presidente" in results_votazione.keys():
                                somma_presenti += 1

                            if osr_prefix+"richiedenteNonVotante" in results_votazione.keys():
                                somma_presenti += len(results_votazione[osr_prefix+"richiedenteNonVotante"])
                            if int(results_votazione[osr_prefix+"presenti"][0]) != somma_presenti:
                                print "Somma presenti non corretta: %s != %s" % (somma_presenti, results_votazione[osr_prefix+"presenti"][0])
                                error_type = "somma_presenti"
                                error_mail_body[votazione['votazione']].append(error_messages[error_type]% (somma_presenti, results_votazione[osr_prefix+"presenti"][0]))


                            #  effettua i controlli sulla votazione basati sui senatori in carica quel giorno

                            #  TODO: controlla che le somme presenti + congedo missione + assenti siano = al n. totale di s. in carica

                            # controlla che tutti i senatori in astenuto, congedo missione, contrario,
                            # favorevole, richiedente non votante, e presidente siano in carica quel giorno
                            totale_senatori_seduta = results_votazione[osr_prefix+'votante']
                            if osr_prefix+"inCongedoMissione" in results_votazione.keys():
                                totale_senatori_seduta.extend(results_votazione[osr_prefix+'inCongedoMissione'])
                            if osr_prefix+"richiedenteNonVotante" in results_votazione.keys():
                                totale_senatori_seduta.extend(results_votazione[osr_prefix+'richiedenteNonVotante'])
                            totale_senatori_seduta.extend(results_votazione[osr_prefix+'presidente'])


                            # prende la lista completa di senatori in carica quel giorno dalle Api
                            if seduta_new_day is True:
                                parlamento_api_incarica = parlamento_api_host  +parlamento_api_url +"/" + \
                                                          parlamento_api_leg_prefix + "/" + \
                                                          parlamento_api_parlamentari_prefix+"/"+ \
                                                        "?ramo=S&data="+seduta_day+"&page_size=500&format=json"

                                print "parlamento_api_incarica:"+parlamento_api_incarica

                                r_incarica_list = requests.get(parlamento_api_incarica)
                                r_incarica_json = r_incarica_list.json()
                                totale_senatori_api = r_incarica_json['results']


                            for senatore in totale_senatori_seduta:
                                trovato = False
                                senatore_noprefix = senatore.replace(senatore_prefix,"")
                                for senatore_api in totale_senatori_api:

                                    if senatore_noprefix == str(senatore_api['carica']['parliament_id']):
                                        trovato = True


                                if not trovato:
                                    # print u"senatore nome:"+senatore_api['anagrafica']['nome']+ \
                                    #       +senatore_api['anagrafica']['cognome']+ \
                                    #       u" id:" +senatore+ u" non trovato in Senatori in Carica"

                                    # TODO: aggingere questo caso al log di errore
                                    print u" id:" +senatore_noprefix+ u" non trovato in Senatori in Carica"



                        else:
                            error_type = "connection_fail"
                            error_mail_body['connection'].append(error_messages[error_type]%query_votazione)


                else:
                    error_type = "connection_fail"
                    error_mail_body['connection'].append(error_messages[error_type]%query_seduta_votazioni)

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
                error_mail_body['connection'].append(error_messages[error_type]%query_seduta)

    else:
        print "nessuna nuova seduta"

else:
    error_type = "connection_fail"
    error_mail_body.append['connection'](error_messages[error_type]%query_sedute)


# se c'e' stato qualche errore manda la mail agli amministratori di sistema

error_keys = error_mail_body.keys()
content_str =""
error_c = 0
for error_key in error_keys:
    # serializza i msg di errori
    if len(error_mail_body[error_key])>0:
        for msg in error_mail_body[error_key]:
            content_str+=error_key+" : "+msg+"\n"
            error_c+=1


if error_c>0:
    send_email(smtp_server,
               notification_system,
               notification_list,
               subject= script_name + " - " + str(error_c) +" errori",
               content= content_str
    )
else:
    print "no errors"