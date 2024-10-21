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
        "max_tokens": 150,
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
                        
                        請按照以下格式回覆:
                        主題: [主題]
                        概述: [概述]
                        學習目標: [目標]
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
    print(f"Question: {questions}\nAnalysis: {topic_text}\n")

    return topic_text


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
    
    # Perform topic analysis on all questions
    topic_analysis_results = analyze_topics(questions)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'question_topics': topic_analysis_results
        })
    }