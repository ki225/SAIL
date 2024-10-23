import requests

# 設定參數
API_KEY = ''  
SPREADSHEET_ID = ''  
RANGE_NAME = "sheet1!A1:B1"  

# 呼叫 Google Sheets API
url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={API_KEY}'
response = requests.get(url)

# 處理回應
if response.status_code == 200:
    data = response.json()
    values = data.get('values', [])
    print(values)
else:
    print(f'Error: {response.status_code}, {response.text}')