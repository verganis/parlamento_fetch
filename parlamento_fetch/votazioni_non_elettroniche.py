import pprint
from utils.sparql_tools import run_query
from utils.utils import send_error_mail, write_file
from settings_local import *
import logging
import requests
from requests import ConnectionError
import gspread

list_address = 'https://docs.google.com/spreadsheet/ccc?key=0Ampi1rC-fkEAdEVIZS02SzJFOWlOOXU0S251NWJtUWc#gid=0'

# Login with your Google account
gc = gspread.login(g_user, g_password)

# Or, if you feel really lazy to extract that key, paste the entire url
spreadsheet = gc.open_by_url(list_address)
# Select worksheet by index. Worksheet indexes start from zero
worksheet = spreadsheet.get_worksheet(0)
list_of_lists = worksheet.get_all_values()
pprint.pprint( list_of_lists)
