async def main(args: Args) -> Output:
    params = args.params
    attendence_list = params['attendence_list'] 

    # calculate absent students
    absent_students = []
    for student in student_list:
        if str(student) not in attendence_list:
            absent_students.append(student)
    absent_count = len(absent_students)
    
    # count total students and calculate attendance rate
    total_students = len(student_list)
    attendance_rate = (float(total_students - absent_count) / float(total_students)) * 100

    # Formatting outputs in Coze
    ret: Output = {
        "absent_students": absent_students,
        "attendance_rate": attendance_rate,
        "all_students": total_students
    }
    return ret