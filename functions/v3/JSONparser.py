import json
async def main(args: Args):
    params = args.params
    data = json.loads(params['json_input']) 

    ret = {
        "questions": [],
        "all_responses": [],
        "attendence_list": []
    }

    # get the questions from the first row
    header = data["sheet"][0][5:]  # the first 5 columns are not questions
    ret["questions"] = header

    # get the student responses for each question
    for i, question in enumerate(header):
        question_responses = {
            "question": question,
            "student_responses": []
        }

        # read each row and extract the student response
        for row in data["sheet"][1:]:  # skip the first row
            if row[4] not in ret["attendence_list"]:
                ret["attendence_list"].append(row[4])
            student_response = {
                "student_id": row[4],  # student ID is in the 5th column
                "student_response": row[i + 5]  
            }
            question_responses["student_responses"].append(student_response)
        
        # append the responses for this question
        ret["all_responses"].append(question_responses)

    # print(json.dumps(ret, ensure_ascii=False, indent=4))
    return ret