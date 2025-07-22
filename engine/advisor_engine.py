from .rules import RecommendationRules, RecommendedCourse
from .facts import *

class AdvisorEngine(RecommendationRules):
    def __init__(self, student_data, uncertainty=1.0):
        super().__init__()
        self.student_data = student_data
        self.uncertainty = uncertainty
        self.recommendations = []
        self.total_hours = 0
        self.study_load_analysis = {
            'easy': {'count': 0, 'hours': 0},
            'medium': {'count': 0, 'hours': 0},
            'hard': {'count': 0, 'hours': 0}
        }
        self.max_hours = student_data.get('max_hours', 18)

        if "all_courses" not in self.student_data:
            raise ValueError("Missing 'all_courses' in student_data")

        self.all_courses = self.student_data["all_courses"]

    def run(self):
        self.reset()

        self.declare(StudentFacts(
            id=self.student_data["id"],
            name=self.student_data["name"],
            current_level=self.student_data["current_level"],
            gpa=self.student_data["gpa"],
            passed_courses=[c["code"] for c in self.student_data["passed_courses"]],
            failed_courses=[c["code"] for c in self.student_data["failed_courses"]],
            max_hours=self.student_data["max_hours"],
            registered_hours=self.student_data.get("registered_hours", 0),
            interests=self.student_data.get("interests", []),
            academic_status=self.student_data.get("academic_status", None),
            goal=self.student_data.get("goal", None)
        ))

        for course in self.all_courses:
            self.declare(Course(
                code=course["code"],
                name=course["name"],
                hours=course["hours"],
                year=course.get("year"),
                semester=course.get("semester"),
                type=course.get("type"),
                prerequisites=course.get("prerequisites", []),
                category=course.get("category"),
                difficulty_ratio=course.get("difficulty_ratio", 0.3)
            ))

        if self.student_data["gpa"] >= 3.5:
            self.declare(HighGPA())

        self.declare(NotFailed())

        passed_courses_dict = {c["code"]: c["grade"] for c in self.student_data["passed_courses"]}

        for course_code, grade in passed_courses_dict.items():
            if grade >= 85:
                self.declare(HighGradeInPrereqs(course_code=course_code)) 

        super().run()

        all_recs = [fact for fact in self.facts.values() if isinstance(fact, RecommendedCourse)]
        sorted_recs = sorted(all_recs, key=lambda x: -x['adjusted_confidence'])

        added_codes = set()  # لتجنب تكرار المواد

        for rec in sorted_recs:
            if rec['code'] in added_codes:
                continue  # تجاهل التكرار

            if self.total_hours + rec['hours'] <= self.max_hours:
                self.recommendations.append(
                    f"{rec['code']} - {rec['name']} ({rec['hours']}h) - Confidence: {rec['adjusted_confidence']:.2f}"
                )
                self.total_hours += rec['hours']
                added_codes.add(rec['code'])

                if rec['difficulty'] in self.study_load_analysis:
                    self.study_load_analysis[rec['difficulty']]['count'] += 1
                    self.study_load_analysis[rec['difficulty']]['hours'] += rec['hours']
