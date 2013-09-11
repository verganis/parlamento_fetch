from settings_local import *
import os.path

BASE_PATH = os.path.dirname(__file__)

sparql_senato = "http://dati.senato.it/sparql"
sparql_camera = "http://dati.camera.it/sparql"
date_format = '%Y%m%d'
legislatura_id = '17'

prefix_separator = "_"

senato_prefix = "s"
camera_prefix = "c"

atti_prefix = "a"
votazioni_prefix = "v"

incarichi_prefix = "i"
composizione_prefix = "composizione"
aggiunte_prefix = "aggiunte"
rimozioni_prefix = "rimozioni"
cambi_gruppo_prefix = "cgruppo"
cariche_prefix = "cariche"

seduta_prefix = "seduta"
votazione_prefix = "votazione"
votazioni_prefix = "votazioni"

query_delay = 0.01

output_folder = BASE_PATH + "/" + "output/"

notification_list = [
    "MAIL",
]

notification_system = {
    "name": "Parlamento_fetch",
    "mail": "noreply@openpolis.it"
}

smtp_server = 'SMTP SERVER ADDRESS'

no_difference_msg = "Nessuna differenza rilevata"

LOGGING = {

    'loggers': {
        'script': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
            }
    }
}