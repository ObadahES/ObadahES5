# import random
# from datetime import datetime

# # Load the previously generated courses
# with open("/mnt/data/courses.json", "r", encoding="utf-8") as f:
#     course_data = json.load(f)

# # Extract course codes
# course_codes = [course["code"] for course in course_data]

# # Generate 30 student entries
# students = []
# for i in range(30):
#     student_id = f"S{1000 + i}"
#     name = f"Student {i + 1}"
#     level = random.randint(1, 4)
#     gpa = round(random.uniform(1.5, 4.0), 2)
#     remaining_hours = random.randint(30, 120)
#     current_semester = random.choice(["Fall", "Spring"])
    
#     # Determine how many courses they passed/failed
#     passed = random.sample(course_codes, k=random.randint(5, 10))
#     remaining = list(set(course_codes) - set(passed))
#     failed = random.sample(remaining, k=random.randint(0, 2))
    
#     students.append({
#         "id": student_id,
#         "name": name,
#         "level": level,
#         "gpa": gpa,
#         "passed_courses": passed,
#         "failed_courses": failed,
#         "remaining_hours": remaining_hours,
#         "current_semester": current_semester
#     })

# # Save to file
# students_path = "/mnt/data/students.json"
# with open(students_path, "w", encoding="utf-8") as f:
#     json.dump(students, f, ensure_ascii=False, indent=2)

# students_path
