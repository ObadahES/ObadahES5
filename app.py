from flask import Flask, request, render_template_string, redirect, url_for
import json, os
from engine.facts import StudentFacts
from engine.advisor_engine import AdvisorEngine

app = Flask(__name__)

with open('data/students.json', 'r', encoding='utf-8') as f:
    STUDENTS = {s['id']: s for s in json.load(f)}

with open('data/collage_info.json', 'r', encoding='utf-8') as f:
    COLLEGE_INFO = json.load(f)

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
</head>
<body class="bg-light">
<div class="container py-5">
  <div class="card shadow-lg">
    <div class="card-header bg-success text-white">
      <h3 class="mb-0">Recommendations for {{ student_name }}</h3>
    </div>
    <div class="card-body">
      {% if recommendations %}
        {% if actual_hours < requested_hours %}
          <div class="alert alert-info">
            You requested {{ requested_hours }} credit hours, but only {{ actual_hours }} were recommended.
            This may be due to the unavailability of additional suitable courses.
          </div>
        {% endif %}
        <ul class="list-group">
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

    student['max_hours'] = max_allowed

    updated_students_list = list(STUDENTS.values())
    with open('data/students.json', 'w', encoding='utf-8') as f:
        json.dump(updated_students_list, f, ensure_ascii=False, indent=2)

    advisor = AdvisorEngine(student)
    advisor.reset()
    advisor.declare(StudentFacts(**student))
    advisor.run()

    actual_hours = advisor.total_hours if hasattr(advisor, 'total_hours') else sum(
        int(rec.split('(')[-1].split('h')[0]) for rec in advisor.recommendations if '(' in rec and 'h' in rec)

    recommendations_data = {}
    if os.path.exists(RECS_FILE):
        with open(RECS_FILE, 'r', encoding='utf-8') as f:
            try:
                recommendations_data = json.load(f)
            except json.JSONDecodeError:
                recommendations_data = {}

    recommendations_data[student_id] = advisor.recommendations

    with open(RECS_FILE, 'w', encoding='utf-8') as f:
        json.dump(recommendations_data, f, ensure_ascii=False, indent=2)

    return render_template_string(RECS_HTML,
                                  student_name=student['name'],
                                  recommendations=advisor.recommendations,
                                  requested_hours=requested_hours,
                                  actual_hours=actual_hours)

if __name__ == '__main__':
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.5, open_browser).start()

    app.run(debug=True)