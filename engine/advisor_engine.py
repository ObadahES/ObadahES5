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
        # تم تعديل هذه الجزئية لتتناسب مع بنية البيانات الجديدة
        self.pending_recommendations.sort(key=lambda x: -x['confidence'])
        for rec in self.pending_recommendations:
            if self.total_hours + rec['hours'] <= self.max_hours:
                self.recommendations.append(rec['text'])
                self.total_hours += rec['hours']
            else:
                break