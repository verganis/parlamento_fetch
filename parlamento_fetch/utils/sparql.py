from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound


def run_query(sparql_endpoint, query, fields):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    my_results=[]
    for r in results["results"]["bindings"]:
        temp=[]
        for field in fields:
            temp[field]=r[field]

        my_results.append(temp)


    return my_results
