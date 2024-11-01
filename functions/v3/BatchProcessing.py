# For a given question, extract the target responses from all student responses
async def main(args: Args) -> Output:
    params = args.params
    index = params["index"]
    all_res = params["all_responses"]
    response_size = len(all_res[index]["student_responses"])
    batch_size = response_size//4

    ret: Output = {
        "question_info": all_res[index]["question"],
        "stu_res_batch1": all_res[index]["student_responses"][:batch_size],
        "stu_res_batch2": all_res[index]["student_responses"][batch_size:2*batch_size],
        "stu_res_batch3": all_res[index]["student_responses"][2*batch_size:3*batch_size],
        "stu_res_batch4": all_res[index]["student_responses"][3*batch_size:],
    }
    return ret