from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

# If modifying the scope, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']  # For read-only access, change if you need write access
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of your spreadsheet (from the Google Sheets URL)
SPREADSHEET_ID = ''
# The range of cells you want to read (e.g., 'Sheet1!A1:D10')
RANGE_NAME = 'Sheet1!F1:ZZ1'

def main():
    print("Reading data from Google Sheets...")
    creds = None
    # The token.json stores the user's access and refresh tokens and is created automatically
    # when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    print("Checking credentials...")

    # If no valid credentials are available, prompt the user to log in.
    if not creds or not creds.valid:
        print("No valid credentials found.")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("Credentials are valid.")

    # Build the service object for Sheets API
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API to read data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Data from Google Sheets:')
        for row in values:
            print(row)

if __name__ == '__main__':
    main()
