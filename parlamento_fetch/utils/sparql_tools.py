import urllib2
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import sys
import time
from requests import ConnectionError


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    src = sys.stdin


def run_query(sparql_endpoint, query, query_delay=0, Json=False):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # sleep is needed to preserve sparql connection, otherwise sparql end point can go down
    if query_delay>0:
        time.sleep(query_delay)
    try:
        results = sparql.query().convert()
    except (urllib2.HTTPError, EndPointNotFound, urllib2.URLError):
        raise ConnectionError(query)



    if Json is True:
        # riorganizza la struttura dati
        pretty_result={}
        for row in results['results']['bindings']:
            if row['field']['value'] not in pretty_result.keys():

                pretty_result[row['field']['value']]=[]
            pretty_result[row['field']['value']].append(row['value']['value'])

        return pretty_result

    my_results=[]
    if results:
        for r in results["results"]["bindings"]:
            fields = r.keys()
            temp={}
            for field in fields:
                temp[field]=r[field]["value"]

            my_results.append(temp)

        return my_results

    else:
        return None

