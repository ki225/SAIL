from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_sheet_data():
    # 1. 設定 API 存取範圍
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # 2. 設定憑證
    # 方法一：使用服務帳戶金鑰(適合後端服務)
    SERVICE_ACCOUNT_FILE = 'path/to/service-account-key.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # 方法二：使用 OAuth 2.0 憑證(適合個人使用)
    """
    CREDENTIALS_FILE = 'path/to/credentials.json'
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    """
    
    # 3. 建立 service 物件
    service = build('sheets', 'v4', credentials=credentials)
    
    # 4. 指定試算表 ID 和範圍
    SPREADSHEET_ID = 'your-spreadsheet-id'  # 從試算表 URL 中取得
    RANGE_NAME = 'Sheet1!A1:E10'  # 要讀取的範圍
    
    # 5. 讀取資料
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    
    values = result.get('values', [])
    return values

if __name__ == '__main__':
    data = get_sheet_data()
    print(data)