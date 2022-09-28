import os.path

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
COLUMNS = ['Vis', 'Description', 'Table', 'Variables', 'Universe', 'Reason', 'Data_source', 'Image']
DIMENSIONS = {'Vis': 100, 'Description': 300, 'Table': 100, 'Variables': 300,
              'Universe': 100, 'Reason': 100, 'Data_source': 300, 'Image': 100} 

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

    # Append the request to add the auxiliar sheet
    requests.append({'addSheet': {'properties': {'title': 'aux_sheet', 'sheetId': 0}}})

    # Append the requests to delete all existing sheets
    sheets = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute().get('sheets', '')
    for s in sheets:
        if s['properties']['title'] != 'aux_sheet':
            requests.append({'deleteSheet': {'sheetId': s['properties']['sheetId']}})

    # Append the requests to add the new sheets
    for title in new_sheets:
        requests.append({'addSheet': {'properties': {'title': title}}})

    # Append the request to delete the auxiliar sheet
    requests.append({'deleteSheet': {'sheetId': 0}})

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

def get_values(data, tab_name):
    values = [COLUMNS] # Row #1: Add the column titles

    # Get data from visualization table
    vis_table = data[f'{htmlt.VIS_TABLE_PREFIX} {tab_name}'] # Visualization table
    vis_columns = vis_table[0] # First row that contains the visualization table column titles
    tab_id = vis_table[1][vis_columns.index(htmlt.TAB_ID_COLUMN)] # Tab id
    for v in vis_table[1:]: # Iterate over the visualization table
        vis_name = v[vis_columns.index(htmlt.VIS_NAME_COLUMN)] # Visualization name
        if isinstance(vis_name, str) and vis_name.replace("'", ""):
            vis_id = v[vis_table[0].index(htmlt.VIS_ID_COLUNM)] # Visualization id

            # Get data from the last table
            lt_columns = data[htmlt.LAST_TABLE][0] # Last table columns
            tc_index = lt_columns.index(htmlt.LAST_TABLE_TABLE_COLUMN) # Table column index
            vc_index = lt_columns.index(htmlt.LAST_TABLE_VARIABLE_COLUMN) #Variable column index
            tables = {}
            for row in data[htmlt.LAST_TABLE][1:]: # Iterate over the last table
                table_name = row[tc_index]
                if isinstance(table_name, str) and table_name \
                and tab_id == row[lt_columns.index(htmlt.TAB_ID_COLUMN)] \
                and vis_id == row[lt_columns.index(htmlt.VIS_ID_COLUNM)]:
                    if table_name not in tables:
                        tables[table_name] = [row[vc_index]]
                    else:
                        tables[table_name].append(row[vc_index])
            for key, variables in tables.items():
                tab_row = [""]*len(vis_columns) # Create a list with empty values
                tab_row[COLUMNS.index('Vis')] = vis_name.replace("'", "")
                tab_row[COLUMNS.index('Table')] = key
                tab_row[COLUMNS.index('Variables')] = ", ".join(variables)
                values.append(tab_row)
    return values

def populate_data(tabs, data):
    spreadsheet = get_spreadsheet()
    create_tabs(spreadsheet, tabs) 
    sheet_data = []

    # Iterate over the tabs
    for tab_name in tabs:
        values = get_values(data, tab_name)
        sheet_data.append({'range': f"{tab_name}!A1", 'values': values})
    body = {'valueInputOption': VALUE_INPUT_OPTION, 'data': sheet_data}

    # Request to update the spreadsheet
    spreadsheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def read():
    spreadsheet = get_spreadsheet()

    sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    for s in sheets:
        print(s["properties"]["title"])

    result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range='sheet1!A1:C4').execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return None

    # df = pd.DataFrame(values)
    # print(df)
    print(values)

    return values
