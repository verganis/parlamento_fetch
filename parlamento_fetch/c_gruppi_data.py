from SPARQLWrapper import SPARQLWrapper, JSON

day = "20130301"

sparql = SPARQLWrapper("http://dati.camera.it/sparql")
sparql.setQuery("""
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?groupLabel ?sigla ?label ?date ?sdate ?edate
WHERE
{
  ?gruppo ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
  ?gruppo a ocd:gruppoParlamentare .
  ?gruppo dc:title ?groupLabel .
  ?gruppo dcterms:alternative ?sigla .
  ?gruppo ocd:siComponeDi [
    rdfs:label ?label;
    dc:date ?date;
    ocd:motivoTermine ?motivo;
    ocd:startDate ?sdate;
    ocd:endDate ?edate;
  ] .
  FILTER(substr(?date, 1, 8) <= '%s').
  FILTER(substr(?date, 10, 8) > '%s')
}
ORDER BY ?sigla ?label
""" % (day, day))
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

#controlla il n. deputati al tal giorno

sparql.setQuery("""
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT count(?label) as ?c
WHERE
{
  ?gruppo ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_16> .
  ?gruppo a ocd:gruppoParlamentare .
  ?gruppo dc:title ?groupLabel .
  ?gruppo dcterms:alternative ?sigla .
  ?gruppo ocd:siComponeDi [
    rdfs:label ?label;
    dc:date ?date;
    ocd:motivoTermine ?motivo;
    ocd:startDate ?sdate;
    ocd:endDate ?edate;
  ] .
  FILTER(substr(?date, 1, 8) <= '%s').
  FILTER(substr(?date, 10, 8) > '%s')
}
""" % (day, day))
sparql.setReturnFormat(JSON)
results_count = sparql.query().convert()

for result in results["results"]["bindings"]:

    print "%s - %s " % (result["sigla"]['value'], result["label"]['value'],)
    print "%s (%s - %s)" % (result["date"]['value'], result["sdate"]['value'], result["edate"]['value'],)

for count in results_count["results"]["bindings"]:
    print "Conteggio totale deputati: %s" % count["c"]['value']

