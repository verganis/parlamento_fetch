#senatori attivi al tal giorno, non include il nome del gruppo x esteso perche' attualmente
# da' luogo a risultati ripetuti

from utils.sparql_tools import *

day = "2012-03-15"

query = """
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX ocd: <http://dati.camera.it/ocd/>
select distinct ?name ?surname ?gruppo ?datafine ?datainizio
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


FILTER(?leg=16).
FILTER(str(?datafine) > '%s').
FILTER(str(?datainizio) <= '%s')
}

ORDER BY ?surname
""" % (day, day)

fields = ["name","surname", "gruppo", "datafine", "datainizio"]
results = run_query(sparql_senato, query, fields)

write_to_file(output_path+"s_gruppi_data",fields, results)
