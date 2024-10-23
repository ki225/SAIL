import requests

# Google Apps Script Web App URL
web_app_url = ""# 'https://script.google.com/macros/s/{SCRIPT_ID}/exec'

try:
    response = requests.get(web_app_url)
    # print(dir(response.))
    
    # 檢查是否成功接收到回應
    if response.status_code == 200:
        # 解析 JSON 內容
        data = response.json()
        print("成功接收到資料：", data)
    else:
        print("請求失敗，狀態碼：", response.status_code)

except requests.exceptions.RequestException as e:
    print("請求發生錯誤：", e)
