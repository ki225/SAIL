"""
Purpose
This Lambda function reads student responses from an Excel file stored in S3, analyzes the responses using AWS Bedrock, and generates an insightful report for each question in the form.

Input
Excel file containing student responses

Output
Insightful report for each question in the form
"""

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

def send_message_to_chatbot(message):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    return response.text


def analyze_all_responses_for_insight(question, all_responses):
    """Use AWS Bedrock to analyze all responses together and generate a single insight report."""

    combined_responses = "\n".join([f"學生ID: {stu_id}, 回覆: {response}" 
                                    for stu_id, response in all_responses.items()])
    prompt = f"""
                題目: {question}  
                學生回覆: {combined_responses}
                
                任務：
                1. 對所有學生的回覆進行綜合分析，生成整體見解報告。
                2. 總結整體回覆的主要觀點、共同點和不同點。
                3. 指出回答中的潛在優點與不足之處。
                4. 見解報告應該總結整體回覆的深度與有效性，並提供改善建議。
                5. 生成一份綜合見解報告，請按照以下 JSON 格式返回：
                
                請按照以下 JSON 格式回覆(每則說明小於30字元):
                {{
                    "overall_insight": "[總體見解]",
                    "main_points": "[主要觀點]",
                    "commonalities": "[共同點]",
                    "differences": "[不同點]",
                    "strengths": "[潛在優點]",
                    "weaknesses": "[不足之處]",
                    "depth_and_effectiveness": "[深度與有效性]",
                    "improvement_suggestions": "[改善建議]"
                }}

                """
   
    # Invoke the model for insight analysis
    insight_response = send_message_to_chatbot(prompt)
    
    # original_text = insight_response_body["content"][0]["text"]
    
    # # Clean and parse the topic text into JSON format
    # insight_report = None
    # print("original text: ", original_text)
    
    # try:
    #     # 將字串中的單引號替換為雙引號，並去除多餘的換行符號
    #     clean_text = original_text.replace("\n", "").replace("'", "\"")
    #     print(clean_text)
        
    #     # 確保清理後的字串符合 JSON 格式
    #     if clean_text.startswith("{") and clean_text.endswith("}"):
    #         insight_report = json.loads(clean_text)
    #     else:
    #         raise ValueError("Cleaned text is not a valid JSON object.")
    
    # except json.JSONDecodeError as e:
    #     print(f"Error decoding JSON: {e}")
    #     insight_report = {"error": "Invalid response format", "message": str(e)}
    # except ValueError as e:
    #     print(f"Value Error: {e}")
    #     insight_report = {"error": "Invalid response format", "message": str(e)}

    # print(f"Question: {question}")
    # print("Combined Insight Report: ", insight_report)
    
    return insight_response


def suggest_chart_types_based_on_insight(insight_report):
    """根據洞見報告生成圖表建議。"""

    prompt =  f"""
                對所有學生的回覆進行綜合分析，並產生結構化的數據報告，便於視覺化展示。

                1. 分析內容: {insight_report}
                
                2. 對所有學生的回覆進行綜合分析，並生成結構化的數據報告，便於視覺化展示。請輸出以下 JSON 格式的回應：

                    {{
                        "分析項目名稱": "[項目名稱]",
                        "標籤數據": {{
                            "標籤1": "數據1",
                            "標籤n": "數據n"
                        }},
                        "圖表類型": "[圖表類型]",
                        "圖表簡短說明": "[圖表簡短說明]"
                    }}

                3. 圖表建議: 圓餅圖，長條圖，折線圖、直方圖，請根據數據特點選擇合適的圖表類型。                                
                """
  
    # 調用模型以生成圖表建議
    chart_suggestion_response = send_message_to_chatbot(prompt)
    

    print("Chart Suggestions: ", chart_suggestion_response)
    return chart_suggestion_response

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

def get_student_responses(questions, sheet):
    student_responses = {}
    for row in sheet[1:]:
        student_id = row[4]
        student_responses[student_id] = {questions[i]: row[i+5] for i in range(0, len(questions)) if row[i] is not None}
    return student_responses


def lambda_handler(event, context):
    sheet = get_google_sheet()
    questions = get_questions(sheet[0])
    student_responses = get_student_responses(questions, sheet)

    insight_results = {}
    chart_suggestions = {}

    for target_question in questions:
        target_question_res = {}
        for student_id, responses in student_responses.items():
            if target_question in responses:
                target_question_res[student_id] = responses[target_question]
        insights = analyze_all_responses_for_insight(target_question, target_question_res)
        insight_results[target_question] = insights

        chart_suggestions[target_question] = suggest_chart_types_based_on_insight(str(insights))
        
lambda_handler(None, None)