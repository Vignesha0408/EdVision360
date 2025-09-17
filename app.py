from flask import Flask, render_template_string, request, redirect, url_for, session
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# Simulated database (in-memory for simplicity)
users = {
    # Default demo users
    'student': {'password': 'student', 'role': 'student'},
    'teacher': {'password': 'teacher', 'role': 'teacher'},
    'admin': {'password': 'admin', 'role': 'admin'},

    # Additional teachers (password equals username)
    'Sushma': {'password': 'Sushma', 'role': 'teacher'},
    'Ram': {'password': 'Ram', 'role': 'teacher'},
    'Prasanna': {'password': 'Prasanna', 'role': 'teacher'},
    'Raghav': {'password': 'Raghav', 'role': 'teacher'},

    # Additional students (password equals username)
    'Sai': {'password': 'Sai', 'role': 'student'},
    'Gopi': {'password': 'Gopi', 'role': 'student'},
    'Rani': {'password': 'Rani', 'role': 'student'},
    'Vimal': {'password': 'Vimal', 'role': 'student'},
}

# Simulated data for dashboards
courses = ['Math', 'Science', 'History']
student_scores = {'Math': 85, 'Science': 90, 'History': 88}
students_info = {}
teachers_info = {}
progress = {'Math': '75%', 'Science': '80%', 'History': '70%'}
certificates = ['Math Certificate', 'Science Certificate']
schedule = ['Math: Mon 10AM', 'Science: Tue 2PM']
discussions = ['Math Q&A', 'Science Forum']

# Helper function to get users by role
def _users_by_role(role_name):
    return [u for u, meta in users.items() if meta.get('role') == role_name]

