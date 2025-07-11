from .rules import RecommendationRules

class AdvisorEngine(RecommendationRules):
    def __init__(self, student_data, uncertainty=1.0):
        super().__init__()
        self.student_data = student_data
        self.recommendations = []
        self.total_hours = 0
        self.uncertainty = uncertainty

    def run(self):
        super().run()
        self.pending_recommendations.sort(key=lambda x: -x[0])
        for confidence, recommendation, hours in self.pending_recommendations:
            if self.total_hours + hours <= self.max_hours:
                self.recommendations.append(recommendation)
                self.total_hours += hours
            else:
                break