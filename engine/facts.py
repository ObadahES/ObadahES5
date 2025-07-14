from experta import Fact, Field

class StudentFacts(Fact):
    id = Field(str, mandatory=True)
    name = Field(str, mandatory=True)
    current_level = Field(int, mandatory=True)
    gpa = Field(float, mandatory=True)
    passed_courses = Field(list, default=[])
    failed_courses = Field(list, default=[])
    max_hours = Field(int, mandatory=True)
    registered_hours = Field(int, default=0)
    interests = Field(list, default=[])
    academic_status = Field(str, default=None)
    goal = Field(str, default=None) 


class RecommendedCourse(Fact):
    code = Field(str)
    name = Field(str)
    hours = Field(int)
    category = Field(str)
    is_failed = Field(bool, default=False)
    base_confidence = Field(float)
    adjusted_confidence = Field(float)
    difficulty = Field(str)
    difficulty_ratio = Field(float)


class Course(Fact): pass
class MandatoryCourse(Fact): pass
class ElectiveCourse(Fact): pass
class FailedCourse(Fact): pass
class NotFailed(Fact): pass
class PrerequisitesPassed(Fact): pass
class HighGPA(Fact): pass
class HighGradeInPrereqs(Fact): pass