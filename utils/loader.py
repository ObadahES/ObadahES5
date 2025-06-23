import json

def load_student_by_id(student_id, path="data/students.json"):
    with open(path, "r", encoding="utf-8") as file:
        students = json.load(file)
        for student in students:
            if student["id"] == student_id:
                return student
    return None
