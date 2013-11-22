import os.path

BASE_PATH = os.path.dirname(__file__)

osr_prefix = "http://dati.senato.it/osr/"
senatore_prefix = "http://dati.senato.it/senatore/"

sparql_senato = "http://dati.senato.it/sparql"
sparql_camera = "http://dati.camera.it/sparql"
date_format = '%Y%m%d'
legislatura_id = '17'

parlamento_api_host = "http://api3.staging.deppsviluppo.org/"
parlamento_api_url = "parlamento"
parlamento_api_leg_prefix = "legislatura-XVII"
parlamento_api_sedute_prefix = "sedute"
parlamento_api_votazioni_prefix = "votazioni"
parlamento_api_parlamentari_prefix = "parlamentari"
parlamento_api_senato_prefix = "S"
parlamento_api_camera_prefix = "C"

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
vne_prefix = "vne"


# Google Account credentials
g_user = 'USERNAME@gmail.com'
g_password = 'PASSW'


gdoc_prefix = 'https://docs.google.com/spreadsheet/ccc?key='
vne_list_address = 'LIST ADDRESS'

query_delay = 0.08


# local output folder
output_folder = 'output'
output_path = BASE_PATH + "/" + output_folder +"/"

notification_list = [
    "MAIL",
]

notification_system = {
    "name": "Parlamento_fetch",
    "mail": "noreply@openpolis.it"
}

smtp_server = 'SMTP SERVER ADDRESS'

no_difference_msg = "Nessuna differenza rilevata"

# Google Account credentials
g_user = 'USERNAME@gmail.com'
g_password = 'PASSWORD'



LOGGING = {

    'loggers': {
        'script': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
            }
    }
}