from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import csv
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound
import elementtree.ElementTree as ET
import sys


sparql_senato = "http://dati.senato.it/sparql-query"
sparql_camera = "http://dati.camera.it/sparql"
output_folder = "/home/nishant/workspace/parlamento_fetch/parlamento_fetch/output/"

prefix_separator = "_"
senato_prefix = "s"
camera_prefix = "c"
atti_prefix = "a"
votazioni_prefix ="v"
incarichi_prefix = "i"
composizione_prefix = "composizione"
aggiunte_prefix = "aggiunte"
rimozioni_prefix = "rimozioni"
cambi_gruppo_prefix = "cgruppo"
cariche_prefix = "cariche"



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




def run_query2(sparql_endpoint, query):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(XML)
    results = sparql.queryAndConvert()
    return results.toprettyxml()


def write_file2(filename, results):

    # output su file
    outputfile = open(filename,'w')
    outputfile.write("%s" %results)
    outputfile.close()


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


def write_file(filename, results):

    if results:
        # output su file
        outputfile = open(filename,'w')
        fields= results[0].keys()
        fields = ["s","p","o"]
        #stampa i metadati
        for index, variable in enumerate(fields):
            outputfile.write('"%s"' % variable)
            if index < len(fields):
                outputfile.write(",")

        outputfile.write("\n")

        #stampa i valori
        for r in results:
            for field in fields:
                outputfile.write('"%s",' % unicode(r[field]).encode("utf-8"))

            outputfile.write("\n")

        outputfile.close()