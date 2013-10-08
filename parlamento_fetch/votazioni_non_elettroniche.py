import pprint
from utils.sparql_tools import run_query
from utils.utils import send_error_mail, write_file
from settings_local import *
import logging
import requests
from requests import ConnectionError
import gspread
import csv

script_name = "Votazioni non elettroniche"

error_messages={
    'address_fail':'Gdoc error: following address not found: %s',

}


error_mail_body= {'gdoc': [],'api': []}


# Login with the script Google account
gc = gspread.login(g_user, g_password)

# open the list worksheet
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

for vne_sheet in list_values:
    # estrae dal link la chiave del file
    # da https://docs.google.com/spreadsheet/ccc?key=0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp=drive_web#gid=0
    # a 0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp
    start = vne_sheet[1].find('key=')
    if start is not -1:
        end = vne_sheet[1].find('&', start)
        vne_key = vne_sheet[1][start+4:end]

        # se non e' stata importata prende la chiave e il titolo della votazione da importare
        if vne_sheet[2] != '1':
            vne_address = gdoc_prefix + vne_key

            try:
                vne_sheet = gc.open_by_url(vne_address)
            except gspread.exceptions.SpreadsheetNotFound:
                error_type = "address_fail"
                error_mail_body['gdoc'].append(error_messages[error_type]%vne_address)
                # TODO: scrivere nella cella apposita l'errore nel ws lista

            # Select worksheet by index. Worksheet indexes start from zero
            vne_worksheet = vne_sheet.get_worksheet(0)
            # Find a cell with exact string value
            vne_titolo = vne_worksheet.acell('B9').value
            vne_seduta = vne_worksheet.acell('B8').value
            vne_to_import.append({'seduta': vne_seduta, 'titolo': vne_titolo, 'key': vne_key})


for vne in vne_to_import:
    pprint.pprint(vne)
