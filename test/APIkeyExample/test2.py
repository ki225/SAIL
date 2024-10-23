import gspread
import httplib2
from apiclient import discovery
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets']
credentials = 
google_spreadsheet_connection = gspread.authorize(credentials)
wks = google_spreadsheet_connection.open("spreadsheet_name")
worksheet = wks.get_worksheet(0)
df = get_as_dataframe(worksheet, evaluate_formulas=True, index='false')

# I added below script.
service = discovery.build(
    'sheets', 'v4', http=credentials.authorize(httplib2.Http()))

spreadsheet_id = '###'  # Please set the Spreadsheet ID here.
ranges = ['Sheet1!A2:B']  # For example, when you want to retrieve the note from the cells "A2:B" of "Sheet1", please use this.

fields = 'sheets(data(rowData(values(note,userEnteredValue))))'
request = service.spreadsheets().get(
    spreadsheetId=spreadsheet_id, ranges=ranges, fields=fields)
response = request.execute()
print(response)