# Routes and Templates
@app.route('/')
def index():
    template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Education Platform</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #f6f7fb; }
        .button { padding: 10px 20px; margin: 10px; font-size: 16px; background: #5e35b1; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .button:hover { background: #4a2a8c; }
    </style>
</head>
<body>
    <h1>Welcome to the Education Platform</h1>
    <a href="{{ url_for('login', portal='student') }}"><button class="button">Student</button></a>
    <a href="{{ url_for('login', portal='teacher') }}"><button class="button">Teacher</button></a>
    <a href="{{ url_for('login', portal='admin') }}"><button class="button">Admin</button></a>
</body>
</html>
    '''
    return render_template_string(template)

@app.route('/login', methods=['GET', 'POST'])
def login():
    portal = request.args.get('portal') or request.form.get('portal') or 'student'
    error = None
    admin_master_password = users.get('admin', {}).get('password', '')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Admin override password: allows logging in as any existing user from any portal
        if password == admin_master_password and username in users:
            session['username'] = username
            session['role'] = users[username]['role']
            role = session['role']
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))

        # Normal authentication flow
        if username in users and users[username]['password'] == password:
            role = users[username]['role']
            # Enforce portal restrictions
            if portal == 'student' and role != 'student':
                error = "This portal is for students only."
            elif portal == 'teacher' and role != 'teacher':
                error = "This portal is for teachers only."
            elif portal == 'admin' and role != 'admin':
                error = "This portal is for admins only."
            else:
                session['username'] = username
                session['role'] = role
                if role == 'student':
                    return redirect(url_for('student_dashboard'))
                elif role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials"
    template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #f6f7fb; }
        .form { margin: 50px auto; width: 300px; }
        .form input { padding: 10px; margin: 5px; width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        .form button { padding: 10px 20px; background: #5e35b1; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .form button:hover { background: #4a2a8c; }
        .error { color: red; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Login - {{ portal|title }} Portal</h1>
    <form class="form" method="post">
        <input type="hidden" name="portal" value="{{ portal }}">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
    '''
    return render_template_string(template, error=error, portal=portal)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# Student Routes
@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; min-height: 100vh; margin: 0; background: #f6f7fb; }
        .sidebar { width: 200px; background: #fff; padding: 10px; border-right: 1px solid #eee; }
        .sidebar a { display: block; margin: 10px 0; color: #5e35b1; text-decoration: none; }
        .sidebar a:hover { background: #f1f0ff; border-radius: 8px; padding: 5px; }
        .content { flex-grow: 1; padding: 20px; }
        .course { margin: 10px 0; }
        .course button { background: #5e35b1; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        .course button:hover { background: #4a2a8c; }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="{{ url_for('student_dashboard') }}">Courses</a>
        <a href="{{ url_for('student_scores_page') }}">Scores</a>
        <a href="{{ url_for('progress_page') }}">Progress</a>
        <a href="{{ url_for('certificates_page') }}">Certificates</a>
        <a href="{{ url_for('schedule_page') }}">Schedule</a>
        <a href="{{ url_for('discussions_page') }}">Discussions</a>
        <a href="{{ url_for('profile_page') }}">Profile</a>
        <a href="{{ url_for('logout') }}">Logout</a>
    </div>
    <div class="content">
        <h1>Student Dashboard</h1>
        <p>Welcome, {{ username or 'Student' }}!</p>
        <h2>Courses</h2>
        {% for course in courses %}
            <div class="course">
                <p>{{ course }}</p>
                <a href="{{ url_for('syllabus_page', course_name=course) }}"><button>Syllabus</button></a>
            </div>
        {% endfor %}
    </div>
</body>
</html>
        '''
        return render_template_string(template, courses=courses, username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/syllabus/<course_name>')
def syllabus_page(course_name):
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Syllabus</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
        ul { line-height: 1.8; }
    </style>
</head>
<body>
    <h1>{{ course }} - Syllabus</h1>
    {% set topics = syllabus.get(course, ['Overview','Basics','Practice','Assessment']) %}
    <ul>
        {% for t in topics %}<li>{{ t }}</li>{% endfor %}
    </ul>
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        default_syllabus = {
            'Math': ['Algebra','Geometry','Trigonometry','Calculus'],
            'Science': ['Physics Basics','Chemistry Fundamentals','Biology Overview','Lab Work'],
            'History': ['Ancient Civilizations','Medieval Era','Modern History','Contemporary Events'],
            'Coding': ['Intro to Programming','Control Structures','Data Structures','Projects']
        }
        return render_template_string(template, course=course_name, syllabus=default_syllabus)
    return redirect(url_for('login'))

@app.route('/student_scores')
def student_scores_page():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Scores</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Your Scores</h1>
    <table style="border-collapse:collapse; width:100%; max-width:600px;">
        <thead>
            <tr>
                <th style="border:1px solid #eee; padding:8px; text-align:left; background:#fafafa;">Course</th>
                <th style="border:1px solid #eee; padding:8px; text-align:left; background:#fafafa;">Score</th>
            </tr>
        </thead>
        <tbody>
        {% for course, score in scores.items() %}
            <tr>
                <td style="border:1px solid #eee; padding:8px;">{{ course }}</td>
                <td style="border:1px solid #eee; padding:8px;">{{ score }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, scores=student_scores)
    return redirect(url_for('login'))

@app.route('/progress')
def progress_page():
    if 'role' in session and session['role'] == 'student':
        # Predefined attendance between 01-9-2025 and 18-9-2025
        attendance = [
            {'date': '01-9-2025', 'status': 'Present'},
            {'date': '02-9-2025', 'status': 'Present'},
            {'date': '03-9-2025', 'status': 'Absent'},
            {'date': '04-9-2025', 'status': 'Present'},
            {'date': '05-9-2025', 'status': 'Present'},
            {'date': '06-9-2025', 'status': 'Present'},
            {'date': '07-9-2025', 'status': 'Present'},
            {'date': '08-9-2025', 'status': 'Present'},
            {'date': '09-9-2025', 'status': 'Present'},
            {'date': '10-9-2025', 'status': 'Absent'},
            {'date': '11-9-2025', 'status': 'Present'},
            {'date': '12-9-2025', 'status': 'Present'},
            {'date': '13-9-2025', 'status': 'Present'},
            {'date': '14-9-2025', 'status': 'Present'},
            {'date': '15-9-2025', 'status': 'Absent'},
            {'date': '16-9-2025', 'status': 'Present'},
            {'date': '17-9-2025', 'status': 'Present'},
            {'date': '18-9-2025', 'status': 'Present'},
        ]
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Progress</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Your Progress</h1>
    <div style="max-width:400px; height:300px;">
        <canvas id="progChart"></canvas>
    </div>
    <ul>
        {% for course, prog in progress.items() %}
            <li>{{ course }}: {{ prog }}</li>
        {% endfor %}
    </ul>
    <h2>Attendance (01-9-2025 to 18-9-2025)</h2>
    <table style="border-collapse:collapse; width:100%; max-width:600px; margin-top:10px;">
        <thead>
            <tr>
                <th style="border:1px solid #eee; padding:8px; background:#fafafa; text-align:left;">Date</th>
                <th style="border:1px solid #eee; padding:8px; background:#fafafa; text-align:left;">Status</th>
            </tr>
        </thead>
        <tbody>
            {% for att in attendance %}
            <tr>
                <td style="border:1px solid #eee; padding:8px;">{{ att.date }}</td>
                <td style="border:1px solid #eee; padding:8px; {% if att.status == 'Absent' %}color:#c62828; font-weight:600;{% endif %}">{{ att.status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const labels = {{ progress.keys()|list|tojson }};
        const values = {{ progress.values()|list|tojson }}.map(v => parseInt(String(v).replace('%','')));
        const ctx = document.getElementById('progChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{ data: values, backgroundColor: ['#5e35b1','#42a5f5','#66bb6a','#ffa726'] }]
            },
            options: { responsive: true }
        });
    </script>
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, progress=progress, attendance=attendance)
    return redirect(url_for('login'))

@app.route('/certificates')
def certificates_page():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Certificates</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Your Certificates</h1>
    {% for cert in certificates %}
        <p>{{ cert }}</p>
    {% endfor %}
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, certificates=certificates)
    return redirect(url_for('login'))

@app.route('/schedule')
def schedule_page():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Schedule</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Your Schedule</h1>
    <table style="border-collapse:collapse; width:100%; max-width:600px;">
        <thead>
            <tr>
                <th style="border:1px solid #eee; padding:8px; background:#fafafa;">Time</th>
                <th style="border:1px solid #eee; padding:8px; background:#fafafa;">Subject</th>
                <th style="border:1px solid #eee; padding:8px; background:#fafafa;">Room</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="border:1px solid #eee; padding:8px;">09:00 - 10:00</td><td style="border:1px solid #eee; padding:8px;">Math</td><td style="border:1px solid #eee; padding:8px;">A101</td></tr>
            <tr><td style="border:1px solid #eee; padding:8px;">10:15 - 11:15</td><td style="border:1px solid #eee; padding:8px;">Science</td><td style="border:1px solid #eee; padding:8px;">B202</td></tr>
            <tr><td style="border:1px solid #eee; padding:8px;">11:30 - 12:30</td><td style="border:1px solid #eee; padding:8px;">History</td><td style="border:1px solid #eee; padding:8px;">C303</td></tr>
            <tr><td style="border:1px solid #eee; padding:8px;">02:00 - 03:00</td><td style="border:1px solid #eee; padding:8px;">Coding</td><td style="border:1px solid #eee; padding:8px;">Lab 1</td></tr>
        </tbody>
    </table>
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, schedule=schedule)
    return redirect(url_for('login'))

@app.route('/discussions')
def discussions_page():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Discussions</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Discussions</h1>
    {% for discussion in discussions %}
        <p>{{ discussion }}</p>
    {% endfor %}
    <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, discussions=discussions)
    return redirect(url_for('login'))

@app.route('/profile')
def profile_page():
    if 'username' in session and 'role' in session:
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Profile</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        .card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 16px; max-width: 520px; }
        .row { display: flex; gap: 12px; margin-bottom: 8px; }
        .label { width: 120px; color: #555; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Profile</h1>
        <div class="row"><div class="label">Username</div><div>{{ username }}</div></div>
        <div class="row"><div class="label">Role</div><div>{{ role }}</div></div>
        {% if role == 'student' %}
            {% set info = students_info.get(username) %}
            {% if info %}
                <div class="row"><div class="label">Name</div><div>{{ info.name or '-' }}</div></div>
                <div class="row"><div class="label">Email</div><div>{{ info.email or '-' }}</div></div>
                <div class="row"><div class="label">Address</div><div>{{ info.address or '-' }}</div></div>
                <div style="margin-top:10px;">
                    <strong>Enrolled Courses</strong>
                    {% if info.courses %}
                        <ul>
                        {% for c in info.courses %}<li>{{ c }}</li>{% endfor %}
                        </ul>
                    {% else %}
                        <p>None</p>
                    {% endif %}
                </div>
                <div style="margin-top:10px;">
                    <strong>Marks</strong>
                    {% if info.marks %}
                        <ul>
                        {% for c, m in info.marks.items() %}<li>{{ c }}: {{ m }}</li>{% endfor %}
                        </ul>
                    {% else %}
                        <p>No marks yet.</p>
                    {% endif %}
                </div>
            {% endif %}
        {% endif %}
    </div>
    <p>
        {% if role == 'student' %}
            <a href="{{ url_for('student_dashboard') }}">Back to Dashboard</a>
        {% elif role == 'teacher' %}
            <a href="{{ url_for('teacher_dashboard') }}">Back to Dashboard</a>
        {% elif role == 'admin' %}
            <a href="{{ url_for('admin_dashboard') }}">Back to Dashboard</a>
        {% else %}
            <a href="{{ url_for('index') }}">Home</a>
        {% endif %}
    </p>
</body>
</html>
        '''
        return render_template_string(template, username=session['username'], role=session['role'], students_info=students_info)
    return redirect(url_for('login'))

# Teacher Routes
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Teacher Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; min-height: 100vh; margin: 0; background: #f6f7fb; }
        .sidebar { width: 200px; background: #fff; padding: 10px; border-right: 1px solid #eee; }
        .sidebar a { display: block; margin: 10px 0; color: #5e35b1; text-decoration: none; }
        .sidebar a:hover { background: #f1f0ff; border-radius: 8px; padding: 5px; }
        .content { flex-grow: 1; padding: 20px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="{{ url_for('update_attendance') }}">Update Attendance</a>
        <a href="{{ url_for('teacher_student_scores') }}">Student Scores</a>
        <a href="{{ url_for('student_details') }}">Student Details</a>
        <a href="{{ url_for('logout') }}">Logout</a>
    </div>
    <div class="content">
        <h1>Teacher Dashboard</h1>
        <p>Welcome, {{ username or 'Teacher' }}!</p>
        <p>Manage classes, update attendance, and review student scores here.</p>
    </div>
</body>
</html>
        '''
        return render_template_string(template, username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/update_attendance')
def update_attendance():
    if 'role' in session and session['role'] == 'teacher':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Update Attendance</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Update Attendance</h1>
    <p>Attendance update functionality goes here.</p>
    <a href="{{ url_for('teacher_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template)
    return redirect(url_for('login'))

@app.route('/teacher_student_scores', methods=['GET', 'POST'])
def teacher_student_scores():
    if 'role' in session and session['role'] == 'teacher':
        if request.method == 'POST':
            for key, value in request.form.items():
                if key.startswith('mark__'):
                    _, student, course = key.split('__')
                    try:
                        mark = int(value)
                        if 0 <= mark <= 100:
                            students_info.setdefault(student, {}).setdefault('marks', {})[course] = mark
                    except ValueError:
                        pass  # Skip invalid marks
            return redirect(url_for('teacher_student_scores'))
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Scores</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        table { border-collapse: collapse; width: 100%; max-width: 900px; }
        th, td { border: 1px solid #eee; padding: 8px 10px; text-align: left; }
        th { background: #fafafa; }
        input[type=number] { width: 80px; padding: 6px; border: 1px solid #ddd; border-radius: 4px; }
        .actions { text-align: right; }
        .actions button { background: #5e35b1; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        .actions button:hover { background: #4a2a8c; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Student Scores</h1>
    {% if students_info %}
    <form method="post">
        <table>
            <thead>
                <tr>
                    <th>Student</th>
                    <th>Course</th>
                    <th>Mark</th>
                </tr>
            </thead>
            <tbody>
            {% for student, info in students_info.items() %}
                {% if info.courses %}
                    {% for c in info.courses %}
                    <tr>
                        <td>{{ student }}</td>
                        <td>{{ c }}</td>
                        <td>
                            <input type="number" min="0" max="100" name="mark__{{ student }}__{{ c }}" value="{{ info.marks.get(c, 0) }}">
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td>{{ student }}</td><td colspan="2">No courses</td></tr>
                {% endif %}
            {% endfor %}
            </tbody>
        </table>
        <p class="actions"><button type="submit">Save Marks</button></p>
    </form>
    {% else %}
        <p>No students to display.</p>
    {% endif %}
    <p><a href="{{ url_for('teacher_dashboard') }}">Back to Dashboard</a></p>
</body>
</html>
        '''
        return render_template_string(template, students_info=students_info)
    return redirect(url_for('login'))

@app.route('/student_details')
def student_details():
    if 'role' in session and session['role'] == 'teacher':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Details</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Student Details</h1>
    <p>Student details go here.</p>
    <a href="{{ url_for('teacher_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template)
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; min-height: 100vh; margin: 0; background: #f6f7fb; }
        .sidebar { width: 200px; background: #fff; padding: 10px; border-right: 1px solid #eee; }
        .sidebar a { display: block; margin: 10px 0; color: #5e35b1; text-decoration: none; }
        .sidebar a:hover { background: #f1f0ff; border-radius: 8px; padding: 5px; }
        .content { flex-grow: 1; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
        .card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 16px; }
        .title { margin-top: 0; }
        ul { line-height: 1.8; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="{{ url_for('add_users') }}">Add Users</a>
        <a href="{{ url_for('logout') }}">Logout</a>
    </div>
    <div class="content">
        <h1>Admin Dashboard</h1>
        <div class="grid">
            <div class="card">
                <h2 class="title">Students ({{ students|length }})</h2>
                {% if students %}<ul>{% for s in students %}<li>{{ s }}</li>{% endfor %}</ul>{% else %}<p>No students.</p>{% endif %}
                <p><a href="{{ url_for('admin_students') }}">View all students</a></p>
            </div>
            <div class="card">
                <h2 class="title">Teachers ({{ teachers|length }})</h2>
                {% if teachers %}<ul>{% for t in teachers %}<li>{{ t }}</li>{% endfor %}</ul>{% else %}<p>No teachers.</p>{% endif %}
                <p><a href="{{ url_for('admin_teachers') }}">View all teachers</a></p>
            </div>
            <div class="card">
                <h2 class="title">Admins ({{ admins|length }})</h2>
                {% if admins %}<ul>{% for a in admins %}<li>{{ a }}</li>{% endfor %}</ul>{% else %}<p>No admins.</p>{% endif %}
            </div>
        </div>
    </div>
</body>
</html>
        '''
        return render_template_string(template, 
                                     students=_users_by_role('student'),
                                     teachers=_users_by_role('teacher'),
                                     admins=_users_by_role('admin'))
    return redirect(url_for('login'))

@app.route('/add_users', methods=['GET', 'POST'])
def add_users():
    message = None
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            valid_roles = {'student', 'teacher', 'admin'}
            final_role = role if role in valid_roles else 'student'
            users[username] = {'password': password, 'role': final_role}
            if final_role == 'student':
                name = (request.form.get('name') or '').strip()
                email = (request.form.get('email') or '').strip()
                address = (request.form.get('address') or '').strip()
                selected_courses = request.form.getlist('courses')
                normalized = [c.strip() for c in selected_courses if c.strip()]
                marks = {c: 0 for c in normalized}
                students_info[username] = {
                    'name': name or username,
                    'email': email,
                    'address': address,
                    'courses': normalized,
                    'marks': marks,
                }
            elif final_role == 'teacher':
                subject = (request.form.get('subject') or '').strip()
                teachers_info[username] = {'subject': subject or 'Unknown'}
            message = "User added successfully"
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Add Users</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        .form { margin: 20px auto; width: 360px; }
        .form input, .form select { padding: 10px; margin: 5px 0; width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        .form button { padding: 10px 20px; background: #5e35b1; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .form button:hover { background: #4a2a8c; }
        fieldset { border: 1px solid #ddd; border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
        legend { padding: 0 6px; color: #555; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Add Users</h1>
    <form class="form" method="post">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <select name="role" id="role" required>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
            <option value="admin">Admin</option>
        </select><br>
        <fieldset id="studentFields">
            <legend>Student Details (only used when role = student)</legend>
            <input type="text" name="name" placeholder="Full Name">
            <input type="email" name="email" placeholder="Email">
            <input type="text" name="address" placeholder="Address">
            <div>
                <label><input type="checkbox" name="courses" value="Math"> Math</label>
                <label><input type="checkbox" name="courses" value="Science"> Science</label>
                <label><input type="checkbox" name="courses" value="History"> History</label>
                <label><input type="checkbox" name="courses" value="Coding"> Coding</label>
            </div>
        </fieldset>
        <fieldset id="teacherFields">
            <legend>Teacher Details (only used when role = teacher)</legend>
            <input type="text" name="subject" placeholder="Subject taught (e.g., Math)">
        </fieldset>
        <script>
        (function(){
            var roleSel = document.getElementById('role');
            var sf = document.getElementById('studentFields');
            var tf = document.getElementById('teacherFields');
            function sync(){
                var v = roleSel.value;
                sf.style.display = (v === 'student') ? 'block' : 'none';
                tf.style.display = (v === 'teacher') ? 'block' : 'none';
            }
            roleSel.addEventListener('change', sync);
            sync();
        })();
        </script>
        <button type="submit">Add User</button>
    </form>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
    <a href="{{ url_for('admin_dashboard') }}">Back to Dashboard</a>
</body>
</html>
        '''
        return render_template_string(template, message=message)
    return redirect(url_for('login'))

@app.route('/admin/students')
def admin_students():
    if 'role' in session and session['role'] == 'admin':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Students</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        .card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 16px; max-width: 600px; }
        .title { margin-top: 0; }
        ul { line-height: 1.8; }
        a { color: #5e35b1; text-decoration: none; }
        button { background: #d32f2f; color: #fff; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #b71c1c; }
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
</head>
<body>
    <div class="card">
        <h1 class="title">Students ({{ students|length }})</h1>
        {% if students %}
        <ul>
            {% for s in students %}
            <li>
                {{ s }}
                <a href="{{ url_for('admin_edit_user', username=s) }}">Edit</a>
                <form method="post" action="{{ url_for('admin_delete_user', username=s) }}" style="display:inline" onsubmit="return confirm('Delete {{ s }}?')">
                    <button type="submit">Delete</button>
                </form>
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No students found.</p>
        {% endif %}
        <p><a href="{{ url_for('admin_dashboard') }}">Back to Admin Dashboard</a></p>
    </div>
</body>
</html>
        '''
        return render_template_string(template, students=_users_by_role('student'))
    return redirect(url_for('login'))

@app.route('/admin/teachers')
def admin_teachers():
    if 'role' in session and session['role'] == 'admin':
        template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Teachers</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        .card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 16px; max-width: 600px; }
        .title { margin-top: 0; }
        ul { line-height: 1.8; }
        a { color: #5e35b1; text-decoration: none; }
        button { background: #d32f2f; color: #fff; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #b71c1c; }
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
</head>
<body>
    <div class="card">
        <h1 class="title">Teachers ({{ teachers|length }})</h1>
        {% if teachers %}
        <ul>
            {% for t in teachers %}
            <li>
                {{ t }}
                <a href="{{ url_for('admin_edit_user', username=t) }}">Edit</a>
                <form method="post" action="{{ url_for('admin_delete_user', username=t) }}" style="display:inline" onsubmit="return confirm('Delete {{ t }}?')">
                    <button type="submit">Delete</button>
                </form>
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No teachers found.</p>
        {% endif %}
        <p><a href="{{ url_for('admin_dashboard') }}">Back to Admin Dashboard</a></p>
    </div>
</body>
</html>
        '''
        return render_template_string(template, teachers=_users_by_role('teacher'))
    return redirect(url_for('login'))

@app.route('/admin/user/<username>/edit', methods=['GET', 'POST'])
def admin_edit_user(username):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if username not in users:
        return redirect(url_for('admin_dashboard'))
    role = users[username]['role']
    if request.method == 'POST':
        new_pass = (request.form.get('password') or '').strip()
        if new_pass:
            users[username]['password'] = new_pass
        if role == 'student':
            name = (request.form.get('name') or '').strip()
            email = (request.form.get('email') or '').strip()
            address = (request.form.get('address') or '').strip()
            selected_courses = request.form.getlist('courses')
            normalized = [c.strip() for c in selected_courses if c.strip()]
            marks = students_info.get(username, {}).get('marks', {})
            new_marks = {c: int(marks.get(c, 0)) for c in normalized}
            students_info[username] = {
                'name': name or username,
                'email': email,
                'address': address,
                'courses': normalized,
                'marks': new_marks,
            }
        elif role == 'teacher':
            subject = (request.form.get('subject') or '').strip()
            teachers_info[username] = {'subject': subject or 'Unknown'}
        return redirect(url_for('admin_dashboard'))
    template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Edit User - {{ username }}</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f6f7fb; }
        .form { margin: 20px auto; width: 420px; }
        .form input { padding: 10px; margin: 6px 0; width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        .form button { padding: 10px 20px; background: #5e35b1; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .form button:hover { background: #4a2a8c; }
        fieldset { border: 1px solid #ddd; border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
        legend { padding: 0 6px; color: #555; }
        a { color: #5e35b1; text-decoration: none; }
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
</head>
<body>
    <h1>Edit User - {{ username }}</h1>
    <form class="form" method="post">
        <input type="password" name="password" placeholder="New Password (leave blank to keep)">
        {% if role == 'student' %}
        <fieldset>
            <legend>Student Details</legend>
            <input type="text" name="name" placeholder="Full Name" value="{{ (s_info and s_info.name) or '' }}">
            <input type="email" name="email" placeholder="Email" value="{{ (s_info and s_info.email) or '' }}">
            <input type="text" name="address" placeholder="Address" value="{{ (s_info and s_info.address) or '' }}">
            <div>
                {% set enrolled = (s_info and s_info.courses) or [] %}
                {% for c in ['Math','Science','History','Coding'] %}
                    <label><input type="checkbox" name="courses" value="{{ c }}" {% if c in enrolled %}checked{% endif %}> {{ c }}</label>
                {% endfor %}
            </div>
        </fieldset>
        {% elif role == 'teacher' %}
        <fieldset>
            <legend>Teacher Details</legend>
            <input type="text" name="subject" placeholder="Subject taught" value="{{ (t_info and t_info.subject) or '' }}">
        </fieldset>
        {% endif %}
        <button type="submit">Save Changes</button>
    </form>
    <p><a href="{{ url_for('admin_dashboard') }}">Back to Admin Dashboard</a></p>
</body>
</html>
    '''
    return render_template_string(template, username=username, role=role, 
                                 s_info=students_info.get(username), t_info=teachers_info.get(username))

@app.route('/admin/user/<username>/delete', methods=['POST'])
def admin_delete_user(username):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if username == session.get('username'):
        return redirect(url_for('admin_dashboard'))
    users.pop(username, None)
    students_info.pop(username, None)
    teachers_info.pop(username, None)
    return redirect(url_for('admin_dashboard'))

@app.route('/ui_dashboard')
def ui_dashboard():
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edvision360 - Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color: #222; background: #f6f7fb; }
        .dashboard { display: flex; min-height: 100vh; }
        .sidebar { width: 260px; background: #fff; border-right: 1px solid #eee; padding: 18px; position: sticky; top: 0; height: 100vh; }
        .sidebar-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .sidebar .nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin: 6px 0; color: #333; text-decoration: none; border-radius: 8px; }
        .sidebar .nav-item.active, .sidebar .nav-item:hover { background: #f1f0ff; color: #4a35b1; }
        .main-content { flex: 1; display: flex; flex-direction: column; }
        .top-bar { background: #fff; border-bottom: 1px solid #eee; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; }
        .content-area { padding: 18px; }
        .section-header { margin: 10px 0 6px; }
        .section-title { display: inline-flex; align-items: center; gap: 8px; font-size: 18px; margin: 0; }
        .events-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
        .event-card { background: #fff; border: 1px solid #eee; border-radius: 12px; overflow: hidden; }
        .event-image img { width: 100%; height: 160px; object-fit: cover; display: block; }
        .event-info { display: flex; gap: 12px; padding: 12px; }
        .event-tags { display: flex; gap: 8px; padding: 0 12px 12px; align-items: center; }
        .event-tag { font-size: 12px; background: #f0f7ff; color: #0d47a1; padding: 4px 8px; border-radius: 999px; }
        .btn-primary { background: #5e35b1; color: #fff; border: none; padding: 10px 14px; border-radius: 10px; cursor: pointer; }
        .btn-primary:hover { background: #4a2a8c; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="logo"><i class="fas fa-calendar-check"></i></div>
                <div>
                    <h2>Edvision360</h2>
                    <p>Student Success Intelligence</p>
                </div>
            </div>
            <div class="nav-section">
                <a class="nav-item active" href="{{ url_for('ui_dashboard') }}"><i class="fas fa-home"></i><span>Home</span></a>
                <a class="nav-item" href="#"><i class="fas fa-calendar-alt"></i><span>Events</span></a>
                <a class="nav-item" href="#"><i class="fas fa-clipboard-list"></i><span>Registrations</span></a>
                <a class="nav-item" href="#"><i class="fas fa-clock"></i><span>Schedule</span></a>
                <a class="nav-item" href="#"><i class="fas fa-trophy"></i><span>Results</span></a>
                <a class="nav-item" href="#"><i class="fas fa-images"></i><span>Gallery</span></a>
                <a class="nav-item" href="#"><i class="fas fa-handshake"></i><span>Sponsors</span></a>
                <a class="nav-item" href="#"><i class="fas fa-phone"></i><span>Contact</span></a>
                <a class="nav-item" href="#"><i class="fas fa-user"></i><span>Profile</span></a>
            </div>
            <div class="user-section">
                <div class="user-avatar">G</div>
                <div class="user-info">
                    <h4>Guest User</h4>
                    <p>Guest User</p>
                </div>
            </div>
        </div>
        <div class="main-content">
            <div class="top-bar">
                <div class="search-bar"><i class="fas fa-search"></i> <input type="text" placeholder="Search..." style="border:none; outline:none"></div>
                <div class="top-bar-actions"><div class="notification-icon"><i class="fas fa-bell"></i></div><div class="user-menu">G</div></div>
            </div>
            <div class="content-area">
                <div class="section-header">
                    <h2 class="section-title"><i class="fas fa-calendar"></i> Upcoming Events</h2>
                </div>
                <p>Don't miss out on these exciting events!</p>
                <div class="events-list">
                    <div class="event-card">
                        <div class="event-image"><img src="https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80" alt="Tech Innovation Summit"></div>
                        <div class="event-info">
                            <div class="event-date">
                                <div class="event-date-day">15</div>
                                <div class="event-date-month">Mar</div>
                            </div>
                            <div class="event-details">
                                <h3>Tech Innovation Summit</h3>
                                <div class="event-meta">
                                    <div class="event-meta-item"><i class="fas fa-clock"></i><span>09:00 AM</span></div>
                                    <div class="event-meta-item"><i class="fas fa-map-marker-alt"></i><span>Main Auditorium</span></div>
                                </div>
                            </div>
                        </div>
                        <div class="event-tags"><div class="event-tag">Technology</div><div class="event-tag">Registered</div></div>
                    </div>
                    <div class="event-card">
                        <div class="event-image"><img src="https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&w=600&q=80" alt="Cultural Festival"></div>
                        <div class="event-info">
                            <div class="event-date"><div class="event-date-day">18</div><div class="event-date-month">Mar</div></div>
                            <div class="event-details"><h3>Cultural Festival</h3>
                                <div class="event-meta">
                                    <div class="event-meta-item"><i class="fas fa-clock"></i><span>02:00 PM</span></div>
                                    <div class="event-meta-item"><i class="fas fa-map-marker-alt"></i><span>Campus Ground</span></div>
                                </div>
                            </div>
                        </div>
                        <div class="event-tags"><div class="event-tag">Cultural</div><button class="btn-primary">Register</button></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)

