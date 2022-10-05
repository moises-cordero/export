import os.path
import string
import random

# import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import html_tables as htmlt


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HJpSC3dG7Hfbk5eEQ7Yi-DoTOoNTDUOaFoVmFaBwIRc'
VALUE_INPUT_OPTION = "RAW" # Options: USER_ENTERED -> Parsed / RAW -> Not parsed
COLUMNS = ['Vis', 'Description', 'Table', 'Variables', 'Formula',
           'Universe', 'Reason', 'Data_source', 'Image']
DIMENSIONS = {'Vis': 200, 'Description': 300, 'Table': 150, 'Variables': 400, 'Formula': 400,
              'Universe': 100, 'Reason': 100, 'Data_source': 300, 'Image': 100} 
END_ROW = 20
URL_BASE = 'https://docs.google.com/spreadsheets/d/'

def getCredentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created
    # automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

def get_spreadsheet():
    service = build('sheets', 'v4', credentials=getCredentials())
    return service.spreadsheets()

def setProperties(spreadsheet, sheets):
    requests = []
    for sid in sheets.values():
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1,
                          'startColumnIndex': 0, 'endColumnIndex': len(COLUMNS)
                          },
                'cell': {'userEnteredFormat': {'horizontalAlignment' : 'CENTER',
                                               "wrapStrategy": 'WRAP',
                                               'textFormat': {'bold': True}
                                               }
                        },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
        for i, col in enumerate(COLUMNS):
            requests.append({
                'updateDimensionProperties': {
                    'range': {'sheetId': sid, 'dimension': 'COLUMNS',
                              'startIndex': i, 'endIndex': i+1
                              },
                    'properties': {'pixelSize': DIMENSIONS[col]},
                    'fields': 'pixelSize'
                }
            })
    spreadsheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()

def create_tabs(spreadsheet, new_sheets):
    requests = []

    sheets = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute().get('sheets', None)
    aux_id = 0
    while aux_id in [s['properties']['sheetId'] for s in sheets]:
        aux_id = random.randint(0, 1000)

    # Append the request to add the auxiliar sheet
    requests.append({'addSheet': {'properties': {'title': 'aux_sheet', 'sheetId': aux_id}}})

    # Append the requests to delete all existing sheets
    for s in sheets:
        if s['properties']['title'] != 'aux_sheet':
            requests.append({'deleteSheet': {'sheetId': s['properties']['sheetId']}})

    # Append the requests to add the new sheets
    for title in new_sheets:
        requests.append({'addSheet': {'properties': {'title': title}}})

    # Append the request to delete the auxiliar sheet
    requests.append({'deleteSheet': {'sheetId': aux_id}})

    # Request to update the spreadsheet
    result = spreadsheet.batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                     body={'requests': requests}
                                     ).execute()
    sheets = {}
    for r in result['replies']:
        if r and r['addSheet']['properties']['title'] != 'aux_sheet':
            sheets[r['addSheet']['properties']['title']] = r['addSheet']['properties']['sheetId']
    setProperties(spreadsheet, sheets)

    return sheets

def get_visualizations(data, tab_name):
    # Get data from visualization table
    vis_table = data[f'{htmlt.VIS_TABLE_PREFIX} {tab_name}'] # Visualization table
    vis_columns = vis_table[0] # First row that contains the visualization table column titles
    tab_id = vis_table[1][vis_columns.index(htmlt.TAB_ID_COLUMN)] # Tab id
    visualizations = {}
    for v in vis_table[1:]: # Iterate over the visualization table
        vis_name = v[vis_columns.index(htmlt.VIS_NAME_COLUMN)] # Visualization name
        if isinstance(vis_name, str) and vis_name.replace("'", ""):
            vis_name = vis_name.replace("'", "")
            if vis_name not in visualizations:
                reason = v[vis_columns.index(htmlt.VIS_REASON_COLUMN)] # Reason column index
                visualizations[vis_name] = {'tables': {}, 'reason': reason}
            vis_id = v[vis_table[0].index(htmlt.VIS_ID_COLUNM)] # Visualization id

            # Get data from the last table
            lt_columns = data[htmlt.LAST_TABLE][0] # Last table columns
            tc_index = lt_columns.index(htmlt.LAST_TABLE_TABLE_COLUMN) # Table column index
            vc_index = lt_columns.index(htmlt.LAST_TABLE_VARIABLE_COLUMN) # Variable column index
            fc_index = lt_columns.index(htmlt.LAST_TABLE_FORMULA_COLUMN) # Formula column index
            for row in data[htmlt.LAST_TABLE][1:]: # Iterate over the last table
                table_name = row[tc_index]
                variable = row[vc_index]
                if isinstance(table_name, str) and table_name \
                    and isinstance(variable, str) and variable \
                    and tab_id == row[lt_columns.index(htmlt.TAB_ID_COLUMN)] \
                    and vis_id == row[lt_columns.index(htmlt.VIS_ID_COLUNM)]:
                    if table_name not in visualizations[vis_name]['tables']:
                        visualizations[vis_name]['tables'][table_name] = {}
                    if row[vc_index] not in visualizations[vis_name]['tables'][table_name]:
                        visualizations[vis_name]['tables'][table_name][row[vc_index]] = []
                    visualizations[vis_name]['tables'][table_name][row[vc_index]].append(row[fc_index])
    return vis_columns, visualizations

def get_values(vis_columns, visualizations, sheet_id):
    values = [COLUMNS] # Row #1: Add the column titles
    for vis, v in visualizations.items():
        if v:
            for table, variables in v['tables'].items():
                for variable, formula in variables.items():
                    tab_row = [""]*len(vis_columns) # Create a list with empty values
                    tab_row[COLUMNS.index('Vis')] = vis
                    tab_row[COLUMNS.index('Table')] = table
                    tab_row[COLUMNS.index('Variables')] = variable
                    tab_row[COLUMNS.index('Formula')] = ", ".join(formula)
                    tab_row[COLUMNS.index('Reason')] = v['reason']
                    sheet_url = os.path.join(URL_BASE, SPREADSHEET_ID, f'edit#gid={sheet_id}')
                    tab_row[COLUMNS.index('Data_source')] = sheet_url
                    values.append(tab_row)
    return values

def populate_data(tabs, data):
    spreadsheet = get_spreadsheet()
    sheets = create_tabs(spreadsheet, tabs)
    setProperties(spreadsheet, sheets)

    sheet_data = []

    # Iterate over the tabs
    for tab_name in tabs:
        vis_columns, visualizations = get_visualizations(data, tab_name)
        values = get_values(vis_columns, visualizations, sheets[tab_name])
        sheet_data.append({'range': f"{tab_name}!A1", 'values': values})
    body = {'valueInputOption': VALUE_INPUT_OPTION, 'data': sheet_data}

    # Request to update the spreadsheet
    spreadsheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def read():
    spreadsheet = get_spreadsheet()
    sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    end_column = string.ascii_uppercase[len(COLUMNS)-1]
    data = []
    for s in sheets:
        title = s["properties"]["title"]
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range=f'{title}!A1:{end_column}{END_ROW}').execute()
        values = result.get('values', [])
        for row in values[1:]:
            d = {'tab': title}
            row = row + ['']*(len(COLUMNS) - len(row))
            for i, val in enumerate(row):
               d[values[0][i]] = val
            data.append(d)
    return data
