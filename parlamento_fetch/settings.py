sparql_senato = "http://dati.senato.it/sparql"
sparql_camera = "http://dati.camera.it/sparql"
date_format='%Y%m%d'
legislatura_id ='16'

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

notification_list=[
    "MAIL",
    ]

notification_system={
    "name":"Parlamento_fetch",
    "mail":"noreply@openpolis.it"
}

smtp_server = 'SMTP SERVER ADDRESS'