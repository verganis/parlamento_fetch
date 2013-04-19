#estrae tutti gli atti della Camera per una certa data e genera dei file XML:
# il primo contiene gli id dell'atto
# dopodiche' genera un file per ogni atto con tutti i dettagli relativi allo stesso

from utils.sparql import *
import sys


def do_fetch(args):

    for today in args:

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

            query_atto="""
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
                ?atto ocd:rif_assegnazione ?rif_assegnazione.
                ?rif_assegnazione ocd:sede ?sedeAssegnazione.
                ?atto ocd:rif_statoIter ?rif_statoIter.
                ?rif_statoIter ocd:title ?titoloIter.
                ?rif_statoIter ocd:date ?dataIter.
                ?atto ocd:rif_trasmissione ?rif_trasmissione.
                ?rif_trasmissione ocd:rif_attoSenato ?rif_attoSenato.
                ?atto ocd:rif_dibattito ?rif_dibattito.

                }
                WHERE
                {

                ?atto a <http://dati.camera.it/ocd/atto> .
                ?atto dc:date ?date .
                ?atto dc:title ?title .

                ?atto ocd:rif_statoIter ?rif_statoIter.
                ?rif_statoIter a <http://dati.camera.it/ocd/statoIter>.
                ?rif_statoIter dc:date ?dataIter.
                ?rif_statoIter dc:title ?titoloIter.

                OPTIONAL{?atto ocd:primo_firmatario ?primo_firmatario.}
                OPTIONAL{?atto ocd:altro_firmatario ?altro_firmatario.}
                OPTIONAL{?atto ocd:rif_richiestaParere ?rif_richiestaParere.}
                OPTIONAL{?atto ocd:rif_relatore ?rif_relatore.}
                OPTIONAL{
                    ?atto ocd:rif_assegnazione ?rif_assegnazione.
                    ?rif_assegnazione a ocd:assegnazione .
                    ?rif_assegnazione ocd:sede ?sedeAssegnazione.
                }
                OPTIONAL{
                    ?atto ocd:rif_trasmissione ?rif_trasmissione.
                    ?rif_transmissione a ocd:trasmissione.
                    ?rif_trasmissione ocd:rif_attoSenato ?rif_attoSenato.

                }
                OPTIONAL {
                    ?atto ocd:rif_dibattito ?rif_dibattito.

                }

                FILTER(substr(str(?atto),42) = '%s')
                }

            """ % atto["atto"]

            results_atto = run_query(sparql_camera, query_atto)
            write_file(output_folder+atto["atto"],results_atto, ["s","p","o"], False)


def main(args):
    do_fetch(args)

if __name__ == '__main__':
    main(sys.argv[1:])


