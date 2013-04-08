#estrae tutti gli atti della Camera per una certa data e genera dei file XML:
# il primo contiene gli id dell'atto
# dopodiche' genera un file per ogni atto con tutti i dettagli relativi allo stesso

from utils.sparql import *
import sys


def do_fetch(args):

    for today in args:


        query_construct="""
            PREFIX ocd: <http://dati.camera.it/ocd/>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
            PREFIX persona: <http://dati.camera.it/ocd/persona>

            CONSTRUCT
            {
            ?atto a <http://dati.camera.it/ocd/atto>.
            ?atto dc:date ?date .
            ?atto dc:title ?title .

            ?atto ocd:primo_firmatario ?primo_firmatario.
            ?atto ocd:altro_firmatario ?altro_firmatario.
            ?atto ocd:rif_richiestaParere ?rif_richiestaParere.
            ?atto ocd:rif_relatore ?rif_relatore.
            }
            WHERE
            {

            ?atto a <http://dati.camera.it/ocd/atto> .
            ?atto dc:date ?date .
            ?atto dc:title ?title .
            OPTIONAL{?atto ocd:primo_firmatario ?primo_firmatario.}
            OPTIONAL{?atto ocd:altro_firmatario ?altro_firmatario.}
            OPTIONAL{?atto ocd:rif_richiestaParere ?rif_richiestaParere.}
            OPTIONAL{?atto ocd:rif_relatore ?rif_relatore.}

            FILTER(str(?date) = '%s')
            }
            ORDER BY SUBSTR(str(?atto),42)
        """ % today

        results_constr = run_query(sparql_camera, query_construct)
        write_file(output_folder+atti_prefix+"query_constr_"+today,results_constr)

        query_test="""
            PREFIX ocd: <http://dati.camera.it/ocd/>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
            PREFIX persona: <http://dati.camera.it/ocd/persona>

            CONSTRUCT
            {
            ?atto a <http://dati.camera.it/ocd/atto>.
            ?atto dc:date ?date .
            ?atto dc:title ?title .

            ?atto ocd:primo_firmatario ?primo_firmatario.
            ?atto ocd:altro_firmatario ?altro_firmatario.
            ?atto ocd:rif_richiestaParere ?rif_richiestaParere.
            ?atto ocd:rif_relatore ?rif_relatore.
            }
            WHERE
            {

            ?atto a <http://dati.camera.it/ocd/atto> .
            ?atto dc:date ?date .
            ?atto dc:title ?title .
            OPTIONAL{?atto ocd:primo_firmatario ?primo_firmatario.}
            OPTIONAL{?atto ocd:altro_firmatario ?altro_firmatario.}
            OPTIONAL{?atto ocd:rif_richiestaParere ?rif_richiestaParere.}
            OPTIONAL{?atto ocd:rif_relatore ?rif_relatore.}

            FILTER(SUBSTR(str(?atto),42) = 'ac16_4007')
            }
            GROUP BY SUBSTR(str(?atto),42)
        """

        results_test = run_query(sparql_camera, query_test)
        write_file(output_folder+atti_prefix+"query_test_"+"ac16_4007",results_test)

        # query_atti="""
        #
        #     PREFIX ocd: <http://dati.camera.it/ocd/>
        #     PREFIX dc: <http://purl.org/dc/elements/1.1/>
        #     PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
        #     PREFIX persona: <http://dati.camera.it/ocd/persona>
        #     PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>
        #
        #
        #     SELECT DISTINCT
        #         SUBSTR(str(?atto),42) AS ?atto
        #         SUBSTR(str(?rif_leg),54) AS ?rif_leg
        #
        #
        #     WHERE
        #     {
        #       ?atto a <http://dati.camera.it/ocd/atto> .
        #       ?atto dc:date ?date .
        #       ?atto ocd:rif_leg ?rif_leg.
        #       FILTER(substr(?date, 1, 8) = '%s')
        #     }
        #     """ % today
        #
        # results_atti = run_query(sparql_camera, query_atti)
        # write_file(output_folder+atti_prefix+camera_prefix+results_atti[0]["rif_leg"]+prefix_separator+today,results_atti)
        #
        # # per ogni atto trovato estrae tutti i dettagli e li mette in un file
        # for atto in results_atti:
        #
        #     query_dettaglio="""
        #
        #     PREFIX ocd: <http://dati.camera.it/ocd/>
        #        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        #        PREFIX creator: <http://purl.org/dc/elements/1.1/creator>
        #        PREFIX persona: <http://dati.camera.it/ocd/persona>
        #        PREFIX atto: <http://dati.camera.it/ocd/attocamera.rdf/>
        #
        #     SELECT ?property ?value
        #     WHERE
        #     {
        #       ?atto a <http://dati.camera.it/ocd/atto> .
        #       ?atto ?property ?value.
        #       FILTER(substr(str(?atto), 42) = '%s')
        #     }
        #     """ % atto["atto"]
        #
        #     results_dettaglio = run_query(sparql_camera, query_dettaglio)
        #     write_file(output_folder+atto["atto"],results_dettaglio)


def main(args):
    do_fetch(args)

if __name__ == '__main__':
    main(sys.argv[1:])


