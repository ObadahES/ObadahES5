# from experta import KnowledgeEngine, Rule, Fact, MATCH, TEST
# from engine.Student import StudentFacts
# import os
# import json
# #-----------------------------------------------------
# class CourseRecommended(Fact):
#     pass

# #-----------------------------------------------------
# class RecommendationRules(KnowledgeEngine):
#     def __init__(self):
#         super().__init__()
#         self.recommendations = []
#         self.total_hours = 0

#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         courses_path = os.path.join(current_dir, '..', 'Data', 'courses.json')

#         with open(courses_path, 'r', encoding='utf-8') as f:
#             self.all_courses = json.load(f)

# #-----------------------------------------------------
#     def add_recommendation(self, course, confidence):
#         code = course["code"]
#         name = course["name"]
#         hours = course.get("hours", 3)
#         if self.total_hours + hours <= self.max_hours:
#             self.recommendations.append(f"{code} - {name} ({hours}h) - Confidence: {confidence:.2f}")
#             self.total_hours += hours
# #-----------------------------------------------------

#     def calc_confidence(self, course, passed, failed, gpa):
#         conf = 0.5
#         if course["code"] not in failed:
#             conf += 0.3
#         prereqs = course.get("prerequisites", [])
#         if all(pr in passed for pr in prereqs):
#             conf += 0.1
#         if gpa >= 3.5:
#             conf += 0.1
#         return min(conf, 1.0)
# #-----------------------------------------------------

#     @Rule(StudentFacts(current_level=MATCH.level, passed_courses=MATCH.passed,
#                        failed_courses=MATCH.failed, max_hours=MATCH.max_hours,
#                        gpa=MATCH.gpa))
#     def init_student(self, level, passed, failed, max_hours, gpa):
#         self.passed = passed
#         self.failed = failed
#         self.gpa = gpa
#         self.max_hours = max_hours

#         for code in failed:
#             course = next((c for c in self.all_courses if c["code"] == code), None)
#             if course:
#                 self.add_recommendation(course, 0.6)

#         for course in self.all_courses:
#             self.declare(Fact(course=course))


#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQU101"))
#     def rule_RQU101(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQU102"))
#     def rule_RQU102(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 105- IT"))
#     def rule_RQF105IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF104-IT"))
#     def rule_RQF104IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 106- IT"))
#     def rule_RQF106IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "Lvl 1"))
#     def rule_Lvl1(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "Lvl 2"))
#     def rule_Lvl2(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "Lvl 3"))
#     def rule_Lvl3(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "Lvl 4"))
#     def rule_Lvl4(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQU 103"))
#     def rule_RQU103(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 210- IT"))
#     def rule_RQF210IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 209- IT"))
#     def rule_RQF209IT(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 208- IT"))
#     def rule_RQF208IT(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 212- IT"))
#     def rule_RQF212IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQU 207"))
#     def rule_RQU207(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQU 211"))
#     def rule_RQU211(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 315- IT"))
#     def rule_RQF315IT(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQF 313- IT"))
#     def rule_RQF313IT(self, course):
#         if all(pr in self.passed for pr in course["prerequisites"]):
#             conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#             if conf >= 0.3:
#                 self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQITC316"))
#     def rule_RQITC316(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

#     @Rule(Fact(course=MATCH.course), TEST(lambda course: course["code"] == "RQUE1"))
#     def rule_RQUE1(self, course):
#         conf = self.calc_confidence(course, self.passed, self.failed, self.gpa)
#         if conf >= 0.3:
#             self.add_recommendation(course, conf)

# #-----------------------------------------------------