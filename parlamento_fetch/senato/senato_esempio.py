from SPARQLWrapper import SPARQLWrapper, JSON

day = "20130301"

sparql = SPARQLWrapper("http://dati.senato.it/sparql-query")
sparql.setQuery("""
select distinct ?Concept where {[] a ?Concept} LIMIT 100
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print "%s " % (result["Concept"]['value'],)

