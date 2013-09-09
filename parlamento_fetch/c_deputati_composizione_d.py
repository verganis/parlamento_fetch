# confronta la composizione attuale con il file di composizione piu' recente trovato
# manda una mail con le differenze tra i file (aggiunte e cancellazioni)

from utils.sparql_tools import *
from settings_local import *
from datetime import date
import os
import glob
import difflib
from settings_local import notification_system, smtp_server


# no_file si attiva se non ci sono file precedenti di riferimento
no_file = False

today_str = date.today().strftime(date_format)
mail_subject = "Differenze Composizione Senato al "+today_str

# trova il file di composizione senato piu' recente con prefisso stabilito
file_prefix = senato_prefix + prefix_separator + composizione_prefix

today_filename = output_folder +file_prefix+today_str
newest_filename=''
filelist = glob.glob(output_folder + file_prefix + '*')
filelist = filter(lambda x: not os.path.isdir(x), filelist)
if filelist:
    newest_filename = max(filelist, key=lambda x: os.stat(x).st_mtime)
else:
    no_file = True

senatori_added = []
senatori_removed = []


# prende la lista dei senatori senza data di fine mandato e li mette in results

query_composizione = """
    PREFIX osr: <http://dati.senato.it/osr/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ocd:<http://dati.camera.it/ocd/>

    SELECT DISTINCT
    ?senatore ?nome ?cognome
    ?inizioMandato ?fineMandato
    ?tipoMandato ?adesioneCarica
    ?id_gruppo ?inizioAdesione ?fineAdesione

    WHERE {
    ?senatore a osr:Senatore.
    ?senatore foaf:firstName ?nome.
    ?senatore foaf:lastName ?cognome.
    ?senatore ocd:aderisce ?aderisce.
    ?senatore osr:mandato ?mandato.
    ?mandato osr:legislatura ?legislaturaMandato.
    ?mandato osr:inizio ?inizioMandato.
    ?mandato osr:tipoMandato ?tipoMandato.
    OPTIONAL { ?mandato osr:fine ?fineMandato. }

    ?aderisce osr:legislatura ?legislaturaAdesione.
    ?aderisce osr:gruppo ?id_gruppo.
    ?aderisce osr:inizio ?inizioAdesione.
    OPTIONAL { ?aderisce osr:fine ?fineAdesione.}
    ?aderisce osr:carica ?adesioneCarica.


    FILTER(str(?legislaturaMandato)='%s')
    FILTER(str(?legislaturaAdesione)='%s')

    } ORDER BY ?cognome ?nome
""" % (legislatura_id,legislatura_id)

results = run_query(sparql_senato, query_composizione)

fields = ["senatore", "nome", "cognome",
          "inizioMandato", "fineMandato",
          "inizioAdesione","fineAdesione",
          "id_gruppo","adesioneCarica", "tipoMandato"]
write_file(today_filename, results, fields, True)

msg = create_diff(today_filename, newest_filename)
if msg == "":
    msg=no_difference_msg

send_email(smtp_server, notification_system,notification_list,mail_subject,msg)

