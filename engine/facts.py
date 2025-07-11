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
    uncertainty = Field(float, default=1.0)
