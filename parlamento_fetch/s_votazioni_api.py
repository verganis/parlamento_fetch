import pprint
from utils.sparql_tools import run_query
from utils.utils import send_error_mail, write_file
from settings_local import *
import logging
import requests
from requests import ConnectionError


# la fuzione import_seduta dato un numero di seduta cerca di importare i dati della seduta
# e tutti i dati delle votazioni collegate
def import_seduta(results_sedute, error_mail_body):
    seduta_day = ""
    sedute_result = {}
    for seduta in results_sedute:
        # total result will be the comprehensive collection of data about a seduta and
        # all its votazioni

        seduta_isimported = True
        votazioni_isimported = {}

        sedute_result[seduta['numero']]= {}
        seduta_result = {}
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

        results_seduta = None
        try:
            results_seduta = run_query(sparql_senato, query_seduta,query_delay, Json=False)
        except ConnectionError,e:
            error_type = "sparql_connection_fail"
            error_mail_body['sparql_connection'].append(error_messages[error_type]%e)
            send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
            exit(0)


        if results_seduta is None:
            # se non trova la seduta genera msg di errore
            error_type = "obj_not_found"
            error_mail_body['sparql_connection'].append(error_messages[error_type]%query_seduta)


        else:

            # TODO: inserimenti con api dei dati della seduta

            # aggiunge i metadati della seduta al dizionario totale
            seduta_result['metadata'] = results_seduta
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

            results_votazioni = None
            try:
                results_votazioni = run_query(sparql_senato, query_seduta_votazioni,query_delay)
            except ConnectionError,e:
                error_type = "sparql_connection_fail"
                error_mail_body['sparql_connection'].append(error_messages[error_type]%e)
                send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
                exit(0)

            if results_votazioni is not None:
                seduta_result['votazioni']={}

                for votazione in results_votazioni:
                    votazioni_isimported[votazione['votazione']]=True

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


                    results_votazione = None
                    try:
                        results_votazione = run_query(sparql_senato, query_votazione,query_delay,Json=True)
                    except ConnectionError,e:
                        error_type = "sparql_connection_fail"
                        error_mail_body['sparql_connection'].append(error_messages[error_type]%e)
                        send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
                        exit(0)

                    print "tipo votazione: "+results_votazione[osr_prefix+'tipoVotazione'][0]

                    if results_votazione is None:
                        # se non trova la votazione genera msg di errore
                        error_type = "obj_not_found"
                        error_mail_body['sparql_connection'].append(error_messages[error_type]%query_votazione)

                    else:
                        seduta_result['votazioni'][votazione['votazione']] = results_votazione

                        #  CHECK 1
                        #  controlla la correttezza dei dati numerici della votazione
                        #  e delle liste di id
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

                        # dopo il controllo di check campi passa il valore finale a votazioni_isimported
                        check_conteggi = True
                        for check in check_campi:
                            if check is False:
                                check_conteggi = False

                        if check_conteggi is False:
                            votazioni_isimported[votazione['votazione']]=False


                        #  CHECK 2
                        # effettua controlli sulle somme
                        # votanti= favorevoli + contrari + astenuti

                        check_somme = True
                        somma_votanti = int(results_votazione[osr_prefix+"favorevoli"][0]) + \
                                        int(results_votazione[osr_prefix+"contrari"][0])+ \
                                        int(results_votazione[osr_prefix+"astenuti"][0])
                        if int(results_votazione[osr_prefix+"votanti"][0]) != somma_votanti:
                            print "Somma votanti non corretta: %s != %s" % (somma_votanti, results_votazione[osr_prefix+"votanti"][0])
                            error_type = "somma_votanti"
                            error_mail_body[votazione['votazione']].append(error_messages[error_type]% (somma_votanti, results_votazione[osr_prefix+"votanti"][0]))
                            check_somme = False

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
                            check_somme = False

                        if check_somme is False:
                            votazioni_isimported[votazione['votazione']]=False


                        # CHECK 3
                        # effettua i controlli sulla votazione basati sui senatori in carica quel giorno
                        # da notare che la data di fine Mandato puo' anche non esserci se il sen.
                        # e' attualmente in carica

                        check_incarica = True

                        # prende la lista completa di senatori in carica quel giorno dallo sparql endpoint
                        if seduta_new_day is True:

                            query_incarica = """

                                PREFIX osr: <http://dati.senato.it/osr/>
                                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                                PREFIX ocd:<http://dati.camera.it/ocd/>

                                SELECT DISTINCT
                                ?senatore ?nome ?cognome
                                ?inizioMandato ?fineMandato
                                ?tipoMandato

                                WHERE {
                                ?senatore a osr:Senatore.
                                ?senatore foaf:firstName ?nome.
                                ?senatore foaf:lastName ?cognome.
                                ?senatore osr:mandato ?mandato.
                                ?mandato osr:legislatura ?legislaturaMandato.
                                ?mandato osr:inizio ?inizioMandato.
                                ?mandato osr:tipoMandato ?tipoMandato.
                                OPTIONAL { ?mandato osr:fine ?fineMandato. }

                                FILTER(str(?legislaturaMandato)='%s')
                                FILTER(?inizioMandato <= "%s"^^xsd:date )
                                FILTER(!bound(?fineMandato) || ?fineMandato > "%s"^^xsd:date )

                                } ORDER BY ?cognome ?nome
                                """ % ( legislatura_id, seduta_day, seduta_day)


                            senatori_incarica_sparql = None
                            try:
                                senatori_incarica_sparql = run_query(sparql_senato, query_incarica,query_delay)
                            except ConnectionError,e:
                                error_type = "sparql_connection_fail"
                                error_mail_body['sparql_connection'].append(error_messages[error_type]%e)
                                send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
                                exit(0)


                        # controlla che tutti i senatori in astenuto, congedo missione, contrario,
                        # favorevole, richiedente non votante, e presidente siano in carica quel giorno
                        senatori_seduta_sparql = results_votazione[osr_prefix+'presente']
                        if osr_prefix+"inCongedoMissione" in results_votazione.keys():
                            senatori_seduta_sparql.extend(results_votazione[osr_prefix+'inCongedoMissione'])
                        senatori_seduta_sparql.extend(results_votazione[osr_prefix+'presidente'])


                        # prende la lista completa di senatori in carica quel giorno dalle Api
                        if seduta_new_day is True:
                            parlamento_api_incarica = parlamento_api_host  +parlamento_api_url +"/" + \
                                                      parlamento_api_leg_prefix + "/" + \
                                                      parlamento_api_parlamentari_prefix+"/"+ \
                                                      "?ramo=S&data="+seduta_day+"&page_size=500&format=json"
                            r_incarica_list= None
                            try:
                                r_incarica_list = requests.get(parlamento_api_incarica)
                            except requests.exceptions.ConnectionError:
                                error_type = "api_connection_fail"
                                error_mail_body['api_connection'].append(error_messages[error_type]%parlamento_api_incarica)
                                send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
                                exit(0)

                            r_incarica_json = r_incarica_list.json()
                            totale_senatori_api = r_incarica_json['results']

                        # se il n. di senatori in carica secondo le api != n. sen in carica dello sparql da' errore
                        if len(totale_senatori_api) != len(senatori_incarica_sparql):
                            error_type = "senatori_incarica"
                            print error_messages[error_type] % (len(totale_senatori_api),len(senatori_incarica_sparql))
                            error_mail_body[votazione['votazione']].append(
                                error_messages[error_type]% (len(totale_senatori_api),len(senatori_incarica_sparql))
                            )
                            check_incarica = False

                        #  trova gli eventuali senatori mancanti nelle api o nei dati dallo sparql

                        for senatore_api in totale_senatori_api:
                            trovato = False
                            i=0
                            while not trovato and i < len(senatori_incarica_sparql):
                                senatore_sparql=senatori_incarica_sparql[i]['senatore']
                                senatore_noprefix = senatore_sparql.replace(senatore_prefix,"")
                                if senatore_noprefix == str(senatore_api['carica']['parliament_id']):
                                    trovato = True
                                i+=1
                            if not trovato:
                                # sparql_id_mismatch
                                error_type = "sparql_id_mismatch"
                                print error_messages[error_type] % (str(senatore_api['carica']['parliament_id']))
                                error_mail_body[votazione['votazione']].append(
                                    error_messages[error_type]% (str(senatore_api['carica']['parliament_id']))
                                )
                                check_incarica=False

                        for senatore_sparql in senatori_incarica_sparql:
                            trovato = False
                            senatore_noprefix = senatore_sparql['senatore'].replace(senatore_prefix,"")
                            i=0
                            while not trovato and i < len(totale_senatori_api):
                                senatore_api = totale_senatori_api[i]

                                if senatore_noprefix == str(senatore_api['carica']['parliament_id']):
                                    trovato = True
                                i += 1

                            if not trovato:
                                # api_id_mismatch
                                error_type = "api_id_mismatch"
                                print error_messages[error_type] % (str(senatore_noprefix))
                                error_mail_body[votazione['votazione']].append(
                                    error_messages[error_type]% (str(senatore_noprefix))
                                )
                                check_incarica=False


                        if check_incarica is False:
                            votazioni_isimported[votazione['votazione']]=False
                        else:
                            # TODO: calcolare gli assenti
                            # se un senatore in carica non e' nella lista senatori_seduta_sparql che
                            # comprende i presenti + presidente + in congedo missione , allora
                            # viene considerato assente
                            senatori_assenti = []
                            for senatore_ass in senatori_incarica_sparql:
                                senatore_ass_id = senatore_ass['senatore']
                                trovato = False
                                i=0
                                while not trovato and i < len(senatori_seduta_sparql):
                                    if senatore_ass_id == senatori_seduta_sparql[i]:
                                        trovato = True
                                    i += 1

                                if trovato is False:
                                    senatori_assenti.append(senatore_ass)




                        # se i 4 check sulla votazione sono andati a buon fine il valore is_imported = True
                        # TODO: insert votazione api, usare il vettore assenti


            # una volta analizzate tutte le votazioni della seduta si va a inserire il valore is_imported
            # per la seduta tramite api
            for votazione_isimported in votazioni_isimported.keys():
                if votazioni_isimported is False:
                    seduta_isimported = False

            # TODO: update dati seduta inserendo il nuovo is_imported value


        sedute_result[seduta['numero']]= seduta_result
    return sedute_result





