from utils.sparql import *

#estrae tutti gli atti della Camera per una certa data e genera un file XML
# con tutti i dati relativi agli atti presentati quel giorno



today="20110908"

query_atti="""
 PREFIX ocd: <http://dati.camera.it/ocd/>
   PREFIX dc: <http://purl.org/dc/elements/1.1/>
   PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
   PREFIX persona: <http://dati.camera.it/ocd/persona>
   PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>

SELECT DISTINCT  ?atto ?label ?title ?rif_governo ?rif_statoIter ?primo_firmatario
WHERE
{
  ?atto ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
  ?atto a <http://dati.camera.it/ocd/atto> .
  ?atto rdfs:label ?label .
  ?atto dc:title ?title.
  ?atto dc:date ?date .
  ?atto ocd:primo_firmatario ?primo_firmatario.
  ?atto ocd:rif_governo ?rif_governo.
  ?atto ocd:rif_statoIter ?rif_statoIter.


  FILTER(substr(?date, 1, 8) = '%s')
}
""" % today


fields_atti = ["atto","label","title","primo_firmatario","rif_governo",
               "rif_statoIter"]
results_atti = run_query(sparql_camera, query_atti, fields_atti)
write_file(output_folder+"c_atti_"+today+".xml",results_atti)

