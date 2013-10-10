import pprint
from utils.sparql_tools import run_query
from utils.utils import send_error_mail, write_file
from settings_local import *
import logging
import requests
from requests import ConnectionError
import gspread
import csv

def write_gdoc_log(worksheet, row, is_imported, log_msg):
    worksheet.update_acell('C'+str(row), is_imported)
    worksheet.update_acell('D'+str(row), log_msg)


script_name = "Votazioni non elettroniche"

error_messages={
    'address_fail':'Gdoc error: following address not found: %s',
    'api_connection_fail':'http error: Connection refused from the api for the following query: %s',
}


error_mail_body= {'gdoc': [],'api': []}


# Login with the script Google account
gc = gspread.login(g_user, g_password)

# open the list worksheet
list_sheet = None
try:
    list_sheet = gc.open_by_url(vne_list_address)
except gspread.exceptions.SpreadsheetNotFound:
    error_type = "address_fail"
    error_mail_body['gdoc'].append(error_messages[error_type]%vne_list_address)
    send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
    exit(0)

# Select worksheet by index. Worksheet indexes start from zero
list_worksheet = list_sheet.get_worksheet(0)
list_values = list_worksheet.get_all_values()

# lista delle votazioni da importare
vne_to_import = []

for vne_index, vne_address_row in enumerate(list_values):
    # estrae dal link la chiave del file
    # da https://docs.google.com/spreadsheet/ccc?key=0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp=drive_web#gid=0
    # a 0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp
    start = vne_address_row[1].find('key=')
    if start is not -1:
        end = vne_address_row[1].find('&', start)
        vne_key = vne_address_row[1][start+4:end]

        # se non e' stata importata prende la chiave e il titolo della votazione da importare
        if vne_address_row[2] != '1':
            vne_address = gdoc_prefix + vne_key
            vne_spreadsheet = None
            try:
                vne_spreadsheet = gc.open_by_url(vne_address)
            except gspread.exceptions.SpreadsheetNotFound:
                error_type = "address_fail"
                error_mail_body['gdoc'].append(error_messages[error_type]%vne_address)
                # scrive nella cella apposita l'errore nel ws lista
                write_gdoc_log(list_worksheet,vne_index+1, '0', error_messages[error_type]%vne_address)

            if vne_spreadsheet is not None:
                # Select worksheet by index. Worksheet indexes start from zero
                vne_worksheet = vne_spreadsheet.get_worksheet(0)
                # Find a cell with exact string value
                vne_titolo = vne_worksheet.acell('B9').value
                vne_seduta = vne_worksheet.acell('B8').value
                vne_to_import.append({'seduta': vne_seduta, 'titolo': vne_titolo, 'spreadsheet': vne_spreadsheet})


# controlla sulle api che la seduta in questione esista, vicerversa da' errore
# se la seduta esiste controlla che non ci sia gia' una votazione con il titolo in questione

if len(vne_to_import)>0:
    parlamento_api_sedute = parlamento_api_host  +parlamento_api_url +"/" + parlamento_api_leg_prefix + "/" + \
                            parlamento_api_sedute_prefix +"/"+ \
                            "?ramo=S&ordering=-numero&page_size=500&format=json"

    # TODO: prendere tutte le sedute dalle api, controllare che esistano le sedute delle votazioni n.e. da importare
    # TODO: per le sedute interessate, controllare che non esistano gia' delle votazioni con titolo = a quello da importare

    # alle votazioni n.e. da importare va assegnato numero 1 se la seduta non ha votazioni,
    # se la seduta ha votazioni gli va assegnato il numero successivo a quello dell'ultima votazione della seduta

    # r_sedute_list=None
    # try:
    #     r_sedute_list = requests.get(parlamento_api_sedute)
    # except requests.exceptions.ConnectionError:
    #     error_type = "api_connection_fail"
    #     error_mail_body['api'].append(error_messages[error_type]%parlamento_api_sedute)
    #     send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)
    #     exit(0)
    #
    # r_sedute_json = r_sedute_list.json()


    # DEBUG
    # vne_to_import = vne_to_import[0]

    for vne in vne_to_import:
        pprint.pprint(vne)

        # per ogni vne scarica un file json con metadati e voti
        vne_sheet = vne['spreadsheet']

        dati_generali_all = vne_sheet.worksheet("Dati generali Votazione").get_all_values()

        # prende i metadata della votazione
        dati_generali = {}

        for i in range(3,len(dati_generali_all)):
            if dati_generali_all[i][1] != '' and dati_generali_all[i][0] != 'carica':
                print u"riga:"+str(i)+u"-"+dati_generali_all[i][0]+u":" + dati_generali_all[i][1]
                dati_generali[
                    dati_generali_all[i][0]
                    ] = \
                    dati_generali_all[i][1].strip()

        if dati_generali['Ramo (4=camera, 5=senato)'] == '4':
            ramo = 'c'
        else:
            ramo = 's'

        # importa i voti
        voti = []

        # "id_politico",
        # "Cognome",
        # "Nome",
        # "Voto"

        voti_all = vne_sheet.worksheet("Voti dei Parlamentari").get_all_values()
        # rimuove dal foglio dei voti le colonne oltre la 4

        for voto in voti_all[1:]:
            # elimina eventuali spazi iniziali/finali dal valore del voto
            voto[4] = voto[4].strip()
            voti.append(voto[:4])

        vne_dict = {'metadati': dati_generali, 'voti' : voti}

        write_file(output_path+
                   ramo+"_vne_" +
                   dati_generali['N. seduta'] +
                   "_"+
                   dati_generali['Titolo votazione'][:10]+".json",
                   vne_dict,
                   fields=None,
                   print_metadata=False,
                   Json=True
            )
        
    send_error_mail(script_name, smtp_server, notification_system, notification_list, error_mail_body)




            
