from string import join
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import csv
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import elementtree.ElementTree as ET
import sys
import difflib

# indents XML file to achieve prettyprint format
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


def run_query(sparql_endpoint, query):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    my_results=[]
    if results:
        for r in results["results"]["bindings"]:
            fields = r.keys()
            temp={}
            for field in fields:
                temp[field]=r[field]["value"]

            my_results.append(temp)

        return my_results
        # return results["results"]["bindings"]
    else:
        return None


def write_file(filename, results,fields=None,print_metadata=True):

    if results:
        # output su file
        outputfile = open(filename,'w')
        if not fields:
            fields= results[0].keys()

        #stampa i metadati
        if print_metadata:
            for index, variable in enumerate(fields):
                outputfile.write('"%s"' % variable)
                if index < len(fields):
                    outputfile.write(",")

            outputfile.write("\n")

        #stampa i valori
        for r in results:
            for field in fields:
                if field in r.keys():
                    outputfile.write('"%s"' % unicode(r[field]).encode("utf-8"))
                outputfile.write(',')
            outputfile.write("\n")

        outputfile.close()


def create_diff(filename1, filename2):

    with open(filename1, 'r') as file1:
        content1 = file1.read().splitlines()
    with open(filename2, 'r') as file2:
        content2 = file2.read().splitlines()

    # trova le differenze fra i due file

    diff = difflib.unified_diff(
        content1,
        content2,
        n=0,
        fromfile=filename1,
        tofile=filename2,
        lineterm='')

    return '\n'.join(list(diff))