# controlla le votazioni presenti sul sito del Senato e le confronta con quelle
# gia' importate tramite le API di Open Parlamento
# se sono presenti nuove votazioni le prende dallo sparql end point,
# le controlla e le inserisce in Open Parlamento tramite le API.
# nel caso vengano riscontrati errori, li notifica.


error_messages={
    'sparql_connection_fail':'http error: Connection refused from the Sparql for the following query: %s',
    'api_connection_fail':'http error: Connection refused from the api for the following query: %s',
    'sparql_id_mismatch': "id: %s presente nelle api ma non nello Sparql end-point",
    'api_id_mismatch': "id: %s presente nelle Sparql end-point ma non nelle api",
    'somma_votanti': "Somma votanti non corretta: %s != %s",
    'somma_presenti': "Somma presenti non corretta: %s != %s",
    'senatori_incarica': "N. Senatori in carica non coincide: %s != %s",
    'obj_not_found': "Object not found in DB with the following query: %s"
}


error_mail_body= {'sparql_connection': [],'api_connection': []}

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

parlamento_api_sedute = parlamento_api_host  +parlamento_api_url +"/" + parlamento_api_leg_prefix + "/" +\
                        parlamento_api_sedute_prefix +"/"+\
                        "?ramo=S&ordering=-numero&page_size=500&format=json"

