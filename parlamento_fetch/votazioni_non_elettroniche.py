import pprint
from utils.sparql_tools import run_query
from utils.utils import send_error_mail, write_file
from settings_local import *
import logging
import requests
from requests import ConnectionError
import gspread
import csv

list_address = 'https://docs.google.com/spreadsheet/ccc?key=0Ampi1rC-fkEAdEVIZS02SzJFOWlOOXU0S251NWJtUWc&single=true&gid=0&output=csv'

# Login with your Google account
# gc = gspread.login(g_user, g_password)
#
# # Or, if you feel really lazy to extract that key, paste the entire url
# list_sheet = gc.open_by_url(list_address)
# # Select worksheet by index. Worksheet indexes start from zero
# list_worksheet = list_sheet.get_worksheet(0)
# list_values = list_worksheet.get_all_values()


# acquisisce la lista di votazioni non elettroniche concluse
list_r = requests.get(list_address)
list_data = list_r.text
list_reader = csv.reader(list_data.splitlines(), delimiter=',')
for vne_sheet in list_reader:
    # estrae dal link la chiave del file
    # da https://docs.google.com/spreadsheet/ccc?key=0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp=drive_web#gid=0
    # a 0AnpZgx29pl3adGJUMHFVRHpudnI0MDVlY1lnRHBNNmc&usp
    start = vne_sheet[1].find('key=')
    if start is not -1:
        end = vne_sheet[1].find('&', start)
        vne_key = vne_sheet[1][start+4:end]

        # apre il file con la chiave di cui sopra e prende il titolo della votazione
        vne_resume_address = gdoc_prefix + vne_key + '&single=true&gid=0&output=csv'
        print vne_resume_address
        vne_resume_r = requests.get(vne_resume_address)
        vne_resume_data = vne_resume_r.text
        vne_resume_reader = csv.reader(vne_resume_data.splitlines(), delimiter=',')

        for vne_resume_row in vne_resume_reader:
            pprint.pprint(vne_resume_row)
            # if vne_resume_row[0] == 'Titolo votazione':
            #     print vne_resume_row[1]




