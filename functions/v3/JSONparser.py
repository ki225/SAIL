import json
from stu_response import json_data

data = json.loads(json_data) 

# 初始化要輸出的結果物件
ret = {
    "questions": [],
    "all_responses": []
}

# 取得問題列表 (假設位於 `sheet` 的第一列)
header = data["sheet"][0][5:]  # 從第6個欄位開始是問題
ret["questions"] = header

# 對每一問題提取所有學生的回覆
for i, question in enumerate(header):
    # 針對當前問題初始化
    question_responses = {
        "question": question,
        "student_responses": []
    }

    # 讀取學生的每一列回覆
    for row in data["sheet"][1:]:  # 跳過標題列
        student_response = {
            "student_id": row[4],  # 使用學號作為 ID
            "student_response": row[i + 5]  # 回覆在第6個欄位之後
        }
        question_responses["student_responses"].append(student_response)
    
    # 加入到結果的 all_responses
    ret["all_responses"].append(question_responses)

# 查看輸出的結果
print(json.dumps(ret, ensure_ascii=False, indent=4))
