# a partire da due date verifica le differenze fra i senatori in carica a data1 e data2 e salva due file
# AAAAMMGG-senatori_added e AAAAMMGG-senatori_removed con le differenze
from utils.sparql import *

today = "2013-03-13"
last_update = "2010-05-06"

senatori_added = []
senatori_removed = []

query_composizione = """
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select distinct ?senatore ?name ?surname ?gruppo ?datafine ?datainizio
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

FILTER(str(?datafine) > '%s').
FILTER(str(?datainizio) <= '%s')
}

ORDER BY ?surname
"""

query_composizione_today = query_composizione % (today, today)
query_composizione_lastupdate = query_composizione % (last_update, last_update)

fields_today = ["senatore","name","surname", "gruppo", "datafine", "datainizio"]
fields_lastupdate = fields_today

results_today = run_query(sparql_senato, query_composizione_today, fields_today )
results_lastupdate = run_query(sparql_senato, query_composizione_lastupdate, fields_lastupdate)

for senatore in results_today:
    #trova i senatori aggiunti
    trovato = False
    for senatore_last in results_lastupdate:
        if senatore["senatore"] == senatore_last["senatore"]:
            trovato = True
            break
    if not trovato:
        senatori_added.append(senatore)


for senatore in results_lastupdate:

    #trova i senatori rimossi
    trovato = False
    for senatore_today in results_today:
        if senatore["senatore"] == senatore_today["senatore"]:
            trovato = True
            break
    if not trovato:
        senatori_removed.append(senatore)


write_to_file(output_folder+"s_composizione_removed",fields_today, senatori_removed)
write_to_file(output_folder+"s_composizione_added",fields_today, senatori_added)

