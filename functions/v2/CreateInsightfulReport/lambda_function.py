"""
Purpose
This Lambda function reads student responses from an Excel file stored in S3, analyzes the responses using AWS Bedrock, and generates an insightful report for each question in the form.

Input
Excel file containing student responses

Output
Insightful report for each question in the form
"""
import json
import boto3
from io import BytesIO
from GetGoogleSheet import get_sheets_service

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
        "max_tokens": 600,
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
    original_text = insight_response_body["content"][0]["text"]
    
    # Clean and parse the topic text into JSON format
    insight_report = None
    print("original text: ", original_text)
    
    try:
        clean_text = original_text.replace("\n", "").replace("'", "\"")
        # print(clean_text)
        
        if clean_text.startswith("{") and clean_text.endswith("}"):
            insight_report = json.loads(clean_text)
        else:
            raise ValueError("Cleaned text is not a valid JSON object.")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        insight_report = {"error": "Invalid response format", "message": str(e)}
    except ValueError as e:
        print(f"Value Error: {e}")
        insight_report = {"error": "Invalid response format", "message": str(e)}

    print(f"Question: {question}")
    print("Combined Insight Report: ", insight_report)
    
    return insight_report


def suggest_chart_types_based_on_insight(insight_report):
    """根據洞見報告生成圖表建議。"""
    
    modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
    accept = 'application/json'
    contentType = 'application/json'

    chart_suggestion_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        對所有學生的回覆進行綜合分析，並產生結構化的數據報告，便於視覺化展示。

                        1. 分析內容: {insight_report}
                        
                        2. 輸出格式: `[分析項目名稱] {{[標籤1 - 數據1] [標籤n - 數據n]}} [圖表類型] [圖表簡短說明]`，例如: `[正確回答百分比] {{[正確 - 70%] [錯誤 - 30%]}} [長條圖] [....根據題目敘述與學生回復狀況說明....]`。
                        
                        3. 圖表建議: 圓餅圖，長條圖，折線圖、直方圖，請根據數據特點選擇合適的圖表類型。                                
                        """
                    }
                ]
            }
        ]
    })

    # Invoke the model for chart suggestion
    chart_suggestion_response = bedrock.invoke_model(
        body=chart_suggestion_body,
        modelId=modelId,
        accept=accept,
        contentType=contentType
    )
    chart_suggestion_response_body = json.loads(chart_suggestion_response.get('body').read())
    chart_suggestions = chart_suggestion_response_body["content"][0]["text"]

    print("Chart Suggestions: ", chart_suggestions)
    return chart_suggestions

def upload_to_s3(data, bucket_name, file_name):
    """Upload the data to S3."""
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(data, ensure_ascii=False))  # 確保儲存為 UTF-8 編碼


def lambda_handler(event, context):
    sheet = get_sheets_service()

    # Assume the questions are in the first row
    questions = sheet.row_values(1)


    student_responses = {}
    for row in sheet.iter_rows(min_row=2, values_only=True):
        student_id = str(row[4])[:9]  # Extract student ID and ensure it's a string
        student_responses[student_id] = {questions[i]: row[i] for i in range(2, len(questions)) if row[i] is not None}

    insight_results = {}
    chart_suggestions = {}

    for target_question in questions[5:]:  
        specific_question_responses = {student_id: responses[target_question]
                                       for student_id, responses in student_responses.items()
                                       if target_question in responses}

        # Generate a combined insight report for all student responses to the current question
        insights = analyze_all_responses_for_insight(target_question, specific_question_responses)
        insight_results[target_question] = insights

        chart_suggestions[target_question] = suggest_chart_types_based_on_insight(str(insights))
        
    upload_to_s3({'insight_report': insight_results, 'chart_suggestions': chart_suggestions}, "analysis-results-reports", "insight_analysis_results.json")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'insight_report': insight_results,
            'chart_suggestions': chart_suggestions
        })
    }
