
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from botocore.config import Config
import google.generativeai as genai
from dotenv import load_dotenv
import os

# 載入 .env 檔案
load_dotenv()

FOLDER_ID = os.getenv('FOLDER_ID')
TARGET_SHEET_ID = os.getenv('TARGET_SHEET_ID')
RANGE_NAME = os.getenv('RANGE_NAME')
API_KEY = os.getenv('API_KEY')
genai.configure(api_key = API_KEY)

# https://github.com/boto/botocore/issues/882#issuecomment-338846339
# https://stackoverflow.com/questions/55016714/an-error-occurred-throttlingexception-when-calling-the-getdeployment-operation

# original problem: throttlingexception
# an error occurred (throttlingexception) when calling the invokemodel operation (reached max retries: 4): too many requests, please wait before trying again. you have sent too many requests. wait before trying again.\"}"
# config = Config(
#     retries = dict(
#         max_attempts = 10 # manually change 
#     )
# )

def send_message_to_chatbot(message):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    return response.text

def analyze_topics(questions):
    topic_text = send_message_to_chatbot(questions)
    return topic_text

# def upload_to_s3(data, bucket_name, file_name):
#     """Upload the data to S3."""
#     s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(data, ensure_ascii=False))  # 確保儲存為 UTF-8 編碼

def get_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('functions\\v3\service_acc_key.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('sc0003r-1')
    sheet_instance = sheet.get_worksheet(0)
    return sheet_instance.get_all_values()

def get_questions(row1st):
    # from first row to extract questions
    questions = row1st[5:] # first 5 columns are not questions
    return questions

def lambda_handler(event, context):
    sheet_content = get_google_sheet()
    questions = get_questions(sheet_content[0])
    user_input = f"""
                        表單內的所有問題: {str(questions)}
                        
                        任務:
                        1. 分析此表單內所有問題探討哪些主題。
                        2. 簡要概述該問題所涉及的領域。
                        3. 列出此表單的學習目標。
                        
                        
                        請按照以下 JSON 格式回覆:
                        {{
                            '主題': '[主題]',
                            '概述': '[概述]',
                            "學習目標": '[目標]'
                        }}
                        """
    bot_response = send_message_to_chatbot(user_input)
    print("Chatbot:", bot_response)
 
lambda_handler(None, None)