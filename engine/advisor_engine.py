
from .rules import RecommendationRules
from .facts import StudentFacts

class AdvisorEngine(RecommendationRules):
    def __init__(self, student_data):
        super().__init__()
        self.student_data = student_data
        self.recommendations = []

    def recommend(self):
        self.reset()
        self.declare(StudentFacts(**self.student_data))
        self.run()
        return self.recommendations
