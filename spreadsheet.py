from __future__ import print_function

import os.path

# import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HJpSC3dG7Hfbk5eEQ7Yi-DoTOoNTDUOaFoVmFaBwIRc'

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

def create_tabs(new_sheets):
    try:
        creds = getCredentials()
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet = service.spreadsheets()

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

        # Apply changes to the spreadsheet
        spreadsheet.batchcreate_tabs(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()
    except HttpError as ex:
        raise Exception(f'{ex.error_details}') from ex

def populate_data_to_spreadsheet(data):
    print(data)

def read():
    creds = getCredentials()
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()

        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        for s in sheets:
            print(s["properties"]["title"])

        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range='sheet1!A1:C4').execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        # df = pd.DataFrame(values)
        # print(df)
        print(values)
        # print('Name, Major:')
        # for row in values:
        #     # Print columns A and E, which correspond to indices 0 and 4.
        #     print('%s, %s' % (row[0], row[2]))
    except HttpError as ex:
        raise Exception(f'{ex.error_details}') from ex

def main():
    # read()
    create_tabs(["sheet #1", "sheet #2", "sheet #3"])

if __name__ == '__main__':
    main()