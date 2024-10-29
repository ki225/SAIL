"""
Purpose:
This Lambda function reads student responses from an Excel file stored in S3, analyzes the responses using AWS Bedrock, and generates attendent status, scores and insights for each student.

Input:
- Excel file containing student responses

Output:
- Attendance status
- Scores and insights for each student response
"""
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import google.generativeai as genai
from student_list import student_list
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

def analyze_responses(question, responses, start_index):
    rate_result = []
    batch_size = 7

    for i in range(start_index, len(responses.items()), batch_size):
        print(f"start from {i} to {i+batch_size}")

        # 獲取當前批次的學生 ID 和回應
        batch = {stu_id: responses[stu_id] for stu_id in list(responses.keys())[i:i + batch_size]}

        # Prepare the request body for scoring
        batch_responses = "\n".join([f"學生ID: {stu_id}, 回覆: {response}" for stu_id, response in batch.items()])

        stu_responses = f"""
                            題目: {question}  
                            學生回答: {batch_responses}
                            
                            請按照以下JSON格式回覆，不包含換行、空白，若有下一筆學生資料，請於大括號之間加入逗號區隔： 
                            {{"student_id": 學生ID,"score": 評分,"reason": 評分理由}},

                            規則：
                                1. 根據學生回答的努力程度和正確性打分（0-10）。
                                2. 若有文不對題、回應不完整、攻擊性言詞、答題態度輕浮，則斟酌扣分。
                                3. 評分理由請言簡意賅，在30字元內。

                            """
        # Invoke the model for scoring
        scoring_response = send_message_to_chatbot(stu_responses)
        print(f"問題: {question}")
        print(f"評分結果: {scoring_response}")

        clean_text = scoring_response.replace("\n", "").replace("'", "\"") # string format
        try:
            if clean_text.startswith("{") and clean_text.endswith("}"):
                clean_text = clean_text.replace('},','}},')
                clean_lst = clean_text.split('},')
                # turn str to dict
                rate_result_list = [json.loads(i) for i in clean_lst]
                rate_result.extend(rate_result_list) 
            else:
                raise ValueError("Cleaned text is not a valid JSON object.")
            
        except Exception as e:
            print(f"Error encountered: {e}\nthe text is : {clean_lst}")
            print(f"Retrying Bedrock request from {i}...")
            return rate_result + analyze_responses(question, responses, i) # rate_result is original list, so we need to add the new result to it.
        rate_result.append(scoring_response)

    print("Rate Results: ", rate_result)    
    return rate_result # [json1, json2, ...]

def calculate_attendance(attendence_list):
    """Calculate attendance based on the specified column index."""
    present_students = set(attendence_list)
    # Calculate absent students
    absent_students = [student_id for student_id in student_list if str(student_id) not in present_students]
    return present_students, absent_students

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
    attendence_list = []
    for row in sheet[1:]:
        student_id = row[4]
        attendence_list.append(student_id)
        student_responses[student_id] = {questions[i]: row[i+5] for i in range(0, len(questions)) if row[i] is not None}

    return student_responses, attendence_list

def lambda_handler(event, context):
    sheet = get_google_sheet()
    questions = get_questions(sheet[0])
    student_responses, attendence_list = get_student_responses(questions, sheet)
    
    # Calculate attendance (assuming attendance is in the 1st column, adjust index if needed)
    present_students, absent_students = calculate_attendance(attendence_list)
    print(f"出席人數: {len(present_students)}")
    print(f"缺席人數: {len(absent_students)}")

    results = {}
    for target_question in questions:
        target_question_res = {}
        for student_id, responses in student_responses.items():
            if target_question in responses:
                target_question_res[student_id] = responses[target_question]
        scores_list = analyze_responses(target_question, target_question_res, 0) # [json1, json2, ...]
        results[target_question] = scores_list

lambda_handler(None, None)