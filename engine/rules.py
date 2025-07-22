from experta import KnowledgeEngine, Rule, Fact, MATCH, TEST, DefFacts
from .facts import *

class RecommendationRules(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.total_hours = 0
        self.failed_courses_added = set()
        self.study_load_analysis = {
            'easy': {'count': 0, 'hours': 0},
            'medium': {'count': 0, 'hours': 0},
            'hard': {'count': 0, 'hours': 0}
        }
        self.all_courses = [] 

    @DefFacts()
    def _initial_facts(self):
        if hasattr(self, 'student_data'):
            passed = {c['code']: c.get('grade', 0) for c in self.student_data.get('passed_courses', [])}
            failed_codes = [c['code'] for c in self.student_data.get('failed_courses', [])]
            gpa = self.student_data.get('gpa', 0.0)
            self.max_hours = self.student_data.get('max_hours', 18)

            for code in failed_codes:
                self.declare(FailedCourse(code=code))

            yield StudentFacts(**self.student_data)
            yield Fact(failed_courses=failed_codes)
            yield Fact(passed_courses=list(passed.keys()))
            yield Fact(passed_grades=passed)

            for course in self.all_courses:
                yield Course(course=course)
                if course.get("category") == "mandatory" or course["type"].endswith("Mandatory Requirements"):
                    yield MandatoryCourse(code=course["code"])
                else:
                    yield ElectiveCourse(code=course["code"])

    @Rule(FailedCourse(code=MATCH.code),
          Course(course=MATCH.course),
          TEST(lambda code, course: code == course["code"]),
          salience=1000)
    def handle_failed_courses(self, course):
        self.declare(RecommendationReady(code=course["code"], is_failed=True, base_confidence=0.8))

    @Rule(Course(course=MATCH.course),
          TEST(lambda course: course.get("difficulty_ratio", 0.3) < 0.3))
    def difficulty_easy(self, course):
        self.declare(DifficultyLevel(code=course["code"], level='easy'))

    @Rule(Course(course=MATCH.course),
          TEST(lambda course: 0.3 <= course.get("difficulty_ratio", 0.3) < 0.5))
    def difficulty_medium(self, course):
        self.declare(DifficultyLevel(code=course["code"], level='medium'))

    @Rule(Course(course=MATCH.course),
          TEST(lambda course: course.get("difficulty_ratio", 0.3) >= 0.5))
    def difficulty_hard(self, course):
        self.declare(DifficultyLevel(code=course["code"], level='hard'))

    @Rule(StudentFacts(gpa=MATCH.gpa),
          TEST(lambda gpa: gpa >= 3.5))
    def student_high_gpa(self):
        self.declare(HighGPA())

    @Rule(Course(course=MATCH.course),
          Fact(failed_courses=MATCH.failed_list),
          TEST(lambda course, failed_list: course["code"] not in failed_list))
    def course_not_failed(self, course, failed_list):
        self.declare(NotFailed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_courses=MATCH.passed_list),
          TEST(lambda course, passed_list: all(pr in passed_list for pr in course.get("prerequisites", [])) if course.get("prerequisites") else True))
    def prerequisites_passed(self, course, passed_list):
        self.declare(PrerequisitesPassed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_grades=MATCH.grades),
          TEST(lambda course, grades: any(grades.get(pr, 0) >= 85 for pr in course.get("prerequisites", []))))
    def high_grade_in_prerequisites(self, course, grades):
        self.declare(HighGradeInPrereqs(code=course["code"]))
    @Rule(
        (MandatoryCourse(code=MATCH.code) | ElectiveCourse(code=MATCH.code)),
        Course(course=MATCH.course),
        NotFailed(code=MATCH.code),
        PrerequisitesPassed(code=MATCH.code),
        Fact(passed_courses=MATCH.passed_list),
        Fact(passed_grades=MATCH.grades),
        TEST(lambda code, passed_list: code not in passed_list)  # شرط عدم ترشيح المواد التي تم اجتيازها
    )
    def determine_base_confidence(self, course, code, passed_list, grades):
        base = 0.7 if course.get("category") == "mandatory" or course["type"].endswith("Mandatory Requirements") else 0.5
        prereqs = course.get("prerequisites", [])
        if prereqs:
            if all(pr in grades for pr in prereqs):
                avg = sum(grades[pr] for pr in prereqs) / len(prereqs)
                if avg >= 85:
                    base += 0.15
                elif avg >= 75:
                    base += 0.10
                elif avg >= 65:
                    base += 0.05
        else:
            base += 0.15

        self.declare(RecommendationReady(code=code, base_confidence=base, is_failed=False))

    @Rule(RecommendationReady(code=MATCH.code, base_confidence=MATCH.base, is_failed=MATCH.is_failed),
          Course(course=MATCH.course),
          DifficultyLevel(code=MATCH.code, level=MATCH.level),
          TEST(lambda course, code: course["code"] == code))
    def finalize_recommendation(self, code, base, is_failed, course, level):
        diff_ratio = course.get("difficulty_ratio", 0.3)
        adjusted = max(0.3, base - (diff_ratio * 0.2))
        self.declare(RecommendedCourse(
            code=code,
            name=course["name"],
            hours=course.get("hours", 3),
            category="mandatory" if course.get("category") == "mandatory" or course["type"].endswith("Mandatory Requirements") else "elective",
            is_failed=is_failed,
            base_confidence=base,
            adjusted_confidence=adjusted,
            difficulty=level,
            difficulty_ratio=diff_ratio
        ))
