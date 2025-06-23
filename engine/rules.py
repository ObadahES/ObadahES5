from experta import KnowledgeEngine, Rule, MATCH, TEST
from engine.facts import StudentFacts
import os
import json

class RecommendationRules(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []

        current_dir = os.path.dirname(os.path.abspath(__file__))
        courses_path = os.path.join(current_dir, '..', 'Data', 'courses.json')

        with open(courses_path, 'r', encoding='utf-8') as f:
            self.all_courses = json.load(f)

    @Rule(StudentFacts(current_level=MATCH.level, passed_courses=MATCH.passed,
                       failed_courses=MATCH.failed, max_hours=MATCH.max_hours))
    def recommend_courses(self, level, passed, failed, max_hours):
        recommended = []
        total_hours = 0

        for code in failed:
            course = next((c for c in self.all_courses if c["code"] == code), None)
            if course:
                hours = course.get("hours", 3)
                if total_hours + hours <= max_hours:
                    recommended.append(f"{course['code']} - {course['name']} ({hours}h)")
                    total_hours += hours

        for course in self.all_courses:
            code = course["code"]
            prereqs = course.get("prerequisites", [])
            hours = course.get("hours", 3)

            if code not in passed and code not in failed:
                if all(pr in passed for pr in prereqs):
                    if total_hours + hours <= max_hours:
                        recommended.append(f"{code} - {course['name']} ({hours}h)")
                        total_hours += hours

        self.recommendations.extend(recommended)

    @Rule(StudentFacts(current_level=MATCH.level, gpa=MATCH.gpa),
          TEST(lambda level, gpa: level >= 2 and gpa >= 3.5))
    def recommend_honor_student_courses(self):
        print("You are an honor student! It is recommended to enroll in advanced courses according to your plan.")

    @Rule(StudentFacts(goal='graduate_early', max_hours=MATCH.hours),
          TEST(lambda hours: hours >= 18))
    def recommend_heavy_load(self):
        print("You want to graduate early, we recommend taking the maximum allowed hours according to your plan.")

    @Rule(StudentFacts(gpa=MATCH.gpa),
          TEST(lambda gpa: gpa < 2.0))
    def recommend_focus_on_easy_courses(self):
        print("Low GPA detected, we recommend easy courses to raise your GPA such as: [CS110, HUM101]")

    @Rule(StudentFacts(passed_courses=MATCH.courses),
          TEST(lambda courses: "CS101" in courses and "CS102" not in courses))
    def recommend_cs102(self):
        print("You passed CS101, it is recommended to take CS102 next semester.")

    @Rule(StudentFacts(goal='raise_gpa'))
    def recommend_gpa_friendly_courses(self):
        print("Your goal is to raise your GPA, choose easy courses with high success rates.")

    @Rule(StudentFacts(max_hours=MATCH.hours),
          TEST(lambda hours: hours < 15))
    def recommend_fewer_courses(self):
        print("Your max allowed hours are low, choose only essential courses carefully.")

    @Rule(StudentFacts(current_level=MATCH.level),
          TEST(lambda level: level >= 4))
    def recommend_graduation_preparation(self):
        print("You are close to graduation, make sure to complete mandatory courses and remaining requirements.")
