import json
import boto3
from io import BytesIO
import openpyxl

# Initialize AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")

def analyze_all_responses_for_insight(question, all_responses):
    """Use AWS Bedrock to analyze all responses together and generate a single insight report."""
    
    modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
    accept = 'application/json'
    contentType = 'application/json'

    combined_responses = "\n".join([f"學生ID: {stu_id}, 回覆: {response}" 
                                    for stu_id, response in all_responses.items()])
    
    insight_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        題目: {question}  
                        學生回覆: {combined_responses}

                        任務：
                            1. 對所有學生的回覆進行綜合分析，生成整體見解報告。
                            2. 總結整體回覆的主要觀點、共同點和不同點。
                            3. 指出回答中的潛在優點與不足之處。
                            4. 見解報告應該總結整體回覆的深度與有效性，並提供改善建議。
                            5. 生成一份綜合見解報告。
                        """
                    }
                ]
            }
        ]
    })

    # Invoke the model for insight analysis
    insight_response = bedrock.invoke_model(
        body=insight_body,
        modelId=modelId,
        accept=accept,
        contentType=contentType
    )
    insight_response_body = json.loads(insight_response.get('body').read())
    
    # Extract the combined insight report
    insight_report = insight_response_body["content"][0]["text"]

    print(f"Question: {question}")
    print("Combined Insight Report: ", insight_report)
    return insight_report


def lambda_handler(event, context):
    bucket_name = "student-excel-files"
    file_name = "test.xlsx"
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    excel_file = BytesIO(response['Body'].read())
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook.active

    questions = [cell.value for cell in sheet[1]]

    student_responses = {}
    for row in sheet.iter_rows(min_row=2, values_only=True):
        student_id = str(row[4])[:9]  # Extract student ID and ensure it's a string
        student_responses[student_id] = {questions[i]: row[i] for i in range(2, len(questions)) if row[i] is not None}

    insight_results = {}

    for target_question in questions[5:]:  
        specific_question_responses = {student_id: responses[target_question]
                                       for student_id, responses in student_responses.items()
                                       if target_question in responses}

        # Generate a combined insight report for all student responses to the current question
        insights = analyze_all_responses_for_insight(target_question, specific_question_responses)
        insight_results[target_question] = insights

    return {
        'statusCode': 200,
        'body': json.dumps({
            'combined_insight_report': insight_results
        })
    }
