from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound

sparql_senato = "http://dati.senato.it/sparql-query"
sparql_camera = "http://dati.camera.it/sparql"


output_folder = "/home/nishant/workspace/parlamento_fetch/parlamento_fetch/output/"


def run_query(sparql_endpoint, query, fields):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    my_results=[]
    for r in results["results"]["bindings"]:
        temp={}
        for field in fields:
            if field in r.keys():
                temp[field] = r[field]["value"]
            else:
                temp[field]= None

        my_results.append(temp)

    return my_results


def write_to_file(filename,fields, results):

    # output su file
    outputfile = open( filename,'w')
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