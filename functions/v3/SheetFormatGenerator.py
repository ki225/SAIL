# Turn the input data into a Googole Sheet format for plugin input. 
# The format should be a 2D list, where the first element is the header and the rest are the data rows.
# example: {"student_id": "A12345678", "score": 8, "reason": "答案正確，但缺乏關聯性"} should be turned into [["student_id", "score", "reason"], ["A12345678", 8, "答案正確，但缺乏關聯性"]]
async def main(args: Args) -> Output:
    # input
    params = args.params
    absent_list = params["absent_list"]
    questions = params["questions"]
    scoring_results = params["scoring_result"]

    # dictionary for temporary storage
    dict = {}

    # final output
    header = ["student_id"]
    output = list()
    output.append(header)

    # student id should be the first column
    for student_id in student_list:
        row = [str(student_id)]
        for i in range(len(questions)):
            row.append("") # score
            row.append("") # reason
        row.append("出席") # attendance
        dict[student_id] = row

    # student id + questions should be header
    # student result is a list of json strings that contain question and results 
    index = 0
    for i in scoring_results:
        # object i contains question and results
        question = i["question"]
        header.append(question + "_score")
        header.append(question + "_reason")
        stu_result = i["stu_result"]

        for student_result in stu_result:
            # student_result contains scoring_reason, student_id, student_score
            student_id = student_result["student_id"]
            score = student_result["student_score"]
            reason = student_result["scoring_reason"]
            if student_id in dict:
                dict[student_id][index*2+1] = score
                dict[student_id][index*2+2] = reason
            else:
                print(f"student_id {student_id} not found in student_list")
        index += 1

    # record absent students
    for stu_id in absent_list:
        dict[stu_id][2*len(questions)+1] = "缺席"

    # turn dictionary into 2D list
    for student_id, row in dict.items():
        output.append(row)

    ret: Output = {
        "sheet_content": output
    }
    return ret