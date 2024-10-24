import json
import boto3
import plotly.graph_objects as go
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Read the analysis results from S3
    bucket_name = 'analysis-results-reports'
    file_key = 'analysis-results.json'
    
    s3_response = s3.get_object(Bucket=bucket_name, Key=file_key)
    analysis_data = json.loads(s3_response['Body'].read().decode('utf-8'))

    # Extract the chart information using AWS Bedrock
    chart_info = extract_chart_info_with_bedrock(analysis_data)
    
    # Prepare the data for visualization
    visualization_data = prepare_visualization_data(chart_info)
    
    # Generate visualization report using Plotly
    image_url = create_visualization_report(visualization_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Visualization report created successfully!', 'image_url': image_url})
    }

def extract_chart_info_with_bedrock(text):
    """
    使用 AWS Bedrock 從自然語言描述中提取圖表類型、主題、標籤和數據。
    """
    
    # 初始化 AWS Bedrock 客戶端
    client = boto3.client('bedrock', region_name='us-east-1')

    prompt = (
        f"從以下自然語言描述中提取圖表類型、主題、標籤和數據:\n"
        f"描述: \"{text}\"\n"
        f"請以以下格式返回: [圖表類型][主題][標籤/數據對]\n"
    )

    try:
        # 調用 Bedrock 模型生成內容
        response = client.invoke_model(
            modelId='your-model-id',  # 替換為你的模型 ID
            body={
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.7
            }
        )
        
        # 提取模型的回應
        result = response['body'].read().decode('utf-8').strip()
        return result
    except Exception as e:
        return f"錯誤: {e}"


def prepare_visualization_data(analysis_data):
    """
    Turn the analysis data into a format suitable for visualization.
    """
    visualization_data = []

    for question, result in analysis_data.items():
        for stu_id, details in result.items():
            score = details['score']
            key_points = details['key_points']
            
            visualization_data.append({
                'student_id': stu_id,
                'question': question,
                'score': score,
                'key_points': key_points
            })

    return visualization_data

def create_visualization_report(visualization_data):
    """
    Generate charts using Plotly and store them in S3.
    """
    # 假設我們要生成一個圓餅圖來展示分數
    scores = [data['score'] for data in visualization_data]
    labels = [f"ID: {data['student_id']}" for data in visualization_data]

    # 使用 Plotly 繪製圖表
    fig = go.Figure(data=[go.Pie(labels=labels, values=scores, hole=.3)])
    fig.update_layout(title_text='學生分數圓餅圖')

    # 儲存圖表為圖片
    image_stream = BytesIO()
    fig.write_image(image_stream, format='png')
    image_stream.seek(0)

    # 將圖片上傳至 S3
    s3_bucket = 'analysis-results-reports'
    s3_key = 'visualization-report.png'
    s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=image_stream.getvalue(), ContentType='image/png')

    # 返回圖片的 S3 URL
    return f'https://{s3_bucket}.s3.amazonaws.com/{s3_key}'

