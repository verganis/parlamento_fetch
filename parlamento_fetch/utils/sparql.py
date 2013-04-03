from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import elementtree.ElementTree as ET
import sys


sparql_senato = "http://dati.senato.it/sparql-query"
sparql_camera = "http://dati.camera.it/sparql"
output_folder = "/home/nishant/workspace/parlamento_fetch/parlamento_fetch/output/"


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


def run_query(sparql_endpoint, query, fields):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(XML)
    results = sparql.queryAndConvert()
    return results.toprettyxml()



def write_file(filename, results):

    # output su file
    outputfile = open(filename,'w')
    outputfile.write("%s" %results)
    outputfile.close()



def write_csv(filename,fields, results):

    # output su file
    outputfile = open(filename,'w')
    #stampa i metadati
    for index, variable in enumerate(fields):
        outputfile.write('"%s"' % variable)
        if index < len(fields):
            outputfile.write(",")

    outputfile.write("\n")

    #stampa i valori
    for r in results:
        for field in fields:
            if field in r.keys():
                outputfile.write('"%s",' % unicode(r[field]).encode("utf-8"))
            else:
                outputfile.write('"",')

        outputfile.write("\n")

    outputfile.close()