from experta import KnowledgeEngine, Rule, Fact, MATCH, TEST, DefFacts
from engine.facts import StudentFacts
import os
import json

class Course(Fact): pass
class MandatoryCourse(Fact): pass
class ElectiveCourse(Fact): pass
class FailedCourse(Fact): pass
class NotFailed(Fact): pass
class PrerequisitesPassed(Fact): pass
class HighGPA(Fact): pass
class HighGradeInPrereqs(Fact): pass
class DifficultyLevel(Fact): pass

class RecommendationRules(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.total_hours = 0
        self.pending_recommendations = []
        self.failed_courses_added = set()
        self.study_load_analysis = {
            'easy': {'count': 0, 'hours': 0},
            'medium': {'count': 0, 'hours': 0},
            'hard': {'count': 0, 'hours': 0}
        }

        current_dir = os.path.dirname(os.path.abspath(__file__))
        courses_path = os.path.join(current_dir, '..', 'Data', 'courses.json')

        with open(courses_path, 'r', encoding='utf-8') as f:
            self.all_courses = json.load(f)

    def calculate_difficulty_factor(self, course):
        difficulty = 0.3
        prereqs_count = len(course.get("prerequisites", []))
        if prereqs_count > 2:
            difficulty += 0.1
        elif prereqs_count > 0:
            difficulty += 0.05
        if course.get("hours", 3) >= 4:
            difficulty += 0.1
        if course.get("year", 1) >= 3:
            difficulty += 0.1
        return max(0.2, min(0.8, difficulty))

    def add_recommendation(self, course, confidence, is_failed=False):
        code = course["code"]
        if code in {r.split(" - ")[0] for r in self.recommendations} \
        or any(r['code'] == code for r in self.pending_recommendations):
            return

        name = course["name"]
        hours = course.get("hours", 3)
        category = "mandatory" if course.get("category") == "mandatory" or course["type"].endswith("Mandatory Requirements") else "elective"

        # استبدل استخدام calculate_difficulty_factor بقراءة difficulty_ratio من course
        difficulty_ratio = course.get("difficulty_ratio", 0.3)

        # تصنيف مستوى الصعوبة بناءً على difficulty_ratio من ملف courses.json
        if difficulty_ratio < 0.3:
            difficulty_level = 'easy'
        elif difficulty_ratio < 0.5:
            difficulty_level = 'medium'
        else:
            difficulty_level = 'hard'

        # تعديل نسبة الثقة حسب الصعوبة (يمكنك تعديل هذا إذا أردت)
        adjusted_confidence = confidence - (difficulty_ratio * 0.2)
        adjusted_confidence = max(0.3, adjusted_confidence)

        rec = {
            "confidence": adjusted_confidence,
            "text": f"{code} - {name} ({hours}h) - Confidence: {adjusted_confidence:.2f}",
            "hours": hours,
            "category": category,
            "is_failed": is_failed,
            "code": code,
            "difficulty": difficulty_level,
            "base_confidence": confidence,
            "difficulty_ratio": difficulty_ratio
        }

        if is_failed:
            if self.total_hours + hours <= self.max_hours:
                self.recommendations.append(rec["text"])
                self.total_hours += hours
                self.failed_courses_added.add(code)
                self.study_load_analysis[difficulty_level]['count'] += 1
                self.study_load_analysis[difficulty_level]['hours'] += hours
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
                self.declare(FailedCourse(code=code))
                course = next((c for c in self.all_courses if c["code"] == code), None)
                if course:
                    self.add_recommendation(course, 0.8, is_failed=True)

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
        if course["code"] not in self.failed_courses_added and self.total_hours + course.get("hours", 3) <= self.max_hours:
            self.add_recommendation(course, 0.8, is_failed=True)

    @Rule((MandatoryCourse(code=MATCH.code) | ElectiveCourse(code=MATCH.code)),
          Course(course=MATCH.course),
          NotFailed(code=MATCH.code),
          PrerequisitesPassed(code=MATCH.code),
          Fact(passed_grades=MATCH.grades),
          salience=700)
    def recommend_course(self, course, code, grades):
        # 1. الثقة الأساسية
        base_confidence = 0.7 if course.get("category") == "mandatory" or course["type"].endswith("Mandatory Requirements") else 0.5

        prereqs = course.get("prerequisites", [])

        # 2. رفع الثقة بناءً على المتطلبات
        if prereqs:
            # إذا اجتاز جميع المتطلبات
            if all(pr in grades for pr in prereqs):
                avg = sum(grades[pr] for pr in prereqs) / len(prereqs)
                if avg >= 85:
                    base_confidence += 0.15
                elif avg >= 75:
                    base_confidence += 0.10
                elif avg >= 65:
                    base_confidence += 0.05
        else:
            # المواد التي لا تحتوي على متطلبات تحصل على +0.15
            base_confidence += 0.15

        # 3. رفع الثقة إذا المعدل عالٍ
        if self.facts.get(HighGPA()):
            base_confidence += 0.1

        # 4. أضف التوصية
        self.add_recommendation(course, confidence=base_confidence)

    @Rule(Course(course=MATCH.course),
          Fact(failed_courses=MATCH.failed_list),
          TEST(lambda course, failed_list: course["code"] not in failed_list),
          salience=100)
    def course_not_failed(self, course, failed_list):
        self.declare(NotFailed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_courses=MATCH.passed_list),
          TEST(lambda course, passed_list: all(pr in passed_list for pr in course.get("prerequisites", [])) if course.get("prerequisites") else True),
          salience=100)
    def prerequisites_passed(self, course, passed_list):
        self.declare(PrerequisitesPassed(code=course["code"]))

    @Rule(Course(course=MATCH.course),
          Fact(passed_grades=MATCH.grades),
          TEST(lambda course, grades: any(grades.get(pr, 0) >= 85 for pr in course.get("prerequisites", []))),
          salience=100)
    def high_grade_in_prerequisites(self, course, grades):
        self.declare(HighGradeInPrereqs(code=course["code"]))

    @Rule(StudentFacts(gpa=MATCH.gpa),
          TEST(lambda gpa: gpa >= 3.5),
          salience=100)
    def student_high_gpa(self):
        self.declare(HighGPA())
        
    def run(self):
        super().run()
        self.pending_recommendations.sort(key=lambda x: (
            -x['confidence'],
            0 if x['category'] == 'mandatory' else 1,
            x['code']
        ))

        for rec in self.pending_recommendations:
            if self.total_hours + rec['hours'] <= self.max_hours:
                self.recommendations.append(rec['text'])
                self.total_hours += rec['hours']
                self.study_load_analysis[rec['difficulty']]['count'] += 1
                self.study_load_analysis[rec['difficulty']]['hours'] += rec['hours']
