from utils.sparql import *



query_gruppi = """
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT DISTINCT ?name ?surname ?nomegruppo ?dataAdesione
WHERE
{
?item a ocd:deputato.
?item ocd:aderisce ?ade.
?ade dc:date ?dataAdesione.
OPTIONAL{

?item foaf:firstName ?name.
?item foaf:surname ?surname.
}
?item ocd:rif_incarico ?incarico.
?incarico ocd:rif_gruppoParlamentare ?gruppo.
?gruppo dc:title ?nomegruppo.

}
ORDER BY ?surname
"""

#TODO: aggiungere riferimento legislatura e data odierna
# PREFIX ocd: <http://dati.camera.it/ocd/>
# PREFIX dc: <http://purl.org/dc/elements/1.1/>
#
# SELECT DISTINCT ?labelGruppo ?rif_leg ?firstName ?surname
# WHERE
# {
#
# ?gp a ocd:gruppoParlamentare.
# ?gp ocd:rif_leg ?rif_leg.
# ?gp rdfs:label ?labelGruppo.
# ?gp ocd:siComponeDi ?scd.
#
# ?scd ocd:startDate ?startDate.
# ?scd ocd:endDate ?endDate.
# ?scd ocd:rif_deputato ?deputato.
#
# ?deputato a ocd:deputato.
# ?deputato foaf:firstName ?firstName.
# ?deputato foaf:surname ?surname.
#
#
# FILTER(str(?rif_leg)="http://dati.camera.it/ocd/legislatura.rdf/repubblica_16")
# }



fields_gruppi = ["name","surname","nomegruppo","dataAdesione"]
results_gruppi = run_query(sparql_camera, query_gruppi, fields_gruppi)
write_to_file(output_folder+"c_attivi_grupppi"+today,fields_atti, results_atti)