r_incarica_list=None
try:
    r_incarica_list = requests.get(parlamento_api_sedute)
except requests.exceptions.ConnectionError:
    error_type = "api_connection_fail"
    error_mail_body['api_connection'].append(error_messages[error_type]%parlamento_api_sedute)
    send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
    exit(0)

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
results_sedute = None

try:
    results_sedute = run_query(sparql_senato, query_sedute,query_delay)
except ConnectionError,e:
    error_type = "sparql_connection_fail"
    error_mail_body['sparql_connection'].append(error_messages[error_type]%e)
    send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
    exit(0)


if results_sedute is not None:

    # se sono presenti sedute non importate le importa
    if len(results_sedute)>0:
        total_result = import_seduta(results_sedute, error_mail_body)

        # scrive un file per ogni seduta importata con tutti i dati delle votazioni associate
        for seduta in total_result.keys():
            write_file(output_folder+
                       seduta_file_pattern+
                       seduta+".json",
                       total_result[seduta],
                       fields=None,
                       print_metadata=False,
                       Json=True
                )

    else:
        print "nessuna nuova seduta"


# check sedute importate nel db OP con is_imported = 0
# TODO: call api per vedere quali sono le sedute interessate
# chiama import_seduta per la lista di sedute interessate

# se c'e' stato qualche errore manda la mail agli amministratori di sistema
send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)

