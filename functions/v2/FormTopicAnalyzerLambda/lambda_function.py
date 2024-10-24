"""
Purpose
This Lambda function reads student responses from an Excel file stored in S3, analyzes the responses using AWS Bedrock, and generates topics for each question in the form.

Input
Excel file containing student responses

Output
Topics for each question in the form
"""
import json
import boto3
import openpyxl
from io import BytesIO

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")

def analyze_topics(questions):
    """ Perform text analysis on each question in the form to identify the topics being discussed """

    modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
    accept = 'application/json'
    contentType = 'application/json'
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
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
                    }
                ]
            }
        ]
    })
    
    # call the Bedrock API to perform topic analysis
    topic_response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(topic_response.get('body').read())
    
    # get the topic and summary from the model response
    topic_text = response_body["content"][0]["text"]
    
    # Clean and parse the topic text into JSON format
    topic_analysis = None
    print("original text: ", topic_text)
    
    try:
        # 將字串中的單引號替換為雙引號，並去除多餘的換行符號
        clean_text = topic_text.replace("\n", "").replace("'", "\"")
        
        # 確保清理後的字串符合 JSON 格式
        if clean_text.startswith("{") and clean_text.endswith("}"):
            topic_analysis = json.loads(clean_text)
        else:
            raise ValueError("Cleaned text is not a valid JSON object.")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        topic_analysis = {"error": "Invalid response format", "message": str(e)}
    except ValueError as e:
        print(f"Value Error: {e}")
        topic_analysis = {"error": "Invalid response format", "message": str(e)}
        

    return topic_analysis

def upload_to_s3(data, bucket_name, file_name):
    """Upload the data to S3."""
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(data, ensure_ascii=False))  # 確保儲存為 UTF-8 編碼


def lambda_handler(event, context):
    # Excel files are stored in S3 and are triggered by S3 events
    bucket_name = "student-excel-files"
    file_name = "test.xlsx"    
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    excel_file = BytesIO(response['Body'].read())
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook.active
    
    # Extract the questions from the first row of the Excel sheet
    questions = [cell.value for cell in sheet[1]]
    target_questions = questions[5:]
    
    # Perform topic analysis on all questions
    topic_analysis_results = analyze_topics(target_questions)

    print({'question_topics': topic_analysis_results})
    upload_to_s3({'question_topics': topic_analysis_results}, "analysis-results-reports", "topic_analysis_results.json")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'question_topics': topic_analysis_results
        })
    }