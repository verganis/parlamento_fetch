# confronta la composizione attuale con il file di composizione piu' recente trovato
# manda una mail con le differenze tra i file (aggiunte e cancellazioni)

from utils.sparql import *
from settings import *

from datetime import date
import os
import glob

# no_file si attiva se non ci sono file precedenti di riferimento
no_file = False
today_str = date.today().strftime(date_format)

# trova il file di composizione senato piu' recente con prefisso stabilito
file_prefix = senato_prefix + prefix_separator + composizione_prefix
filelist = glob.glob(output_folder + file_prefix + '*')
filelist = filter(lambda x: not os.path.isdir(x), filelist)
if filelist:
    newest = max(filelist, key=lambda x: os.stat(x).st_mtime)
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
    ?tipoMandato
    ?id_gruppo ?inizioAdesione ?fineAdesione ?nomeGruppo

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

    ?id_gruppo osr:denominazione ?denGruppo.
    ?denGruppo osr:titolo ?nomeGruppo.

    FILTER(str(?legislaturaMandato)='%s')
    FILTER(str(?legislaturaAdesione)='%s')

    } ORDER BY ?cognome ?nome
""" % (16,16)

results = run_query(sparql_senato, query_composizione)


# per ogni senatore va a prendere il gruppo di appartenenza e lo aggiunge al dizionario del senatore


fields = ["senatore", "nome", "cognome", "inizioMandato", "fineMandato", "tipoMandato","inizioAdesione","fineAdesione","id_gruppo","nomeGruppo"]
write_file(output_folder +file_prefix+today_str, results, fields, True)



