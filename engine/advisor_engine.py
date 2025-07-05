
from .rules import RecommendationRules
from .facts import StudentFacts
class AdvisorEngine(RecommendationRules):
    def __init__(self, student_data, uncertainty=1.0):
        super().__init__()
        self.student_data = student_data
        self.uncertainty = uncertainty
        self.recommendations = []

    def recommend(self):
        self.reset()
        self.student_data['uncertainty'] = self.uncertainty
        self.declare(StudentFacts(**self.student_data))
        self.run()
        return self.recommendations
