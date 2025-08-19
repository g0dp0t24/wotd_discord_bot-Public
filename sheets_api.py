import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sqlite3
import helper_functions as hf
from contextlib import closing
import os


# Path to the service account key file
script_dir = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(script_dir, 'dependencies','credentials.json') 
database_path = os.path.join(script_dir, 'hyperlinks.db')

# Authenticate using the service account key file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
credentials = credentials.with_universe_domain('googleapis.com')

# The ID and range of the spreadsheet.
SPREADSHEET_ID = hf.SPREADSHEET_ID

# Build the service
service = build('sheets', 'v4', credentials=credentials)
sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()

def get_sheet_names(spreadsheet_id=SPREADSHEET_ID):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet_names = [sheet['properties']['title'] for sheet in sheets]
    return sheet_names

def get_cell_value(sheet_name, cell_range, spreadsheet_id=SPREADSHEET_ID):
    range_name = f"{sheet_name}!{cell_range}"
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=range_name,
        fields="sheets.data.rowData.values.hyperlink,sheets.data.rowData.values.userEnteredValue"
    ).execute()
    
    try:
        cell_data = result['sheets'][0]['data'][0]['rowData']
        return cell_data
    except KeyError:
        return None

def populate_db():
    sheet_names = get_sheet_names(SPREADSHEET_ID)
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        for sheet_name in sheet_names:
            values_list = get_cell_value(sheet_name, 'C3:R60', SPREADSHEET_ID)
            if values_list is None:
                continue
            for row_idx, row in enumerate(values_list, start=3):
                for col_idx, cell_value in enumerate(row['values'], start=3):
                    cell = hf.row_col_to_a1(row_idx, col_idx)
                    if cell_value.get('hyperlink') and len(cell_value.get('userEnteredValue').get('stringValue').split()) < 3:
                        hyperlink = cell_value.get('hyperlink')
                        text_value = cell_value.get('userEnteredValue').get('stringValue')
                        definition_cell = hf.get_next_cell(cell)

                        cursor.execute('SELECT text_value, processed FROM hyperlinks WHERE text_value = ?', (text_value,))
                        result = cursor.fetchone()

                        if result:
                            if result[1] == 1:
                                continue
                            hf.log_duplicate(text_value)                            
                        else:
                            hf.log_entrySuccess(text_value)
                            cursor.execute('''
                                INSERT OR IGNORE INTO hyperlinks (sheet_name, cell, hyperlink, text_value, definition_cell, processed)
                                VALUES (?, ?, ?, ?, ?, 0)
                            ''', (sheet_name, cell, hyperlink, text_value, definition_cell))
                        cursor.execute('UPDATE hyperlinks SET processed = 1 WHERE sheet_name = ? and cell = ?', (sheet_name, cell))

        conn.commit()


def select_daily_hyperlink():
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM hyperlinks WHERE used = 0')
        rows = cursor.fetchall()
        
        if not rows:
            cursor.execute('UPDATE hyperlinks SET used = 0')
            conn.commit()
            cursor.execute('SELECT * FROM hyperlinks WHERE used = 0')
            rows = cursor.fetchall()
        
        selected = random.choice(rows)
        cursor.execute('UPDATE hyperlinks SET used = 1 WHERE id = ?', (selected[0],))
        conn.commit()
        
        return selected

def post_hyperlink_data(hyperlink_data):
    sheet, cell, hyperlink, text_value, definition_cell = hyperlink_data[1:6]
    def_list = get_cell_value(sheet, definition_cell, SPREADSHEET_ID)
    definition = def_list[0]['values'][0].get('userEnteredValue').get('stringValue')
    print(f"Hyperlink: {hyperlink}")
    print(f"Text: {text_value} on sheet:cell = {sheet}:{cell}")
    print(f"Definition: {definition}")

# selected_hyperlink = select_daily_hyperlink()

# post_hyperlink_data(selected_hyperlink)

populate_db() #comment out now for testing purposes - UNCOMMENT WHEN DONE