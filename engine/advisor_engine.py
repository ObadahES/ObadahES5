from .rules import RecommendationRules, RecommendedCourse

class AdvisorEngine(RecommendationRules):
    def __init__(self, student_data, uncertainty=1.0):
        super().__init__()
        self.student_data = student_data
        self.uncertainty = uncertainty
        self.recommendations = []
        self.total_hours = 0

    def run(self):
        super().run()
        all_recs = [fact for fact in self.facts.values() if isinstance(fact, RecommendedCourse)]
        sorted_recs = sorted(all_recs, key=lambda x: -x['adjusted_confidence'])

        for rec in sorted_recs:
            if self.total_hours + rec['hours'] <= self.max_hours:
                self.recommendations.append(
                    f"{rec['code']} - {rec['name']} ({rec['hours']}h) - Confidence: {rec['adjusted_confidence']:.2f}"
                )
                self.total_hours += rec['hours']
                self.study_load_analysis[rec['difficulty']]['count'] += 1
                self.study_load_analysis[rec['difficulty']]['hours'] += rec['hours']
