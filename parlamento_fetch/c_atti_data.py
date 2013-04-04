#estrae tutti gli atti della Camera per una certa data e genera dei file XML:
# il primo contiene gli id dell'atto
# dopodiche' genera un file per ogni atto con tutti i dettagli relativi allo stesso


from utils.sparql import *
import sys


def do_something(args):

    for today in args:
        print "today:"+today

        query_atti="""

            PREFIX ocd: <http://dati.camera.it/ocd/>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
            PREFIX persona: <http://dati.camera.it/ocd/persona>
            PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>


            SELECT DISTINCT  SUBSTR(str(?atto),42) AS ?atto

            WHERE
            {
              ?atto a <http://dati.camera.it/ocd/atto> .
              ?atto dc:date ?date .



              FILTER(substr(?date, 1, 8) = '%s')
            }
            """ % today

        results_atti = run_query(sparql_camera, query_atti)
        write_file(output_folder+"c_atti_"+today,results_atti)

        # per ogni atto trovato estrae tutti i dettagli e li mette in un file
        for atto in results_atti:
            print atto["atto"]
            query_dettaglio="""

            PREFIX ocd: <http://dati.camera.it/ocd/>
               PREFIX dc: <http://purl.org/dc/elements/1.1/>
               PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
               PREFIX persona: <http://dati.camera.it/ocd/persona>
               PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>

            SELECT ?p ?v
            WHERE
            {
              ?atto a <http://dati.camera.it/ocd/atto> .
              ?atto ?p ?v
              FILTER(substr(str(?atto), 42) = '%s')
            }
            """ % atto["atto"]

            results_dettaglio = run_query(sparql_camera, query_dettaglio)
            write_file(output_folder+"c_atto_"+atto["atto"],results_dettaglio)


def main(args):
    do_something(args)

if __name__ == '__main__':
    main(sys.argv[1:])


