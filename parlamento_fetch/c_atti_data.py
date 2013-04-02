from stringold import split
from utils.sparql import *

#estrae tutti gli atti della Camera da una certa data e
# per ogni atto estrae tutti i dettagli

today="20110908"

query_atti="""
 PREFIX ocd: <http://dati.camera.it/ocd/>
   PREFIX dc: <http://purl.org/dc/elements/1.1/>
   PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
   PREFIX persona: <http://dati.camera.it/ocd/persona>
   PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>

SELECT DISTINCT  ?atto ?label ?title ?rif_governo ?rif_statoIter
WHERE
{
  ?atto ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
  ?atto a <http://dati.camera.it/ocd/atto> .
  ?atto rdfs:label ?label .
  ?atto dc:title ?title.
  ?atto dc:date ?date .
  ?atto ocd:rif_governo ?rif_governo.
  ?atto ocd:rif_statoIter ?rif_statoIter.


  FILTER(substr(?date, 1, 8) = '%s')
}
""" % today


fields_atti = ["atto","label","title","primo_firmatario","rif_governo",
               "richiesta_parere","rif_statoIter","riv_versioneTestoAtto"]
results_atti = run_query(sparql_camera, query_atti, fields_atti)
write_to_file(output_folder+"c_atti_"+today,fields_atti, results_atti)


for result in results_atti:
    #dettagli delle leggi

    query_detail = "SELECT DISTINCT ?p ?v WHERE {<" + result["atto"] + "> ?p ?v}"
    fields_detail = ["p","v"]

    results_detail = run_query(sparql_camera, query_detail, fields_detail)
    string_split = result["label"].rsplit(". - \"")
    n_atto=string_split[0]
    write_to_file(output_folder+"c_atti_"+n_atto,["p","v"], results_detail)



