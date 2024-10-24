import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import boto3
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_sheets_service():
    """建立並返回Google Sheets API服務"""
    SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    # 從AWS Secrets Manager獲取服務帳號憑證
    # credentials = ServiceAccountCredentials.from_json_keyfile_name('service_acc_key.json', scope)
    secrets = boto3.client('secretsmanager')
    credentials_json = json.loads(
        secrets.get_secret_value(
            SecretId='google_service_account_key'
        )['SecretString']
    )

    
    
    credentials = service_account.Credentials.from_service_account_info(
        credentials_json, scopes=SCOPES)
    
    client = gspread.authorize(credentials)
    sheet = client.open('sc0003r-1')
    sheet_instance = sheet.get_worksheet(0)
    
    return sheet_instance
    # return build('sheets', 'v4', credentials=credentials)

def get_drive_service():
    """建立並返回Google Drive API服務"""
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # 從AWS Secrets Manager獲取服務帳號憑證
    secrets = boto3.client('secretsmanager')
    credentials_json = json.loads(
        secrets.get_secret_value(
            SecretId='google-service-account-key'
        )['SecretString']
    )
    
    credentials = service_account.Credentials.from_service_account_info(
        credentials_json, scopes=SCOPES)
    
    return build('drive', 'v3', credentials=credentials)

def list_sheets_in_folder(folder_id):
    """列出特定資料夾中的所有Google Sheets"""
    drive_service = get_drive_service()
    
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    
    return results.get('files', [])

def read_sheet_content(sheet_id, range_name):
    """讀取特定Google Sheet的內容"""
    sheets_service = get_sheets_service()
    
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])

def invoke_lambda_function(function_name, payload):
    """呼叫另一個Lambda函數"""
    lambda_client = boto3.client('lambda')
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',  # 非同步呼叫
        Payload=json.dumps(payload)
    )
    return response

def lambda_handler(event, context):
    # 設定參數
    FOLDER_ID = os.environ['GOOGLE_FOLDER_ID']  # 從環境變數獲取資料夾ID
    TARGET_SHEET_ID = os.environ['TARGET_SHEET_ID']  # 從環境變數獲取目標Sheet ID
    RANGE_NAME = 'Sheet1!A1:Z'  # 調整範圍根據需求
    
    try:
        # 1. 列出資料夾中的所有Sheets
        sheets = list_sheets_in_folder(FOLDER_ID)
        
        # 2. 讀取目標Sheet的內容
        sheet_content = read_sheet_content(TARGET_SHEET_ID, RANGE_NAME)
        
        # 3. 根據Sheet內容處理並呼叫對應的Lambda函數
        for row in sheet_content[1:]:  # 跳過標題行
            if len(row) >= 2:  # 確保行中有足夠的數據
                function_name = row[0]  # 假設第一列是Lambda函數名稱
                payload = json.loads(row[1])  # 假設第二列是JSON格式的參數
                
                # 呼叫對應的Lambda函數
                invoke_lambda_function(function_name, payload)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed sheets',
                'processed_sheets': len(sheets)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }