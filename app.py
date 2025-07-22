from flask import Flask, request, render_template_string, redirect, url_for
import json, os
from engine.facts import StudentFacts
from engine.advisor_engine import AdvisorEngine

app = Flask(__name__)

with open('data/students.json', 'r', encoding='utf-8') as f:
    STUDENTS = {s['id']: s for s in json.load(f)}

with open('data/collage_info.json', 'r', encoding='utf-8') as f:
    COLLEGE_INFO = json.load(f)

with open('data/courses.json', 'r', encoding='utf-8') as f:
    ALL_COURSES = json.load(f)

RECS_FILE = 'data/all_students_recommendations.json'

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Academic Advisor</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
  <div class="card shadow-lg">
    <div class="card-header bg-primary text-white">
      <h3 class="mb-0">Smart Academic Advising System</h3>
    </div>
    <div class="card-body">
      <form method="post" action="/recommend">
        <div class="mb-3">
          <label for="student_id" class="form-label">Enter Your University ID</label>
          <input type="text" class="form-control" id="student_id" name="student_id" required>
        </div>
        <div class="mb-3">
          <label for="requested_hours" class="form-label">Select Desired Credit Hours</label>
          <select class="form-select" id="requested_hours" name="requested_hours" required>
            {% for h in range(18, 22) %}
              <option value="{{ h }}" {% if h == 18 %}selected{% endif %}>{{ h }} Credit Hours</option>
            {% endfor %}
          </select>
          <small class="form-text text-muted">Note: Max hours may be limited based on your GPA (min GPA {{ min_gpa }} for 19+)</small>
        </div>
        <button type="submit" class="btn btn-primary">Get Recommendations</button>
      </form>
    </div>
  </div>
</div>
</body>
</html>
"""

RECS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recommendations for {{ student_name }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .load-analysis {
      transition: all 0.3s ease;
      max-height: 0;
      overflow: hidden;
    }
    .load-analysis.show {
      max-height: 500px;
    }
    .difficulty-easy { color: #28a745; }
    .difficulty-medium { color: #ffc107; }
    .difficulty-hard { color: #dc3545; }
  </style>
</head>
<body class="bg-light">
<div class="container py-5">
  <div class="card shadow-lg">
    <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
      <h3 class="mb-0">Recommendations for {{ student_name }}</h3>
      <button class="btn btn-light btn-sm" onclick="toggleAnalysis()">Show Study Load Analysis</button>
    </div>
    <div class="card-body">
      {% if recommendations %}
        {% if actual_hours < requested_hours %}
          <div class="alert alert-info">
            You requested {{ requested_hours }} credit hours, but only {{ actual_hours }} were recommended.
            This may be due to the unavailability of additional suitable courses.
          </div>
        {% endif %}
        
        <div class="load-analysis" id="loadAnalysis">
          <h5 class="mt-3">Study Load Analysis</h5>
          <div class="row">
            <div class="col-md-4">
              <div class="card">
                <div class="card-header difficulty-easy">
                  Easy Courses
                </div>
                <div class="card-body">
                  <p class="mb-1">Count: {{ load_analysis.easy.count }}</p>
                  <p>Hours: {{ load_analysis.easy.hours }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card">
                <div class="card-header difficulty-medium">
                  Medium Courses
                </div>
                <div class="card-body">
                  <p class="mb-1">Count: {{ load_analysis.medium.count }}</p>
                  <p>Hours: {{ load_analysis.medium.hours }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card">
                <div class="card-header difficulty-hard">
                  Hard Courses
                </div>
                <div class="card-body">
                  <p class="mb-1">Count: {{ load_analysis.hard.count }}</p>
                  <p>Hours: {{ load_analysis.hard.hours }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="alert alert-secondary mt-3">
            <strong>Load Balance:</strong> 
            {% if load_analysis.hard.hours > load_analysis.easy.hours + load_analysis.medium.hours %}
              <span class="text-danger">Challenging - Consider balancing with easier courses</span>
            {% elif load_analysis.hard.hours > (load_analysis.easy.hours + load_analysis.medium.hours)/2 %}
              <span class="text-warning">Moderate - Manageable but could be balanced better</span>
            {% else %}
              <span class="text-success">Well Balanced - Good mix of difficulty levels</span>
            {% endif %}
          </div>
        </div>
        
        <h5 class="mt-4">Recommended Courses (Total: {{ actual_hours }} hours)</h5>
        <ul class="list-group mt-3">
          {% for rec in recommendations %}
            <li class="list-group-item">{{ rec }}</li>
          {% endfor %}
        </ul>
      {% else %}
        <div class="alert alert-warning">No recommendations found based on your current status.</div>
      {% endif %}
      <a href="/" class="btn btn-link mt-3">Back</a>
    </div>
  </div>
</div>
<script>
  function toggleAnalysis() {
    const analysisDiv = document.getElementById('loadAnalysis');
    analysisDiv.classList.toggle('show');
    const btn = document.querySelector('.card-header button');
    if (analysisDiv.classList.contains('show')) {
      btn.textContent = 'Hide Study Load Analysis';
    } else {
      btn.textContent = 'Show Study Load Analysis';
    }
  }
</script>
</body>
</html>
"""
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HOME_HTML, min_gpa=COLLEGE_INFO['min_gpa_for_overload'])

@app.route('/recommend', methods=['POST'])
def recommend():
    student_id = request.form.get('student_id', '').strip()
    requested_hours = int(request.form.get('requested_hours', 18))

    student = STUDENTS.get(student_id)
    if not student:
        return redirect(url_for('home'))

    gpa = student['gpa']
    if gpa >= COLLEGE_INFO['min_gpa_for_overload']:
        max_allowed = min(requested_hours, COLLEGE_INFO['max_credit_hours_with_permission'])
    else:
        max_allowed = min(requested_hours, COLLEGE_INFO['max_credit_hours_per_semester'])

    # تحديث max_hours في بيانات الطالب
    student['max_hours'] = max_allowed

    # إضافة جميع المقررات إلى بيانات الطالب
    student['all_courses'] = ALL_COURSES

    advisor = AdvisorEngine(student)
    advisor.run()

    actual_hours = advisor.total_hours if hasattr(advisor, 'total_hours') else 0

    load_analysis = getattr(advisor, 'study_load_analysis', {
        'easy': {'count': 0, 'hours': 0},
        'medium': {'count': 0, 'hours': 0},
        'hard': {'count': 0, 'hours': 0}
    })

    recommendations_data = {}
    if os.path.exists(RECS_FILE):
        with open(RECS_FILE, 'r', encoding='utf-8') as f:
            try:
                recommendations_data = json.load(f)
            except json.JSONDecodeError:
                recommendations_data = {}

    recommendations_data[student_id] = {
        'courses': advisor.recommendations,
        'load_analysis': load_analysis,
        'total_hours': actual_hours
    }

    with open(RECS_FILE, 'w', encoding='utf-8') as f:
        json.dump(recommendations_data, f, ensure_ascii=False, indent=2)

    return render_template_string(RECS_HTML,
                                student_name=student['name'],
                                recommendations=advisor.recommendations,
                                requested_hours=requested_hours,
                                actual_hours=actual_hours,
                                load_analysis=load_analysis)

if __name__ == '__main__':
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.5, open_browser).start()

    app.run(debug=True)