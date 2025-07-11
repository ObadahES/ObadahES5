from experta import KnowledgeEngine, Rule, Fact, MATCH, TEST, DefFacts
from engine.facts import StudentFacts
import os
import json

class Course(Fact):
    pass

class NotFailed(Fact):
    pass

class PrerequisitesPassed(Fact):
    pass

class HighGPA(Fact):
    pass

class HighGradeInPrereqs(Fact):
    pass

class RecommendationRules(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.total_hours = 0
        self.pending_recommendations = [] 
        self.failed_courses_added = set()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        courses_path = os.path.join(current_dir, '..', 'Data', 'courses.json')

        with open(courses_path, 'r', encoding='utf-8') as f:
            self.all_courses = json.load(f)

    def add_recommendation(self, course, confidence):
        code = course["code"]
        name = course["name"]
        hours = course.get("hours", 3)

        rec = (confidence, f"{code} - {name} ({hours}h) - Confidence: {confidence:.2f}", hours)

        if code in self.failed_courses_added:
            if self.total_hours + hours <= self.max_hours:
                self.recommendations.append(rec[1])
                self.total_hours += hours
        else:
            self.pending_recommendations.append(rec)


    @DefFacts()
    def _initial_facts(self):
        if hasattr(self, 'student_data'):
            passed = {c['code']: c.get('grade', 0) for c in self.student_data.get('passed_courses', [])}
            failed_codes = [c['code'] for c in self.student_data.get('failed_courses', [])]
            gpa = self.student_data.get('gpa', 0.0)
            self.max_hours = self.student_data.get('max_hours', 18)

            for code in failed_codes:
                course = next((c for c in self.all_courses if c["code"] == code), None)
                if course:
                    self.add_recommendation(course, 0.6)

            yield StudentFacts(**self.student_data)
            yield Fact(failed_courses=failed_codes)
            yield Fact(passed_courses=list(passed.keys()))
            yield Fact(passed_grades=passed)

            for course in self.all_courses:
                yield Course(course=course)

    @Rule(Course(course=MATCH.course),
          Fact(failed_courses=MATCH.failed_list),
          TEST(lambda course, failed_list: course["code"] not in failed_list))
    def course_not_failed(self, course, failed_list):
        self.declare(NotFailed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_courses=MATCH.passed_list),
          TEST(lambda course, passed_list: all(pr in passed_list for pr in course.get("prerequisites", []))))
    def prerequisites_passed(self, course, passed_list):
        self.declare(PrerequisitesPassed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_grades=MATCH.grades),
          TEST(lambda course, grades: any(grades.get(pr, 0) >= 85 for pr in course.get("prerequisites", []))))
    def high_grade_in_prerequisites(self, course, grades):
        self.declare(HighGradeInPrereqs(code=course["code"]))

    @Rule(StudentFacts(gpa=MATCH.gpa),
          TEST(lambda gpa: gpa >= 3.5))
    def student_high_gpa(self):
        self.declare(HighGPA())

    @Rule(Course(course=MATCH.course),
        NotFailed(code=MATCH.code),
        PrerequisitesPassed(code=MATCH.code))
    def base_recommendation(self, course, code):
        self.add_recommendation(course, confidence=0.5)


    @Rule(Course(course=MATCH.course),
          NotFailed(code=MATCH.code),
          PrerequisitesPassed(code=MATCH.code),
          HighGradeInPrereqs(code=MATCH.code))
    def bonus_high_grade(self, course):
        self.add_recommendation(course, confidence=0.6)

    @Rule(Course(course=MATCH.course),
          NotFailed(code=MATCH.code),
          PrerequisitesPassed(code=MATCH.code),
          HighGPA())
    def bonus_high_gpa(self, course):
        self.add_recommendation(course, confidence=0.6)

    @Rule(Course(course=MATCH.course),
          NotFailed(code=MATCH.code),
          PrerequisitesPassed(code=MATCH.code),
          HighGradeInPrereqs(code=MATCH.code),
          HighGPA())
    def full_confidence_recommendation(self, course):
        self.add_recommendation(course, confidence=1.0)
