from utils.sparql_tools import *
import sys

# stampa la composizione dei gruppi parlamentari alla data

def do_fetch(args):

    for today in args:
        print "today:"+today

       #TODO: aggiungere riferimento legislatura e data odierna
        query="""
            PREFIX ocd: <http://dati.camera.it/ocd/>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>

            SELECT DISTINCT ?labelGruppo ?rif_leg ?firstName ?surname
            WHERE
            {

            ?gp a ocd:gruppoParlamentare.
            ?gp ocd:rif_leg ?rif_leg.
            ?gp rdfs:label ?labelGruppo.
            ?gp ocd:siComponeDi ?scd.

            ?scd ocd:startDate ?startDate.
            ?scd ocd:endDate ?endDate.
            ?scd ocd:rif_deputato ?deputato.

            ?deputato a ocd:deputato.
            ?deputato foaf:firstName ?firstName.
            ?deputato foaf:surname ?surname.


            FILTER(str(?rif_leg)="http://dati.camera.it/ocd/legislatura.rdf/repubblica_16")
            }
        """

        results_atti = run_query(sparql_camera, query_atti)
        write_file(output_path+atti_prefix+camera_prefix+results_atti[0]["rif_leg"]+prefix_separator+today,results_atti)

        # per ogni atto trovato estrae tutti i dettagli e li mette in un file
        for atto in results_atti:
            print atto["atto"]
            query_dettaglio="""

            PREFIX ocd: <http://dati.camera.it/ocd/>
               PREFIX dc: <http://purl.org/dc/elements/1.1/>
               PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
               PREFIX persona: <http://dati.camera.it/ocd/persona>
               PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>

            SELECT ?property ?value
            WHERE
            {
              ?atto a <http://dati.camera.it/ocd/atto> .
              ?atto ?property ?value.
              FILTER(substr(str(?atto), 42) = '%s')
            }
            """ % atto["atto"]

            results_dettaglio = run_query(sparql_camera, query_dettaglio)
            write_file(output_path+atto["atto"],results_dettaglio)


def main(args):
    do_fetch(args)

if __name__ == '__main__':
    main(sys.argv[1:])




