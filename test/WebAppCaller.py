# for calling Google Apps Script Web App API

import json
import requests

def lambda_handler(event, context):
    # Google Apps Script Web App URL
    web_app_url = 'https://script.google.com/macros/s/{SCRIPT_ID}/exec'
    
    try:
        # 發送GET請求到Google Apps Script Web App
        response = requests.get(web_app_url)
        response.raise_for_status()  # 確保請求成功

        # 解析回應的JSON資料
        data = response.json()

        if data['status'] == 'success':
            spreadsheets = data['spreadsheets']
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Successfully retrieved spreadsheet data',
                    'spreadsheets': spreadsheets
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Failed to retrieve spreadsheet data'})
            }

    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
