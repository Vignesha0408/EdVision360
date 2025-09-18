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

# Enhanced attendance data
attendance_records = {
    'Sai': {
        '2025-09-01': 'Present', '2025-09-02': 'Present', '2025-09-03': 'Absent',
        '2025-09-04': 'Present', '2025-09-05': 'Present', '2025-09-06': 'Present',
        '2025-09-07': 'Present', '2025-09-08': 'Absent', '2025-09-09': 'Present',
        '2025-09-10': 'Present', '2025-09-11': 'Present', '2025-09-12': 'Present',
        '2025-09-13': 'Present', '2025-09-14': 'Present', '2025-09-15': 'Absent',
        '2025-09-16': 'Present', '2025-09-17': 'Present', '2025-09-18': 'Present'
    },
    'Gopi': {
        '2025-09-01': 'Present', '2025-09-02': 'Absent', '2025-09-03': 'Present',
        '2025-09-04': 'Present', '2025-09-05': 'Present', '2025-09-06': 'Absent',
        '2025-09-07': 'Present', '2025-09-08': 'Present', '2025-09-09': 'Present',
        '2025-09-10': 'Absent', '2025-09-11': 'Present', '2025-09-12': 'Present',
        '2025-09-13': 'Present', '2025-09-14': 'Present', '2025-09-15': 'Present',
        '2025-09-16': 'Present', '2025-09-17': 'Absent', '2025-09-18': 'Present'
    },
    'Rani': {
        '2025-09-01': 'Present', '2025-09-02': 'Present', '2025-09-03': 'Present',
        '2025-09-04': 'Present', '2025-09-05': 'Absent', '2025-09-06': 'Present',
        '2025-09-07': 'Present', '2025-09-08': 'Present', '2025-09-09': 'Present',
        '2025-09-10': 'Present', '2025-09-11': 'Present', '2025-09-12': 'Absent',
        '2025-09-13': 'Present', '2025-09-14': 'Present', '2025-09-15': 'Present',
        '2025-09-16': 'Present', '2025-09-17': 'Present', '2025-09-18': 'Present'
    },
    'Vimal': {
        '2025-09-01': 'Present', '2025-09-02': 'Present', '2025-09-03': 'Present',
        '2025-09-04': 'Absent', '2025-09-05': 'Present', '2025-09-06': 'Present',
        '2025-09-07': 'Present', '2025-09-08': 'Present', '2025-09-09': 'Absent',
        '2025-09-10': 'Present', '2025-09-11': 'Present', '2025-09-12': 'Present',
        '2025-09-13': 'Present', '2025-09-14': 'Absent', '2025-09-15': 'Present',
        '2025-09-16': 'Present', '2025-09-17': 'Present', '2025-09-18': 'Present'
    }
}

# Student enrollment data
student_enrollments = {
    'Sai': ['Math', 'Science'],
    'Gopi': ['Math', 'History'],
    'Rani': ['Science', 'History'],
    'Vimal': ['Math', 'Science', 'History']
}

# Helper function to get users by role
def _users_by_role(role_name):
    return [u for u, meta in users.items() if meta.get('role') == role_name]

# Add a notifications system
notifications = {
    'student': [
        {'id': 1, 'title': 'Assignment Due', 'message': 'Math homework due tomorrow', 'type': 'warning', 'time': '2 hours ago'},
        {'id': 2, 'title': 'New Course Material', 'message': 'Science chapter 5 uploaded', 'type': 'info', 'time': '1 day ago'},
        {'id': 3, 'title': 'Grade Released', 'message': 'History quiz results available', 'type': 'success', 'time': '3 days ago'}
    ],
    'teacher': [
        {'id': 1, 'title': 'Grade Submission', 'message': '5 assignments pending review', 'type': 'warning', 'time': '1 hour ago'},
        {'id': 2, 'title': 'Parent Meeting', 'message': 'Meeting scheduled for tomorrow', 'type': 'info', 'time': '4 hours ago'}
    ],
    'admin': [
        {'id': 1, 'title': 'System Update', 'message': 'Scheduled maintenance tonight', 'type': 'warning', 'time': '30 minutes ago'},
        {'id': 2, 'title': 'New Registration', 'message': '3 new student registrations', 'type': 'success', 'time': '2 hours ago'}
    ]
}

# Add route for notifications
@app.route('/notifications')
def get_notifications():
    if 'role' not in session:
        return redirect(url_for('login'))
    
    user_role = session.get('role', 'student')
    user_notifications = notifications.get(user_role, [])
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notifications - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .notifications-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .notification-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        .notification-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        .notification-card.warning {
            border-left-color: #f39c12;
        }
        .notification-card.success {
            border-left-color: #27ae60;
        }
        .notification-card.error {
            border-left-color: #e74c3c;
        }
        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .notification-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .notification-time {
            color: #7f8c8d;
            font-size: 0.85rem;
        }
        .notification-message {
            color: #5a6c7d;
            line-height: 1.5;
        }
        .notification-icon {
            font-size: 1.2rem;
        }
        .notification-icon.info { color: #3498db; }
        .notification-icon.warning { color: #f39c12; }
        .notification-icon.success { color: #27ae60; }
        .notification-icon.error { color: #e74c3c; }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .empty-icon {
            font-size: 4rem;
            color: #bdc3c7;
            margin-bottom: 20px;
        }
        .empty-title {
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .empty-message {
            color: #7f8c8d;
        }
        .clear-single-btn {
            background: transparent;
            border: none;
            color: #bdc3c7;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            font-size: 0.8rem;
        }
        .clear-single-btn:hover {
            background: #f8f9fa;
            color: #e74c3c;
        }
        .clear-all-btn {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .clear-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(231, 76, 60, 0.3);
        }
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        .toast.show {
            transform: translateX(0);
        }
        .toast.error {
            background: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-bell"></i>
                Notifications
            </h1>
            <div style="display: flex; gap: 10px;">
                <button class="clear-all-btn" onclick="clearAllNotifications()">
                    <i class="fas fa-trash"></i> Clear All
                </button>
                <a href="{{ url_for(user_role + '_dashboard') }}" class="back-btn">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
        
        {% if user_notifications %}
        <div class="notifications-list" id="notificationsList">
            {% for notification in user_notifications %}
            <div class="notification-card {{ notification.type }}" data-notification-id="{{ notification.id }}">
                <div class="notification-header">
                    <div class="notification-title">
                        <i class="fas {% if notification.type == 'warning' %}fa-exclamation-triangle{% elif notification.type == 'success' %}fa-check-circle{% elif notification.type == 'error' %}fa-times-circle{% else %}fa-info-circle{% endif %} notification-icon {{ notification.type }}"></i>
                        {{ notification.title }}
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="notification-time">{{ notification.time }}</div>
                        <button class="clear-single-btn" onclick="clearSingleNotification({{ notification.id }})" title="Clear this notification">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="notification-message">{{ notification.message }}</div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <div class="empty-icon">
                <i class="fas fa-bell-slash"></i>
            </div>
            <div class="empty-title">No notifications</div>
            <div class="empty-message">You're all caught up! Check back later for updates.</div>
        </div>
        {% endif %}
    </div>

    <script>
        function clearAllNotifications() {
            const notificationsList = document.getElementById('notificationsList');
            if (notificationsList) {
                notificationsList.innerHTML = '';
                showToast('All notifications cleared successfully!');
                
                // If no notifications left, show empty state
                setTimeout(() => {
                    const container = document.querySelector('.container');
                    const emptyState = `
                        <div class="empty-state">
                            <div class="empty-icon">
                                <i class="fas fa-bell-slash"></i>
                            </div>
                            <div class="empty-title">No notifications</div>
                            <div class="empty-message">You're all caught up! Check back later for updates.</div>
                        </div>
                    `;
                    notificationsList.outerHTML = emptyState;
                }, 300);
            }
        }
        
        function clearSingleNotification(notificationId) {
            const notificationCard = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationCard) {
                notificationCard.style.transform = 'translateX(100%)';
                notificationCard.style.opacity = '0';
                
                setTimeout(() => {
                    notificationCard.remove();
                    
                    // Check if there are any notifications left
                    const remainingNotifications = document.querySelectorAll('.notification-card');
                    if (remainingNotifications.length === 0) {
                        const notificationsList = document.getElementById('notificationsList');
                        if (notificationsList) {
                            const emptyState = `
                                <div class="empty-state">
                                    <div class="empty-icon">
                                        <i class="fas fa-bell-slash"></i>
                                    </div>
                                    <div class="empty-title">No notifications</div>
                                    <div class="empty-message">You're all caught up! Check back later for updates.</div>
                                </div>
                            `;
                            notificationsList.outerHTML = emptyState;
                        }
                    }
                }, 300);
                
                showToast('Notification cleared!');
            }
        }
        
        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
                ${message}
            `;
            
            document.body.appendChild(toast);
            
            // Show toast
            setTimeout(() => {
                toast.classList.add('show');
            }, 100);
            
            // Hide toast after 3 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            }, 3000);
        }
    </script>
</body>
</html>
    '''
    return render_template_string(template, user_notifications=user_notifications, user_role=user_role)

# Routes and Templates
@app.route('/')
def index():
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edvision360 - Educational Intelligence Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            color: white;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            animation: fadeInUp 1s ease-out;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 20px;
            color: #ffd700;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ffd700, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        .portal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .portal-card {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 30px 20px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .portal-card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.2);
            border-color: #ffd700;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }
        .portal-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            display: block;
        }
        .portal-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .portal-desc {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        .features {
            margin-top: 50px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .feature {
            text-align: left;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border-left: 4px solid #ffd700;
        }
        .feature-icon {
            color: #ffd700;
            margin-right: 10px;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .floating-shapes {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            z-index: -1;
        }
        .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }
        .shape:nth-child(1) { width: 80px; height: 80px; top: 20%; left: 10%; animation-delay: 0s; }
        .shape:nth-child(2) { width: 120px; height: 120px; top: 70%; left: 20%; animation-delay: 2s; }
        .shape:nth-child(3) { width: 60px; height: 60px; top: 40%; right: 10%; animation-delay: 4s; }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
    </style>
</head>
<body>
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    
    <div class="container">
        <div class="logo">
            <i class="fas fa-graduation-cap"></i>
        </div>
        <h1>Edvision360</h1>
        <p class="subtitle">Educational Intelligence Platform - Transforming Learning Experience</p>
        
        <div class="portal-grid">
            <a href="{{ url_for('login', portal='student') }}" class="portal-card">
                <i class="fas fa-user-graduate portal-icon"></i>
                <div class="portal-title">Student Portal</div>
                <div class="portal-desc">Access courses, track progress, view scores</div>
            </a>
            <a href="{{ url_for('login', portal='teacher') }}" class="portal-card">
                <i class="fas fa-chalkboard-teacher portal-icon"></i>
                <div class="portal-title">Teacher Portal</div>
                <div class="portal-desc">Manage classes, update attendance, grade students</div>
            </a>
            <a href="{{ url_for('login', portal='admin') }}" class="portal-card">
                <i class="fas fa-user-shield portal-icon"></i>
                <div class="portal-title">Admin Portal</div>
                <div class="portal-desc">System administration, user management</div>
            </a>
        </div>
        
        <div class="features">
            <div class="feature">
                <i class="fas fa-chart-line feature-icon"></i>
                <strong>Real-time Analytics</strong><br>
                Track student progress and performance with advanced analytics
            </div>
            <div class="feature">
                <i class="fas fa-mobile-alt feature-icon"></i>
                <strong>Mobile Responsive</strong><br>
                Access your dashboard from any device, anywhere
            </div>
            <div class="feature">
                <i class="fas fa-shield-alt feature-icon"></i>
                <strong>Secure Platform</strong><br>
                Your data is protected with enterprise-grade security
            </div>
        </div>
    </div>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - {{ portal|title }} Portal</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 400px;
            animation: slideInDown 0.6s ease-out;
        }
        .portal-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .portal-icon {
            font-size: 3rem;
            color: #5e35b1;
            margin-bottom: 15px;
        }
        .portal-title {
            font-size: 1.8rem;
            color: #333;
            margin-bottom: 5px;
        }
        .portal-subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        .form-group {
            margin-bottom: 20px;
            position: relative;
        }
        .form-group input {
            width: 100%;
            padding: 15px 20px 15px 50px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        .form-group input:focus {
            outline: none;
            border-color: #5e35b1;
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(94, 53, 177, 0.2);
        }
        .form-group i {
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: #999;
            font-size: 1.1rem;
        }
        .login-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #5e35b1, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(94, 53, 177, 0.3);
        }
        .error-message {
            background: #fee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #c62828;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #5e35b1;
            text-decoration: none;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.3s ease;
        }
        .back-link a:hover {
            color: #4a2a8c;
            transform: translateX(-5px);
        }
        .demo-credentials {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.85rem;
        }
        .demo-credentials h4 {
            color: #1976d2;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        .demo-credentials p {
            margin: 3px 0;
            color: #424242;
        }
        @keyframes slideInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="portal-header">
            {% if portal == 'student' %}
                <i class="fas fa-user-graduate portal-icon"></i>
            {% elif portal == 'teacher' %}
                <i class="fas fa-chalkboard-teacher portal-icon"></i>
            {% else %}
                <i class="fas fa-user-shield portal-icon"></i>
            {% endif %}
            <h1 class="portal-title">{{ portal|title }} Portal</h1>
            <p class="portal-subtitle">Welcome back! Please sign in to continue.</p>
        </div>
        
        {% if error %}
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                {{ error }}
            </div>
        {% endif %}
        
        <div class="demo-credentials">
            <h4><i class="fas fa-info-circle"></i> Demo Credentials</h4>
            {% if portal == 'student' %}
                <p><strong>Students:</strong> student/student, Sai/Sai, Gopi/Gopi</p>
            {% elif portal == 'teacher' %}
                <p><strong>Teachers:</strong> teacher/teacher, Sushma/Sushma, Ram/Ram</p>
            {% else %}
                <p><strong>Admin:</strong> admin/admin</p>
            {% endif %}
        </div>
        
        <form method="post">
            <input type="hidden" name="portal" value="{{ portal }}">
            
            <div class="form-group">
                <i class="fas fa-user"></i>
                <input type="text" name="username" placeholder="Username" required autocomplete="username">
            </div>
            
            <div class="form-group">
                <i class="fas fa-lock"></i>
                <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-sign-in-alt"></i> Sign In
            </button>
        </form>
        
        <div class="back-link">
            <a href="{{ url_for('index') }}">
                <i class="fas fa-arrow-left"></i> Back to Home
            </a>
        </div>
    </div>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Dashboard - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .dashboard { display: flex; min-height: 100vh; }
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0,0,0,0.1);
        }
        .sidebar-header {
            padding: 25px 20px;
            background: rgba(0,0,0,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .sidebar-header h2 {
            font-size: 1.4rem;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .sidebar-header p {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        .nav-menu {
            padding: 20px 0;
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 25px;
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(255,255,255,0.1);
            border-left-color: #ffd700;
            color: white;
        }
        .nav-item i {
            width: 20px;
            text-align: center;
            font-size: 1.1rem;
        }
        .main-content {
            flex: 1;
            margin-left: 280px;
            background: #f5f7fa;
        }
        .top-bar {
            background: white;
            padding: 20px 30px;
            border-bottom: 1px solid #e1e8ed;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .welcome-text {
            font-size: 1.5rem;
            color: #2c3e50;
            font-weight: 600;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
            color: #5a6c7d;
        }
        .notification-bell {
            position: relative;
            cursor: pointer;
            padding: 10px;
            border-radius: 50%;
            transition: all 0.3s ease;
        }
        .notification-bell:hover {
            background: #f8f9fa;
        }
        .notification-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            background: #e74c3c;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        .notification-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            width: 350px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border: 1px solid #e1e8ed;
            z-index: 1000;
            display: none;
            max-height: 400px;
            overflow-y: auto;
        }
        .notification-dropdown.show {
            display: block;
            animation: slideDown 0.3s ease;
        }
        .dropdown-header {
            padding: 15px 20px;
            border-bottom: 1px solid #e1e8ed;
            font-weight: 600;
            color: #2c3e50;
        }
        .dropdown-item {
            padding: 15px 20px;
            border-bottom: 1px solid #f8f9fa;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        .dropdown-item:hover {
            background: #f8f9fa;
        }
        .dropdown-item:last-child {
            border-bottom: none;
        }
        .dropdown-title {
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .dropdown-message {
            font-size: 0.85rem;
            color: #5a6c7d;
            margin-bottom: 5px;
        }
        .dropdown-time {
            font-size: 0.75rem;
            color: #95a5a6;
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .content-area {
            padding: 30px;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .stat-title {
            color: #5a6c7d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-icon {
            font-size: 1.5rem;
            color: #3498db;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
        }
        .courses-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
        }
        .course-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .course-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        .course-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .course-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .course-subtitle {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .course-body {
            padding: 25px;
        }
        .course-progress {
            margin-bottom: 20px;
        }
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #5a6c7d;
        }
        .progress-bar {
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        .course-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .btn-outline {
            background: transparent;
            color: #3498db;
            border: 2px solid #3498db;
        }
        .btn-outline:hover {
            background: #3498db;
            color: white;
        }
        .quick-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .quick-stat {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }
        .quick-stat-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .quick-stat-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
        }
        .quick-stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .sidebar { transform: translateX(-100%); }
            .main-content { margin-left: 0; }
            .top-bar { padding: 15px 20px; }
            .content-area { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2><i class="fas fa-graduation-cap"></i> Edvision360</h2>
                <p>Student Portal</p>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('student_dashboard') }}" class="nav-item active">
                    <i class="fas fa-home"></i> Dashboard
                </a>
                <a href="{{ url_for('student_scores_page') }}" class="nav-item">
                    <i class="fas fa-chart-bar"></i> Scores
                </a>
                <a href="{{ url_for('progress_page') }}" class="nav-item">
                    <i class="fas fa-chart-line"></i> Progress
                </a>
                <a href="{{ url_for('certificates_page') }}" class="nav-item">
                    <i class="fas fa-certificate"></i> Certificates
                </a>
                <a href="{{ url_for('schedule_page') }}" class="nav-item">
                    <i class="fas fa-calendar-alt"></i> Schedule
                </a>
                <a href="{{ url_for('discussions_page') }}" class="nav-item">
                    <i class="fas fa-comments"></i> Discussions
                </a>
                <a href="{{ url_for('profile_page') }}" class="nav-item">
                    <i class="fas fa-user"></i> Profile
                </a>
                <a href="{{ url_for('logout') }}" class="nav-item">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </nav>
        
        <main class="main-content">
            <div class="top-bar">
                <div class="welcome-text">
                    <i class="fas fa-sun" style="color: #f39c12; margin-right: 10px;"></i>
                    Good day, {{ username or 'Student' }}!
                </div>
                <div class="user-info" style="position: relative;">
                    <div class="notification-bell" onclick="toggleNotifications()">
                        <i class="fas fa-bell"></i>
                        <span class="notification-badge">3</span>
                    </div>
                    <div class="notification-dropdown" id="notificationDropdown">
                        <div class="dropdown-header">
                            <i class="fas fa-bell"></i> Recent Notifications
                        </div>
                        <div class="dropdown-item">
                            <div class="dropdown-title">Assignment Due</div>
                            <div class="dropdown-message">Math homework due tomorrow</div>
                            <div class="dropdown-time">2 hours ago</div>
                        </div>
                        <div class="dropdown-item">
                            <div class="dropdown-title">New Course Material</div>
                            <div class="dropdown-message">Science chapter 5 uploaded</div>
                            <div class="dropdown-time">1 day ago</div>
                        </div>
                        <div class="dropdown-item">
                            <div class="dropdown-title">Grade Released</div>
                            <div class="dropdown-message">History quiz results available</div>
                            <div class="dropdown-time">3 days ago</div>
                        </div>
                        <div class="dropdown-item" style="text-align: center; color: #3498db; font-weight: 500;">
                            <a href="{{ url_for('get_notifications') }}" style="color: inherit; text-decoration: none;">
                                View All Notifications
                            </a>
                        </div>
                    </div>
                    <i class="fas fa-user-circle" style="font-size: 1.5rem; margin-left: 15px;"></i>
                    <span>{{ username or 'Student' }}</span>
                </div>
            </div>
            
            <div class="content-area">
                <h1 class="page-title">
                    <i class="fas fa-tachometer-alt"></i>
                    Student Dashboard
                </h1>
                
                <div class="quick-stats">
                    <div class="quick-stat">
                        <div class="quick-stat-icon" style="color: #3498db;">
                            <i class="fas fa-book-open"></i>
                        </div>
                        <div class="quick-stat-value">{{ courses|length }}</div>
                        <div class="quick-stat-label">Active Courses</div>
                    </div>
                    <div class="quick-stat">
                        <div class="quick-stat-icon" style="color: #28a745;">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="quick-stat-value">87%</div>
                        <div class="quick-stat-label">Average Score</div>
                    </div>
                    <div class="quick-stat">
                        <div class="quick-stat-icon" style="color: #fd7e14;">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="quick-stat-value">24h</div>
                        <div class="quick-stat-label">Study Time</div>
                    </div>
                    <div class="quick-stat">
                        <div class="quick-stat-icon" style="color: #e83e8c;">
                            <i class="fas fa-medal"></i>
                        </div>
                        <div class="quick-stat-value">{{ certificates|length }}</div>
                        <div class="quick-stat-label">Certificates</div>
                    </div>
                </div>
                
                <h2 style="margin-bottom: 20px; color: #2c3e50; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-book"></i> My Courses
                </h2>
                
                <div class="courses-grid">
                    {% for course in courses %}
                    <div class="course-card">
                        <div class="course-header">
                            <div class="course-title">{{ course }}</div>
                            <div class="course-subtitle">Interactive Learning</div>
                        </div>
                        <div class="course-body">
                            <div class="course-progress">
                                <div class="progress-label">
                                    <span>Progress</span>
                                    <span>{{ progress.get(course, '0%') }}</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {{ progress.get(course, '0%') }}"></div>
                                </div>
                            </div>
                            <div class="course-actions">
                                <a href="{{ url_for('syllabus_page', course_name=course) }}" class="btn btn-primary">
                                    <i class="fas fa-play"></i> Continue
                                </a>
                                <a href="{{ url_for('syllabus_page', course_name=course) }}" class="btn btn-outline">
                                    <i class="fas fa-list"></i> Syllabus
                                </a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </main>
    </div>
    
    <script>
        function toggleNotifications() {
            const dropdown = document.getElementById('notificationDropdown');
            dropdown.classList.toggle('show');
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('notificationDropdown');
            const bell = document.querySelector('.notification-bell');
            
            if (!bell.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.classList.remove('show');
            }
        });
        
        // Animate cards on load
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.course-card, .quick-stat');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
        '''
        return render_template_string(template, courses=courses, username=session.get('username'), 
                                     progress=progress, certificates=certificates)
    return redirect(url_for('login'))

@app.route('/syllabus/<course_name>')
def syllabus_page(course_name):
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ course }} Syllabus - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .course-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        .course-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .course-icon {
            width: 80px;
            height: 80px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
        }
        .course-details h1 {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .course-meta {
            display: flex;
            gap: 20px;
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            align-self: flex-start;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .course-description {
            color: #5a6c7d;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        .course-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.85rem;
        }
        .syllabus-content {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 30px;
        }
        .main-syllabus {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .syllabus-header {
            background: linear-gradient(135deg, var(--course-color-light), var(--course-color-dark));
            color: white;
            padding: 25px 30px;
            text-align: center;
        }
        .syllabus-title {
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .syllabus-subtitle {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .topics-list {
            padding: 30px;
        }
        .topic-item {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            padding: 20px 0;
            border-bottom: 1px solid #f1f3f4;
        }
        .topic-item:last-child {
            border-bottom: none;
        }
        .topic-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--course-color-light);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            flex-shrink: 0;
        }
        .topic-content {
            flex: 1;
        }
        .topic-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .topic-description {
            color: #5a6c7d;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        .topic-duration {
            display: flex;
            align-items: center;
            gap: 5px;
            color: #7f8c8d;
            font-size: 0.85rem;
        }
        .sidebar-content {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .info-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .info-list {
            list-style: none;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f8f9fa;
        }
        .info-item:last-child {
            border-bottom: none;
        }
        .info-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .info-value {
            color: #2c3e50;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: var(--course-color-light);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .resources-list {
            list-style: none;
        }
        .resource-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0;
            color: #3498db;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .resource-item:hover {
            color: #2980b9;
            transform: translateX(5px);
        }
        .resource-icon {
            width: 16px;
            text-align: center;
        }
        @media (max-width: 768px) {
            .syllabus-content {
                grid-template-columns: 1fr;
            }
            .course-header {
                flex-direction: column;
                gap: 20px;
            }
            .course-info {
                flex-direction: column;
                text-align: center;
            }
            .course-stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="course-header">
                <div class="course-info">
                    <div class="course-icon" style="
                        {% if course == 'Math' %}background: linear-gradient(135deg, #e74c3c, #c0392b); --course-color-light: #e74c3c; --course-color-dark: #c0392b;{% endif %}
                        {% if course == 'Science' %}background: linear-gradient(135deg, #2ecc71, #27ae60); --course-color-light: #2ecc71; --course-color-dark: #27ae60;{% endif %}
                        {% if course == 'History' %}background: linear-gradient(135deg, #f39c12, #e67e22); --course-color-light: #f39c12; --course-color-dark: #e67e22;{% endif %}
                        {% if course == 'Coding' %}background: linear-gradient(135deg, #9b59b6, #8e44ad); --course-color-light: #9b59b6; --course-color-dark: #8e44ad;{% endif %}
                    ">
                        {% if course == 'Math' %}<i class="fas fa-calculator"></i>{% endif %}
                        {% if course == 'Science' %}<i class="fas fa-flask"></i>{% endif %}
                        {% if course == 'History' %}<i class="fas fa-scroll"></i>{% endif %}
                        {% if course == 'Coding' %}<i class="fas fa-code"></i>{% endif %}
                    </div>
                    <div class="course-details">
                        <h1>{{ course }} Course</h1>
                        <div class="course-meta">
                            <div class="meta-item">
                                <i class="fas fa-user-tie"></i>
                                <span>Prof. Dr. Smith</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-calendar"></i>
                                <span>Fall 2025</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-clock"></i>
                                <span>3 Credits</span>
                            </div>
                        </div>
                    </div>
                </div>
                <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
            
            <div class="course-description">
                {% if course == 'Math' %}
                    Comprehensive mathematics course covering algebra, geometry, trigonometry, and calculus fundamentals. Build strong mathematical foundations for advanced studies.
                {% elif course == 'Science' %}
                    Explore the fascinating world of science through physics, chemistry, and biology. Hands-on experiments and theoretical knowledge combined.
                {% elif course == 'History' %}
                    Journey through time from ancient civilizations to modern era. Understand how historical events shaped our present world.
                {% elif course == 'Coding' %}
                    Learn programming fundamentals, data structures, and algorithms. Build real-world applications using modern programming languages.
                {% else %}
                    Comprehensive course designed to provide deep understanding and practical skills in {{ course }}.
                {% endif %}
            </div>
            
            <div class="course-stats">
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--course-color-light);">{{ topics|length }}</div>
                    <div class="stat-label">Topics</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--course-color-light);">12</div>
                    <div class="stat-label">Weeks</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--course-color-light);">45</div>
                    <div class="stat-label">Hours</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--course-color-light);">85%</div>
                    <div class="stat-label">Your Score</div>
                </div>
            </div>
        </div>
        
        <div class="syllabus-content">
            <div class="main-syllabus">
                <div class="syllabus-header" style="background: linear-gradient(135deg, var(--course-color-light), var(--course-color-dark));">
                    <div class="syllabus-title">Course Syllabus</div>
                    <div class="syllabus-subtitle">Detailed curriculum and learning objectives</div>
                </div>
                <div class="topics-list">
                    {% for topic in topics %}
                    <div class="topic-item">
                        <div class="topic-number" style="background: var(--course-color-light);">{{ loop.index }}</div>
                        <div class="topic-content">
                            <div class="topic-title">{{ topic }}</div>
                            <div class="topic-description">
                                {% if course == 'Math' %}
                                    {% if 'Algebra' in topic %}Master linear equations, polynomials, and algebraic expressions{% endif %}
                                    {% if 'Geometry' in topic %}Explore shapes, angles, and spatial relationships{% endif %}
                                    {% if 'Trigonometry' in topic %}Study triangles, angles, and trigonometric functions{% endif %}
                                    {% if 'Calculus' in topic %}Introduction to derivatives and integrals{% endif %}
                                {% elif course == 'Science' %}
                                    {% if 'Physics' in topic %}Fundamental principles of motion, energy, and forces{% endif %}
                                    {% if 'Chemistry' in topic %}Atomic structure, chemical reactions, and molecular behavior{% endif %}
                                    {% if 'Biology' in topic %}Living organisms, cells, and biological processes{% endif %}
                                    {% if 'Lab' in topic %}Hands-on experiments and practical applications{% endif %}
                                {% elif course == 'History' %}
                                    {% if 'Ancient' in topic %}Early civilizations and their contributions{% endif %}
                                    {% if 'Medieval' in topic %}Middle Ages, feudalism, and cultural developments{% endif %}
                                    {% if 'Modern' in topic %}Industrial revolution and contemporary events{% endif %}
                                    {% if 'Contemporary' in topic %}20th and 21st century global developments{% endif %}
                                {% elif course == 'Coding' %}
                                    {% if 'Programming' in topic %}Basic programming concepts and syntax{% endif %}
                                    {% if 'Control' in topic %}Loops, conditionals, and program flow{% endif %}
                                    {% if 'Data' in topic %}Arrays, objects, and data manipulation{% endif %}
                                    {% if 'Projects' in topic %}Real-world applications and portfolio building{% endif %}
                                {% else %}
                                    Comprehensive study of {{ topic.lower() }} principles and applications
                                {% endif %}
                            </div>
                            <div class="topic-duration">
                                <i class="fas fa-clock"></i>
                                <span>{{ 3 if loop.index <= 2 else 2 }} weeks</span>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="sidebar-content">
                <div class="info-card">
                    <h3 class="card-title">
                        <i class="fas fa-info-circle"></i>
                        Course Information
                    </h3>
                    <ul class="info-list">
                        <li class="info-item">
                            <span class="info-label">Instructor</span>
                            <span class="info-value">Prof. Dr. Smith</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Duration</span>
                            <span class="info-value">12 Weeks</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Credits</span>
                            <span class="info-value">3 Credits</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Level</span>
                            <span class="info-value">Intermediate</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Prerequisites</span>
                            <span class="info-value">{% if course == 'Math' %}Basic Algebra{% elif course == 'Science' %}General Science{% elif course == 'History' %}None{% elif course == 'Coding' %}Basic Computer Skills{% else %}None{% endif %}</span>
                        </li>
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3 class="card-title">
                        <i class="fas fa-chart-line"></i>
                        Your Progress
                    </h3>
                    <div style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #5a6c7d; font-size: 0.9rem;">Completion</span>
                            <span style="color: #2c3e50; font-weight: 600;">75%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 75%; background: var(--course-color-light);"></div>
                        </div>
                    </div>
                    <ul class="info-list">
                        <li class="info-item">
                            <span class="info-label">Completed Topics</span>
                            <span class="info-value">3/4</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Current Score</span>
                            <span class="info-value">85%</span>
                        </li>
                        <li class="info-item">
                            <span class="info-label">Attendance</span>
                            <span class="info-value">92%</span>
                        </li>
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3 class="card-title">
                        <i class="fas fa-download"></i>
                        Resources
                    </h3>
                    <ul class="resources-list">
                        <li class="resource-item">
                            <i class="fas fa-file-pdf resource-icon"></i>
                            <span>Course Textbook (PDF)</span>
                        </li>
                        <li class="resource-item">
                            <i class="fas fa-video resource-icon"></i>
                            <span>Video Lectures</span>
                        </li>
                        <li class="resource-item">
                            <i class="fas fa-tasks resource-icon"></i>
                            <span>Practice Exercises</span>
                        </li>
                        <li class="resource-item">
                            <i class="fas fa-clipboard-list resource-icon"></i>
                            <span>Assignment Templates</span>
                        </li>
                        <li class="resource-item">
                            <i class="fas fa-external-link-alt resource-icon"></i>
                            <span>Additional References</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Set CSS custom properties for course colors
        document.documentElement.style.setProperty('--course-color-light', 
            {% if course == 'Math' %}'#e74c3c'{% elif course == 'Science' %}'#2ecc71'{% elif course == 'History' %}'#f39c12'{% elif course == 'Coding' %}'#9b59b6'{% else %}'#3498db'{% endif %}
        );
        document.documentElement.style.setProperty('--course-color-dark', 
            {% if course == 'Math' %}'#c0392b'{% elif course == 'Science' %}'#27ae60'{% elif course == 'History' %}'#e67e22'{% elif course == 'Coding' %}'#8e44ad'{% else %}'#2980b9'{% endif %}
        );
        
        // Add click handlers for resources
        document.querySelectorAll('.resource-item').forEach(item => {
            item.addEventListener('click', function() {
                const resourceName = this.querySelector('span').textContent;
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 1000;
                `;
                toast.innerHTML = `<i class="fas fa-download"></i> Downloading: ${resourceName}`;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            });
        });
        
        // Animate topic items on load
        document.addEventListener('DOMContentLoaded', function() {
            const topics = document.querySelectorAll('.topic-item');
            topics.forEach((topic, index) => {
                topic.style.opacity = '0';
                topic.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    topic.style.transition = 'all 0.5s ease';
                    topic.style.opacity = '1';
                    topic.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
        '''
        default_syllabus = {
            'Math': ['Algebra','Geometry','Trigonometry','Calculus'],
            'Science': ['Physics Basics','Chemistry Fundamentals','Biology Overview','Lab Work'],
            'History': ['Ancient Civilizations','Medieval Era','Modern History','Contemporary Events'],
            'Coding': ['Intro to Programming','Control Structures','Data Structures','Projects']
        }
        return render_template_string(template, course=course_name, syllabus=default_syllabus, 
                                     topics=default_syllabus.get(course_name, ['Overview','Basics','Practice','Assessment']))
    return redirect(url_for('login'))

@app.route('/student_scores')
def student_scores_page():
    if 'role' in session and session['role'] == 'student':
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Scores - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .scores-overview {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 30px;
            margin-bottom: 30px;
        }
        .scores-table-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .table-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            font-size: 1.2rem;
            font-weight: 600;
        }
        .scores-table {
            width: 100%;
            border-collapse: collapse;
        }
        .scores-table th,
        .scores-table td {
            padding: 20px 25px;
            text-align: left;
            border-bottom: 1px solid #f1f3f4;
        }
        .scores-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        .scores-table tr:hover {
            background: #f8f9fb;
        }
        .score-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .score-excellent {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .score-good {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .score-average {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .chart-title {
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #scoresChart {
            max-height: 300px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .course-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            color: white;
            margin-right: 15px;
        }
        .course-name {
            display: flex;
            align-items: center;
            font-weight: 500;
        }
        @media (max-width: 768px) {
            .scores-overview {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .scores-table th,
            .scores-table td {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-chart-bar"></i>
                Your Academic Scores
            </h1>
            <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="color: #28a745;">
                    <i class="fas fa-trophy"></i>
                </div>
                <div class="stat-value" style="color: #28a745;">87.7</div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498db;">
                    <i class="fas fa-star"></i>
                </div>
                <div class="stat-value" style="color: #3498db;">90</div>
                <div class="stat-label">Highest Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #fd7e14;">
                    <i class="fas fa-books"></i>
                </div>
                <div class="stat-value" style="color: #fd7e14;">{{ scores|length }}</div>
                <div class="stat-label">Subjects</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #e83e8c;">
                    <i class="fas fa-medal"></i>
                </div>
                <div class="stat-value" style="color: #e83e8c;">A-</div>
                <div class="stat-label">Overall Grade</div>
            </div>
        </div>
        
        <div class="scores-overview">
            <div class="scores-table-container">
                <div class="table-header">
                    <i class="fas fa-list-alt"></i> Subject Scores
                </div>
                <table class="scores-table">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Score</th>
                            <th>Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for course, score in scores.items() %}
                        <tr>
                            <td>
                                <div class="course-name">
                                    <div class="course-icon" style="
                                        {% if course == 'Math' %}background: #e74c3c;{% endif %}
                                        {% if course == 'Science' %}background: #2ecc71;{% endif %}
                                        {% if course == 'History' %}background: #f39c12;{% endif %}
                                    ">
                                        {% if course == 'Math' %}<i class="fas fa-calculator"></i>{% endif %}
                                        {% if course == 'Science' %}<i class="fas fa-flask"></i>{% endif %}
                                        {% if course == 'History' %}<i class="fas fa-scroll"></i>{% endif %}
                                    </div>
                                    {{ course }}
                                </div>
                            </td>
                            <td>
                                <strong style="font-size: 1.1rem;">{{ score }}%</strong>
                            </td>
                            <td>
                                <span class="score-badge 
                                    {% if score >= 90 %}score-excellent{% elif score >= 80 %}score-good{% else %}score-average{% endif %}
                                ">
                                    {% if score >= 90 %}
                                        <i class="fas fa-star"></i> A
                                    {% elif score >= 80 %}
                                        <i class="fas fa-thumbs-up"></i> B
                                    {% else %}
                                        <i class="fas fa-check"></i> C
                                    {% endif %}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <h3 class="chart-title">
                    <i class="fas fa-chart-pie"></i>
                    Score Distribution
                </h3>
                <canvas id="scoresChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Scores Chart
        const ctx = document.getElementById('scoresChart').getContext('2d');
        const courses = {{ scores.keys()|list|tojson }};
        const scores = {{ scores.values()|list|tojson }};
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: courses,
                datasets: [{
                    data: scores,
                    backgroundColor: ['#e74c3c', '#2ecc71', '#f39c12'],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
        // Animate table rows
        document.addEventListener('DOMContentLoaded', function() {
            const rows = document.querySelectorAll('.scores-table tbody tr');
            rows.forEach((row, index) => {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    row.style.transition = 'all 0.5s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, index * 100);
            });
        });
    </script>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .progress-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .chart-title {
            font-size: 1.3rem;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .chart-container {
            position: relative;
            height: 300px;
        }
        .progress-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .attendance-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .section-title {
            font-size: 1.4rem;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-bottom: 20px;
        }
        .calendar-day {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .day-header {
            background: #f8f9fa;
            color: #5a6c7d;
            font-weight: 600;
        }
        .present {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }
        .absent {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }
        .attendance-summary {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .summary-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .summary-value {
            font-size: 1.5rem;
            font-weight: 700;
        }
        .summary-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .progress-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-chart-line"></i>
                Academic Progress
            </h1>
            <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="progress-stats">
            <div class="stat-card">
                <div class="stat-icon" style="color: #28a745;">
                    <i class="fas fa-percentage"></i>
                </div>
                <div class="stat-value" style="color: #28a745;">83%</div>
                <div class="stat-label">Attendance Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498db;">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-value" style="color: #3498db;">124h</div>
                <div class="stat-label">Study Hours</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #fd7e14;">
                    <i class="fas fa-tasks"></i>
                </div>
                <div class="stat-value" style="color: #fd7e14;">18/20</div>
                <div class="stat-label">Assignments</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #e83e8c;">
                    <i class="fas fa-star"></i>
                </div>
                <div class="stat-value" style="color: #e83e8c;">87%</div>
                <div class="stat-label">Average Score</div>
            </div>
        </div>
        
        <div class="progress-grid">
            <div class="chart-card">
                <h3 class="chart-title">
                    <i class="fas fa-chart-pie"></i>
                    Course Progress
                </h3>
                <div class="chart-container">
                    <canvas id="progressChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3 class="chart-title">
                    <i class="fas fa-chart-bar"></i>
                    Weekly Performance
                </h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="attendance-section">
            <h3 class="section-title">
                <i class="fas fa-calendar-check"></i>
                Attendance Record (Sept 1-18, 2025)
            </h3>
            
            <div class="calendar-grid">
                <div class="calendar-day day-header">Mon</div>
                <div class="calendar-day day-header">Tue</div>
                <div class="calendar-day day-header">Wed</div>
                <div class="calendar-day day-header">Thu</div>
                <div class="calendar-day day-header">Fri</div>
                <div class="calendar-day day-header">Sat</div>
                <div class="calendar-day day-header">Sun</div>
                
                {% for att in attendance %}
                <div class="calendar-day {% if att.status == 'Present' %}present{% else %}absent{% endif %}" 
                     title="{{ att.date }}: {{ att.status }}">
                    {{ att.date.split('-')[0] }}
                </div>
                {% endfor %}
            </div>
            
            <div class="attendance-summary">
                <div class="summary-item">
                    <div class="summary-value" style="color: #28a745;">15</div>
                    <div class="summary-label">Present Days</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value" style="color: #dc3545;">3</div>
                    <div class="summary-label">Absent Days</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value" style="color: #3498db;">83%</div>
                    <div class="summary-label">Attendance Rate</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Progress Chart
        const progressCtx = document.getElementById('progressChart').getContext('2d');
        const progressLabels = {{ progress.keys()|list|tojson }};
        const progressValues = {{ progress.values()|list|tojson }}.map(v => parseInt(String(v).replace('%','')));
        
        new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: progressLabels,
                datasets: [{
                    data: progressValues,
                    backgroundColor: ['#3498db', '#28a745', '#fd7e14', '#e83e8c'],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(performanceCtx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Current'],
                datasets: [{
                    label: 'Performance Score',
                    data: [78, 85, 82, 87],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: '#3498db',
                    borderWidth: 2,
                    borderRadius: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    </script>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificates - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .certificates-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .certificate-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
        }
        .certificate-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        .certificate-header {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
            padding: 25px;
            text-align: center;
            position: relative;
        }
        .certificate-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
            opacity: 0.3;
        }
        .certificate-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }
        .certificate-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
        }
        .certificate-date {
            opacity: 0.9;
            font-size: 0.9rem;
            position: relative;
            z-index: 1;
        }
        .certificate-body {
            padding: 25px;
        }
        .certificate-description {
            color: #5a6c7d;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        .certificate-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .detail-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #2c3e50;
            font-size: 0.9rem;
        }
        .detail-icon {
            color: #f39c12;
            width: 16px;
        }
        .certificate-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            flex: 1;
            justify-content: center;
        }
        .btn-primary {
            background: linear-gradient(45deg, #f39c12, #e67e22);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(243, 156, 18, 0.3);
        }
        .btn-outline {
            background: transparent;
            color: #f39c12;
            border: 2px solid #f39c12;
        }
        .btn-outline:hover {
            background: #f39c12;
            color: white;
        }
        .stats-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .stats-title {
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #f39c12;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .empty-icon {
            font-size: 4rem;
            color: #bdc3c7;
            margin-bottom: 20px;
        }
        .empty-title {
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .empty-message {
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        @media (max-width: 768px) {
            .certificates-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .certificate-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-certificate"></i>
                My Certificates
            </h1>
            <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="stats-section">
            <h2 class="stats-title">
                <i class="fas fa-chart-bar"></i>
                Certificate Overview
            </h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ certificates|length }}</div>
                    <div class="stat-label">Total Certificates</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2</div>
                    <div class="stat-label">This Month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">100%</div>
                    <div class="stat-label">Completion Rate</div>
                </div>
            </div>
        </div>
        
        {% if certificates %}
        <div class="certificates-grid">
            {% for cert in certificates %}
            <div class="certificate-card">
                <div class="certificate-header">
                    <div class="certificate-icon">
                        <i class="fas fa-medal"></i>
                    </div>
                    <div class="certificate-title">{{ cert }}</div>
                    <div class="certificate-date">Earned on September 15, 2025</div>
                </div>
                <div class="certificate-body">
                    <div class="certificate-description">
                        Congratulations! You have successfully completed the {{ cert.replace(' Certificate', '') }} course with excellent performance.
                    </div>
                    <div class="certificate-details">
                        <div class="detail-item">
                            <i class="fas fa-star detail-icon"></i>
                            <span>Grade: A</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-clock detail-icon"></i>
                            <span>Duration: 3 months</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-user-tie detail-icon"></i>
                            <span>Instructor: Prof. Smith</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-calendar detail-icon"></i>
                            <span>Valid: Lifetime</span>
                        </div>
                    </div>
                    <div class="certificate-actions">
                        <a href="#" class="btn btn-primary" onclick="downloadCertificate('{{ cert }}')">
                            <i class="fas fa-download"></i> Download PDF
                        </a>
                        <a href="#" class="btn btn-outline" onclick="shareCertificate('{{ cert }}')">
                            <i class="fas fa-share"></i> Share
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <div class="empty-icon">
                <i class="fas fa-certificate"></i>
            </div>
            <div class="empty-title">No Certificates Yet</div>
            <div class="empty-message">Complete courses to earn your first certificate!</div>
            <a href="{{ url_for('student_dashboard') }}" class="btn btn-primary">
                <i class="fas fa-book"></i> Browse Courses
            </a>
        </div>
        {% endif %}
    </div>
    
    <script>
        function downloadCertificate(certName) {
            // Simulate certificate download
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            `;
            toast.innerHTML = `<i class="fas fa-check"></i> ${certName} downloaded successfully!`;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
        
        function shareCertificate(certName) {
            if (navigator.share) {
                navigator.share({
                    title: certName,
                    text: `I just earned my ${certName} from Edvision360!`,
                    url: window.location.href
                });
            } else {
                // Fallback for browsers that don't support Web Share API
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #3498db;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 1000;
                `;
                toast.innerHTML = `<i class="fas fa-info"></i> Share link copied to clipboard!`;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }
        }
        
        // Animate cards on load
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.certificate-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Class Schedule - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .schedule-container {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
        }
        .today-schedule {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .today-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .today-date {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .today-day {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .today-classes {
            padding: 20px;
        }
        .class-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid #f1f3f4;
        }
        .class-item:last-child {
            border-bottom: none;
        }
        .class-time {
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            min-width: 80px;
            text-align: center;
        }
        .class-info {
            flex: 1;
        }
        .class-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 3px;
        }
        .class-room {
            color: #5a6c7d;
            font-size: 0.85rem;
        }
        .class-status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        .status-upcoming {
            background: #fff3cd;
            color: #856404;
        }
        .status-current {
            background: #d4edda;
            color: #155724;
        }
        .status-completed {
            background: #f8d7da;
            color: #721c24;
        }
        .weekly-schedule {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .schedule-header {
            padding: 25px 30px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: between;
            align-items: center;
        }
        .schedule-title {
            font-size: 1.3rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .schedule-table {
            width: 100%;
            border-collapse: collapse;
        }
        .schedule-table th,
        .schedule-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #f1f3f4;
        }
        .schedule-table th {
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        .time-slot {
            background: #f8f9fa;
            font-weight: 600;
            color: #5a6c7d;
            width: 120px;
        }
        .class-cell {
            background: #e3f2fd;
            border: 2px solid #bbdefb;
            border-radius: 8px;
            padding: 10px;
            margin: 2px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .class-cell:hover {
            background: #bbdefb;
            transform: scale(1.05);
        }
        .subject-math {
            background: #ffebee;
            border-color: #f8bbd9;
            color: #c2185b;
        }
        .subject-science {
            background: #e8f5e8;
            border-color: #a5d6a7;
            color: #388e3c;
        }
        .subject-history {
            background: #fff3e0;
            border-color: #ffcc02;
            color: #f57c00;
        }
        .subject-coding {
            background: #f3e5f5;
            border-color: #ce93d8;
            color: #7b1fa2;
        }
        .class-name-cell {
            font-weight: 600;
            font-size: 0.9rem;
        }
        .class-room-cell {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        .empty-cell {
            color: #bdc3c7;
            font-style: italic;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .schedule-container {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .schedule-table {
                font-size: 0.8rem;
            }
            .schedule-table th,
            .schedule-table td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-calendar-alt"></i>
                Class Schedule
            </h1>
            <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498db;">
                    <i class="fas fa-book"></i>
                </div>
                <div class="stat-value" style="color: #3498db;">20</div>
                <div class="stat-label">Classes This Week</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #28a745;">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-value" style="color: #28a745;">4</div>
                <div class="stat-label">Classes Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #fd7e14;">
                    <i class="fas fa-hourglass-half"></i>
                </div>
                <div class="stat-value" style="color: #fd7e14;">25h</div>
                <div class="stat-label">Total Hours</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #e83e8c;">
                    <i class="fas fa-user-tie"></i>
                </div>
                <div class="stat-value" style="color: #e83e8c;">6</div>
                <div class="stat-label">Instructors</div>
            </div>
        </div>
        
        <div class="schedule-container">
            <div class="today-schedule">
                <div class="today-header">
                    <div class="today-date">September 18</div>
                    <div class="today-day">Today's Classes</div>
                </div>
                <div class="today-classes">
                    <div class="class-item">
                        <div class="class-time">09:00</div>
                        <div class="class-info">
                            <div class="class-name">Mathematics</div>
                            <div class="class-room">Room A101</div>
                        </div>
                        <div class="class-status status-current">Current</div>
                    </div>
                    <div class="class-item">
                        <div class="class-time">10:15</div>
                        <div class="class-info">
                            <div class="class-name">Science</div>
                            <div class="class-room">Lab B202</div>
                        </div>
                        <div class="class-status status-upcoming">Upcoming</div>
                    </div>
                    <div class="class-item">
                        <div class="class-time">11:30</div>
                        <div class="class-info">
                            <div class="class-name">History</div>
                            <div class="class-room">Room C303</div>
                        </div>
                        <div class="class-status status-upcoming">Upcoming</div>
                    </div>
                    <div class="class-item">
                        <div class="class-time">14:00</div>
                        <div class="class-info">
                            <div class="class-name">Coding</div>
                            <div class="class-room">Computer Lab</div>
                        </div>
                        <div class="class-status status-upcoming">Upcoming</div>
                    </div>
                </div>
            </div>
            
            <div class="weekly-schedule">
                <div class="schedule-header">
                    <h2 class="schedule-title">
                        <i class="fas fa-calendar-week"></i>
                        Weekly Schedule
                    </h2>
                </div>
                <table class="schedule-table">
                    <thead>
                        <tr>
                            <th class="time-slot">Time</th>
                            <th>Monday</th>
                            <th>Tuesday</th>
                            <th>Wednesday</th>
                            <th>Thursday</th>
                            <th>Friday</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="time-slot">09:00 - 10:00</td>
                            <td>
                                <div class="class-cell subject-math">
                                    <div class="class-name-cell">Math</div>
                                    <div class="class-room-cell">A101</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-science">
                                    <div class="class-name-cell">Science</div>
                                    <div class="class-room-cell">B202</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-math">
                                    <div class="class-name-cell">Math</div>
                                    <div class="class-room-cell">A101</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-history">
                                    <div class="class-name-cell">History</div>
                                    <div class="class-room-cell">C303</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-coding">
                                    <div class="class-name-cell">Coding</div>
                                    <div class="class-room-cell">Lab 1</div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td class="time-slot">10:15 - 11:15</td>
                            <td>
                                <div class="class-cell subject-science">
                                    <div class="class-name-cell">Science</div>
                                    <div class="class-room-cell">B202</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-history">
                                    <div class="class-name-cell">History</div>
                                    <div class="class-room-cell">C303</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-science">
                                    <div class="class-name-cell">Science</div>
                                    <div class="class-room-cell">B202</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-math">
                                    <div class="class-name-cell">Math</div>
                                    <div class="class-room-cell">A101</div>
                                </div>
                            </td>
                            <td class="empty-cell">Free Period</td>
                        </tr>
                        <tr>
                            <td class="time-slot">11:30 - 12:30</td>
                            <td>
                                <div class="class-cell subject-history">
                                    <div class="class-name-cell">History</div>
                                    <div class="class-room-cell">C303</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-coding">
                                    <div class="class-name-cell">Coding</div>
                                    <div class="class-room-cell">Lab 1</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-history">
                                    <div class="class-name-cell">History</div>
                                    <div class="class-room-cell">C303</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-science">
                                    <div class="class-name-cell">Science</div>
                                    <div class="class-room-cell">B202</div>
                                </div>
                            </td>
                            <td>
                                <div class="class-cell subject-math">
                                    <div class="class-name-cell">Math</div>
                                    <div class="class-room-cell">A101</div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td class="time-slot">14:00 - 15:00</td>
                            <td>
                                <div class="class-cell subject-coding">
                                    <div class="class-name-cell">Coding</div>
                                    <div class="class-room-cell">Lab 1</div>
                                </div>
                            </td>
                            <td class="empty-cell">Free Period</td>
                            <td>
                                <div class="class-cell subject-coding">
                                    <div class="class-name-cell">Coding</div>
                                    <div class="class-room-cell">Lab 1</div>
                                </div>
                            </td>
                            <td class="empty-cell">Free Period</td>
                            <td>
                                <div class="class-cell subject-history">
                                    <div class="class-name-cell">History</div>
                                    <div class="class-room-cell">C303</div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Add click handlers for class cells
        document.querySelectorAll('.class-cell:not(.empty-cell)').forEach(cell => {
            cell.addEventListener('click', function() {
                const className = this.querySelector('.class-name-cell').textContent;
                const room = this.querySelector('.class-room-cell').textContent;
                
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #3498db;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                `;
                toast.innerHTML = `<i class="fas fa-info-circle"></i> ${className} class in room ${room}`;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            });
        });
        
        // Animate elements on load
        document.addEventListener('DOMContentLoaded', function() {
            const elements = document.querySelectorAll('.stat-card, .class-item');
            elements.forEach((element, index) => {
                element.style.opacity = '0';
                element.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    element.style.transition = 'all 0.5s ease';
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }, index * 50);
            });
        });
    </script>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discussions - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .discussions-layout {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
        }
        .sidebar {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
            height: fit-content;
        }
        .sidebar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .sidebar-title {
            font-size: 1.2rem;
            font-weight: 600;
        }
        .categories-list {
            padding: 20px;
        }
        .category-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #5a6c7d;
        }
        .category-item:hover,
        .category-item.active {
            background: #e3f2fd;
            color: #1976d2;
        }
        .category-icon {
            width: 20px;
            text-align: center;
        }
        .category-count {
            margin-left: auto;
            background: #f1f3f4;
            color: #5a6c7d;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        .main-content {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .content-header {
            padding: 25px 30px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .clear-all-btn {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .clear-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(231, 76, 60, 0.3);
        }
        .content-title {
            font-size: 1.3rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .new-discussion-btn {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .new-discussion-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(40, 167, 69, 0.3);
        }
        .discussions-list {
            padding: 0;
        }
        .discussion-item {
            padding: 20px 30px;
            border-bottom: 1px solid #f8f9fa;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .discussion-item:hover {
            background: #f8f9fa;
        }
        .discussion-item:last-child {
            border-bottom: none;
        }
        .discussion-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .discussion-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .discussion-meta {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.85rem;
            color: #7f8c8d;
        }
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .discussion-preview {
            color: #5a6c7d;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .discussion-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .stats-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .stats-title {
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .pinned-badge {
            background: #ffd700;
            color: #856404;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 10px;
        }
        .solved-badge {
            background: #d4edda;
            color: #155724;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 10px;
        }
        @media (max-width: 768px) {
            .discussions-layout {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .content-header {
                flex-direction: column;
                gap: 15px;
                align-items: stretch;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-comments"></i>
                Class Discussions
            </h1>
            <a href="{{ url_for('student_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="stats-section">
            <h2 class="stats-title">
                <i class="fas fa-chart-bar"></i>
                Discussion Overview
            </h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon" style="color: #3498db;">
                        <i class="fas fa-comments"></i>
                    </div>
                    <div class="stat-value" style="color: #3498db;">24</div>
                    <div class="stat-label">Total Discussions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: #28a745;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="stat-value" style="color: #28a745;">18</div>
                    <div class="stat-label">Solved Topics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: #fd7e14;">
                        <i class="fas fa-user-edit"></i>
                    </div>
                    <div class="stat-value" style="color: #fd7e14;">5</div>
                    <div class="stat-label">Your Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: #e83e8c;">
                        <i class="fas fa-thumbs-up"></i>
                    </div>
                    <div class="stat-value" style="color: #e83e8c;">42</div>
                    <div class="stat-label">Likes Received</div>
                </div>
            </div>
        </div>
        
        <div class="discussions-layout">
            <div class="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-title">Categories</div>
                </div>
                <div class="categories-list">
                    <div class="category-item active">
                        <i class="fas fa-home category-icon"></i>
                        <span>All Discussions</span>
                        <span class="category-count">24</span>
                    </div>
                    <div class="category-item">
                        <i class="fas fa-calculator category-icon"></i>
                        <span>Math Q&A</span>
                        <span class="category-count">8</span>
                    </div>
                    <div class="category-item">
                        <i class="fas fa-flask category-icon"></i>
                        <span>Science Forum</span>
                        <span class="category-count">6</span>
                    </div>
                    <div class="category-item">
                        <i class="fas fa-scroll category-icon"></i>
                        <span>History Hub</span>
                        <span class="category-count">4</span>
                    </div>
                    <div class="category-item">
                        <i class="fas fa-code category-icon"></i>
                        <span>Coding Corner</span>
                        <span class="category-count">6</span>
                    </div>
                    <div class="category-item">
                        <i class="fas fa-question-circle category-icon"></i>
                        <span>General Help</span>
                        <span class="category-count">3</span>
                    </div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="content-header">
                    <h2 class="content-title">
                        <i class="fas fa-list"></i>
                        Recent Discussions
                    </h2>
                    <button class="new-discussion-btn" onclick="showNewDiscussionForm()">
                        <i class="fas fa-plus"></i> New Discussion
                    </button>
                </div>
                
                <div class="discussions-list">
                    <div class="discussion-item">
                        <div class="discussion-header">
                            <div>
                                <div class="discussion-title">
                                    Need help with Calculus derivatives
                                    <span class="pinned-badge">PINNED</span>
                                </div>
                                <div class="discussion-meta">
                                    <div class="meta-item">
                                        <i class="fas fa-user"></i>
                                        <span>Sarah Chen</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-clock"></i>
                                        <span>2 hours ago</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-comments"></i>
                                        <span>12 replies</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-eye"></i>
                                        <span>45 views</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="discussion-preview">
                            I'm struggling with understanding the chain rule for derivatives. Can someone explain it with simple examples?
                        </div>
                        <div class="discussion-tags">
                            <span class="tag">Math</span>
                            <span class="tag">Calculus</span>
                            <span class="tag">Help</span>
                        </div>
                    </div>
                    
                    <div class="discussion-item">
                        <div class="discussion-header">
                            <div>
                                <div class="discussion-title">
                                    Chemistry lab experiment results
                                    <span class="solved-badge">SOLVED</span>
                                </div>
                                <div class="discussion-meta">
                                    <div class="meta-item">
                                        <i class="fas fa-user"></i>
                                        <span>Mike Johnson</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-clock"></i>
                                        <span>5 hours ago</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-comments"></i>
                                        <span>8 replies</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-eye"></i>
                                        <span>28 views</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="discussion-preview">
                            Sharing my results from the acid-base titration experiment. Got some interesting observations to discuss.
                        </div>
                        <div class="discussion-tags">
                            <span class="tag">Science</span>
                            <span class="tag">Chemistry</span>
                            <span class="tag">Lab</span>
                        </div>
                    </div>
                    
                    <div class="discussion-item">
                        <div class="discussion-header">
                            <div>
                                <div class="discussion-title">
                                    World War II timeline discussion
                                </div>
                                <div class="discussion-meta">
                                    <div class="meta-item">
                                        <i class="fas fa-user"></i>
                                        <span>Emma Davis</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-clock"></i>
                                        <span>1 day ago</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-comments"></i>
                                        <span>15 replies</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-eye"></i>
                                        <span>67 views</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="discussion-preview">
                            Let's discuss the major events and turning points of WWII. What do you think was the most decisive moment?
                        </div>
                        <div class="discussion-tags">
                            <span class="tag">History</span>
                            <span class="tag">WWII</span>
                            <span class="tag">Discussion</span>
                        </div>
                    </div>
                    
                    <div class="discussion-item">
                        <div class="discussion-header">
                            <div>
                                <div class="discussion-title">
                                    Python debugging tips and tricks
                                </div>
                                <div class="discussion-meta">
                                    <div class="meta-item">
                                        <i class="fas fa-user"></i>
                                        <span>Alex Kumar</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-clock"></i>
                                        <span>2 days ago</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-comments"></i>
                                        <span>22 replies</span>
                                    </div>
                                    <div class="meta-item">
                                        <i class="fas fa-eye"></i>
                                        <span>89 views</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="discussion-preview">
                            Share your favorite Python debugging techniques! I'll start with using print statements effectively.
                        </div>
                        <div class="discussion-tags">
                            <span class="tag">Coding</span>
                            <span class="tag">Python</span>
                            <span class="tag">Tips</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showNewDiscussionForm() {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            `;
            toast.innerHTML = `<i class="fas fa-info-circle"></i> New discussion form would open here!`;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
        
        // Add click handlers for category items
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', function() {
                document.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                
                const categoryName = this.querySelector('span').textContent;
                document.querySelector('.content-title span').textContent = categoryName;
            });
        });
        
        // Add click handlers for discussion items
        document.querySelectorAll('.discussion-item').forEach(item => {
            item.addEventListener('click', function() {
                const title = this.querySelector('.discussion-title').textContent.trim();
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #3498db;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 1000;
                `;
                toast.innerHTML = `<i class="fas fa-eye"></i> Opening: ${title}`;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            });
        });
        
        // Animate elements on load
        document.addEventListener('DOMContentLoaded', function() {
            const items = document.querySelectorAll('.discussion-item, .category-item');
            items.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    item.style.transition = 'all 0.5s ease';
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, index * 50);
            });
        });
    </script>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        .profile-grid {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 30px;
        }
        .profile-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
            height: fit-content;
        }
        .profile-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin: 0 auto 20px;
            border: 4px solid rgba(255,255,255,0.3);
        }
        .profile-name {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .profile-role {
            opacity: 0.9;
            font-size: 1rem;
            text-transform: capitalize;
        }
        .profile-body {
            padding: 30px;
        }
        .info-group {
            margin-bottom: 25px;
        }
        .info-label {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #5a6c7d;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .info-value {
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 500;
        }
        .details-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .card-header {
            padding: 25px 30px;
            border-bottom: 1px solid #f1f3f4;
        }
        .card-title {
            font-size: 1.3rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card-body {
            padding: 30px;
        }
        .courses-list {
            display: grid;
            gap: 15px;
        }
        .course-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        .course-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.1rem;
        }
        .course-info {
            flex: 1;
        }
        .course-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 2px;
        }
        .course-score {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            opacity: 0.5;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .profile-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-user-circle"></i>
                My Profile
            </h1>
            <a href="{% if role == 'student' %}{{ url_for('student_dashboard') }}{% elif role == 'teacher' %}{{ url_for('teacher_dashboard') }}{% else %}{{ url_for('admin_dashboard') }}{% endif %}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="profile-grid">
            <div class="profile-card">
                <div class="profile-header">
                    <div class="avatar">
                        <i class="fas {% if role == 'student' %}fa-user-graduate{% elif role == 'teacher' %}fa-chalkboard-teacher{% else %}fa-user-shield{% endif %}"></i>
                    </div>
                    <div class="profile-name">{{ username }}</div>
                    <div class="profile-role">{{ role }}</div>
                </div>
                <div class="profile-body">
                    <div class="info-group">
                        <div class="info-label">
                            <i class="fas fa-user"></i> Username
                        </div>
                        <div class="info-value">{{ username }}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">
                            <i class="fas fa-shield-alt"></i> Role
                        </div>
                        <div class="info-value" style="text-transform: capitalize;">{{ role }}</div>
                    </div>
                    {% if role == 'student' %}
                    {% set info = students_info.get(username) %}
                    {% if info and info.name %}
                    <div class="info-group">
                        <div class="info-label">
                            <i class="fas fa-id-card"></i> Full Name
                        </div>
                        <div class="info-value">{{ info.name }}</div>
                    </div>
                    {% endif %}
                    {% if info and info.email %}
                    <div class="info-group">
                        <div class="info-label">
                            <i class="fas fa-envelope"></i> Email
                        </div>
                        <div class="info-value">{{ info.email }}</div>
                    </div>
                    {% endif %}
                    {% if info and info.address %}
                    <div class="info-group">
                        <div class="info-label">
                            <i class="fas fa-map-marker-alt"></i> Address
                        </div>
                        <div class="info-value">{{ info.address }}</div>
                    </div>
                    {% endif %}
                    {% endif %}
                </div>
            </div>
            
            <div class="details-card">
                {% if role == 'student' %}
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-graduation-cap"></i>
                        Academic Information
                    </h2>
                </div>
                <div class="card-body">
                    {% set info = students_info.get(username) %}
                    {% if info and info.courses %}
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{{ info.courses|length }}</div>
                            <div class="stat-label">Enrolled Courses</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">
                                {% if info.marks %}
                                    {{ "%.1f"|format(info.marks.values()|sum / info.marks.values()|length) }}
                                {% else %}
                                    0
                                {% endif %}
                            </div>
                            <div class="stat-label">Average Score</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">83%</div>
                            <div class="stat-label">Attendance</div>
                        </div>
                    </div>
                    
                    <h3 style="margin-bottom: 20px; color: #2c3e50; display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-book"></i> Enrolled Courses
                    </h3>
                    <div class="courses-list">
                        {% for course in info.courses %}
                        <div class="course-item">
                            <div class="course-icon" style="
                                {% if course == 'Math' %}background: #e74c3c;{% endif %}
                                {% if course == 'Science' %}background: #2ecc71;{% endif %}
                                {% if course == 'History' %}background: #f39c12;{% endif %}
                                {% if course == 'Coding' %}background: #9b59b6;{% endif %}
                            ">
                                {% if course == 'Math' %}<i class="fas fa-calculator"></i>{% endif %}
                                {% if course == 'Science' %}<i class="fas fa-flask"></i>{% endif %}
                                {% if course == 'History' %}<i class="fas fa-scroll"></i>{% endif %}
                                {% if course == 'Coding' %}<i class="fas fa-code"></i>{% endif %}
                            </div>
                            <div class="course-info">
                                <div class="course-name">{{ course }}</div>
                                <div class="course-score">
                                    {% if info.marks and course in info.marks %}
                                        Current Score: {{ info.marks[course] }}%
                                    {% else %}
                                        No grades yet
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-book-open"></i>
                        </div>
                        <p>No course information available</p>
                    </div>
                    {% endif %}
                </div>
                {% else %}
                <div class="card-header">
                    <h2 class="card-title">
                        <i class="fas fa-info-circle"></i>
                        Account Information
                    </h2>
                </div>
                <div class="card-body">
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <p>{{ role|title }} account details</p>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teacher Dashboard - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .dashboard { display: flex; min-height: 100vh; }
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #2c3e50 0%, #c0392b 100%);
            color: white;
            padding: 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0,0,0,0.1);
        }
        .sidebar-header {
            padding: 25px 20px;
            background: rgba(0,0,0,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .sidebar-header h2 {
            font-size: 1.4rem;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .sidebar-header p {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        .nav-menu {
            padding: 20px 0;
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 25px;
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(255,255,255,0.1);
            border-left-color: #ffd700;
            color: white;
        }
        .nav-item i {
            width: 20px;
            text-align: center;
            font-size: 1.1rem;
        }
        .main-content {
            flex: 1;
            margin-left: 280px;
            background: #f5f7fa;
        }
        .top-bar {
            background: white;
            padding: 20px 30px;
            border-bottom: 1px solid #e1e8ed;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .welcome-text {
            font-size: 1.5rem;
            color: #2c3e50;
            font-weight: 600;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
            color: #5a6c7d;
        }
        .content-area {
            padding: 30px;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #c0392b;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .stat-title {
            color: #5a6c7d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-icon {
            font-size: 1.5rem;
            color: #c0392b;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
        }
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }
        .action-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .action-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        .action-header {
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .action-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        .action-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .action-subtitle {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .action-body {
            padding: 25px;
        }
        .action-description {
            color: #5a6c7d;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            width: 100%;
            justify-content: center;
        }
        .btn-primary {
            background: linear-gradient(45deg, #c0392b, #e74c3c);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(192, 57, 43, 0.3);
        }
        .recent-activity {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-top: 30px;
        }
        .activity-header {
            padding: 25px 30px;
            border-bottom: 1px solid #f1f3f4;
        }
        .activity-title {
            font-size: 1.3rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .activity-body {
            padding: 20px 30px;
        }
        .activity-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid #f8f9fa;
        }
        .activity-item:last-child {
            border-bottom: none;
        }
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #c0392b;
        }
        .activity-content {
            flex: 1;
        }
        .activity-text {
            color: #2c3e50;
            font-weight: 500;
            margin-bottom: 2px;
        }
        .activity-time {
            color: #7f8c8d;
            font-size: 0.85rem;
        }
        @media (max-width: 768px) {
            .sidebar { transform: translateX(-100%); }
            .main-content { margin-left: 0; }
            .top-bar { padding: 15px 20px; }
            .content-area { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2><i class="fas fa-chalkboard-teacher"></i> Edvision360</h2>
                <p>Teacher Portal</p>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('teacher_dashboard') }}" class="nav-item active">
                    <i class="fas fa-home"></i> Dashboard
                </a>
                <a href="{{ url_for('update_attendance') }}" class="nav-item">
                    <i class="fas fa-calendar-check"></i> Attendance
                </a>
                <a href="{{ url_for('teacher_student_scores') }}" class="nav-item">
                    <i class="fas fa-chart-bar"></i> Student Scores
                </a>
                <a href="{{ url_for('student_details') }}" class="nav-item">
                    <i class="fas fa-users"></i> Student Details
                </a>
                <a href="{{ url_for('profile_page') }}" class="nav-item">
                    <i class="fas fa-user"></i> Profile
                </a>
                <a href="{{ url_for('logout') }}" class="nav-item">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </nav>
        
        <main class="main-content">
            <div class="top-bar">
                <div class="welcome-text">
                    <i class="fas fa-apple-alt" style="color: #e74c3c; margin-right: 10px;"></i>
                    Welcome back, {{ username or 'Teacher' }}!
                </div>
                <div class="user-info">
                    <i class="fas fa-user-circle" style="font-size: 1.5rem;"></i>
                    <span>{{ username or 'Teacher' }}</span>
                </div>
            </div>
            
            <div class="content-area">
                <h1 class="page-title">
                    <i class="fas fa-tachometer-alt"></i>
                    Teacher Dashboard
                </h1>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-title">Total Students</div>
                            <div class="stat-icon">
                                <i class="fas fa-user-graduate"></i>
                            </div>
                        </div>
                        <div class="stat-value">{{ students_info|length or 24 }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-title">Classes Today</div>
                            <div class="stat-icon">
                                <i class="fas fa-calendar-day"></i>
                            </div>
                        </div>
                        <div class="stat-value">4</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-title">Pending Grades</div>
                            <div class="stat-icon">
                                <i class="fas fa-clipboard-list"></i>
                            </div>
                        </div>
                        <div class="stat-value">12</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <div class="stat-title">Average Score</div>
                            <div class="stat-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                        </div>
                        <div class="stat-value">85%</div>
                    </div>
                </div>
                
                <div class="actions-grid">
                    <div class="action-card">
                        <div class="action-header">
                            <div class="action-icon">
                                <i class="fas fa-calendar-check"></i>
                            </div>
                            <div class="action-title">Update Attendance</div>
                            <div class="action-subtitle">Mark student attendance</div>
                        </div>
                        <div class="action-body">
                            <div class="action-description">
                                Record and manage daily attendance for your classes. Keep track of student participation and engagement.
                            </div>
                            <a href="{{ url_for('update_attendance') }}" class="btn btn-primary">
                                <i class="fas fa-edit"></i> Mark Attendance
                            </a>
                        </div>
                    </div>
                    
                    <div class="action-card">
                        <div class="action-header">
                            <div class="action-icon">
                                <i class="fas fa-chart-bar"></i>
                            </div>
                            <div class="action-title">Grade Students</div>
                            <div class="action-subtitle">Review and update scores</div>
                        </div>
                        <div class="action-body">
                            <div class="action-description">
                                Grade assignments, tests, and projects. Provide feedback and track student academic progress.
                            </div>
                            <a href="{{ url_for('teacher_student_scores') }}" class="btn btn-primary">
                                <i class="fas fa-star"></i> Grade Students
                            </a>
                        </div>
                    </div>
                    
                    <div class="action-card">
                        <div class="action-header">
                            <div class="action-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="action-title">Student Details</div>
                            <div class="action-subtitle">View student information</div>
                        </div>
                        <div class="action-body">
                            <div class="action-description">
                                Access comprehensive student profiles, contact information, and academic history.
                            </div>
                            <a href="{{ url_for('student_details') }}" class="btn btn-primary">
                                <i class="fas fa-eye"></i> View Details
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="recent-activity">
                    <div class="activity-header">
                        <h2 class="activity-title">
                            <i class="fas fa-clock"></i> Recent Activity
                        </h2>
                    </div>
                    <div class="activity-body">
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-user-plus"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-text">New student enrolled in Math class</div>
                                <div class="activity-time">2 hours ago</div>
                            </div>
                        </div>
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-clipboard-check"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-text">Graded 15 assignments for Science class</div>
                                <div class="activity-time">1 day ago</div>
                            </div>
                        </div>
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i class="fas fa-calendar"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-text">Updated attendance for History class</div>
                                <div class="activity-time">2 days ago</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
        '''
        return render_template_string(template, username=session.get('username'), students_info=students_info)
    return redirect(url_for('login'))

@app.route('/update_attendance', methods=['GET', 'POST'])
def update_attendance():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update attendance records
        for key, value in request.form.items():
            if key.startswith('attendance_'):
                _, student, date = key.split('_', 2)
                if student in attendance_records:
                    attendance_records[student][date] = value
        return redirect(url_for('update_attendance'))
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Attendance - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: linear-gradient(45deg, #c0392b, #e74c3c);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(192, 57, 43, 0.3);
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .control-label {
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.9rem;
        }
        .control-input {
            padding: 10px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        .control-input:focus {
            outline: none;
            border-color: #c0392b;
            box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.1);
        }
        .save-btn {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        .save-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(39, 174, 96, 0.3);
        }
        .attendance-table {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .table-header {
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .table-title {
            font-size: 1.3rem;
            font-weight: 600;
        }
        .attendance-grid {
            overflow-x: auto;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #f1f3f4;
        }
        th {
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        .student-name {
            font-weight: 600;
            color: #2c3e50;
        }
        .date-header {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            width: 60px;
            text-align: center;
            font-size: 0.8rem;
        }
        .attendance-cell {
            text-align: center;
            padding: 8px;
        }
        .attendance-select {
            border: none;
            background: transparent;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 6px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .attendance-select.present {
            background: #d4edda;
            color: #155724;
        }
        .attendance-select.absent {
            background: #f8d7da;
            color: #721c24;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            .control-group {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-calendar-check"></i>
                Update Attendance
            </h1>
            <a href="{{ url_for('teacher_dashboard') }}" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498db;">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-value" style="color: #3498db;">{{ attendance_records|length }}</div>
                <div class="stat-label">Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #27ae60;">
                    <i class="fas fa-calendar-day"></i>
                </div>
                <div class="stat-value" style="color: #27ae60;">18</div>
                <div class="stat-label">Days Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #f39c12;">
                    <i class="fas fa-percentage"></i>
                </div>
                <div class="stat-value" style="color: #f39c12;">85%</div>
                <div class="stat-label">Average Attendance</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #e74c3c;">
                    <i class="fas fa-user-times"></i>
                </div>
                <div class="stat-value" style="color: #e74c3c;">12</div>
                <div class="stat-label">Total Absences</div>
            </div>
        </div>
        
        <form method="post">
            <div class="controls">
                <div class="control-group">
                    <label class="control-label">Date Range</label>
                    <input type="date" class="control-input" value="2025-09-01">
                </div>
                <div class="control-group">
                    <label class="control-label">To</label>
                    <input type="date" class="control-input" value="2025-09-18">
                </div>
                <div class="control-group">
                    <label class="control-label">Subject</label>
                    <select class="control-input">
                        <option>All Subjects</option>
                        <option>Math</option>
                        <option>Science</option>
                        <option>History</option>
                    </select>
                </div>
                <button type="submit" class="save-btn">
                    <i class="fas fa-save"></i> Save Changes
                </button>
            </div>
            
            <div class="attendance-table">
                <div class="table-header">
                    <div class="table-title">
                        <i class="fas fa-table"></i> Attendance Records (September 1-18, 2025)
                    </div>
                </div>
                <div class="attendance-grid">
                    <table>
                        <thead>
                            <tr>
                                <th>Student</th>
                                {% for day in range(1, 19) %}
                                <th class="date-header">Sep {{ "%02d"|format(day) }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for student, records in attendance_records.items() %}
                            <tr>
                                <td class="student-name">
                                    <i class="fas fa-user-graduate"></i> {{ student }}
                                </td>
                                {% for day in range(1, 19) %}
                                {% set date_key = "2025-09-" + "%02d"|format(day) %}
                                <td class="attendance-cell">
                                    <select name="attendance_{{ student }}_{{ date_key }}" 
                                            class="attendance-select {{ 'present' if records.get(date_key) == 'Present' else 'absent' }}" 
                                            onchange="updateAttendanceColor(this)">
                                        <option value="Present" {{ 'selected' if records.get(date_key) == 'Present' else '' }}>P</option>
                                        <option value="Absent" {{ 'selected' if records.get(date_key) == 'Absent' else '' }}>A</option>
                                    </select>
                                </td>
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </form>
    </div>
    
    <script>
        function updateAttendanceColor(select) {
            select.className = 'attendance-select ' + (select.value === 'Present' ? 'present' : 'absent');
        }
        
        // Initialize colors on page load
        document.addEventListener('DOMContentLoaded', function() {
            const selects = document.querySelectorAll('.attendance-select');
            selects.forEach(select => {
                updateAttendanceColor(select);
            });
            
            // Add animation to table rows
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach((row, index) => {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    row.style.transition = 'all 0.5s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, index * 100);
            });
        });
        
        // Add confirmation for form submission
        document.querySelector('form').addEventListener('submit', function(e) {
            const changes = document.querySelectorAll('.attendance-select:focus');
            if (changes.length > 0) {
                if (!confirm('Save attendance changes?')) {
                    e.preventDefault();
                }
            }
        });
    </script>
</body>
</html>
    '''
    return render_template_string(template, attendance_records=attendance_records)

@app.route('/teacher_student_scores', methods=['GET', 'POST'])
def teacher_student_scores():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
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
    
    # Populate students_info with enrollment data if empty
    for student, courses in student_enrollments.items():
        if student not in students_info:
            students_info[student] = {
                'name': student,
                'email': f'{student.lower()}@student.edu',
                'courses': courses,
                'marks': {course: 75 + (hash(student + course) % 26) for course in courses}
            }
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Scores - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary {
            background: linear-gradient(45deg, #c0392b, #e74c3c);
            color: white;
        }
        .btn-secondary {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .scores-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .table-header {
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
            color: white;
            padding: 20px;
        }
        .table-title {
            font-size: 1.3rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .table-content {
            padding: 20px;
        }
        .student-grid {
            display: grid;
            gap: 20px;
        }
        .student-card {
            border: 2px solid #f1f3f4;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .student-card:hover {
            border-color: #c0392b;
            box-shadow: 0 6px 20px rgba(192, 57, 43, 0.1);
        }
        .student-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .student-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(45deg, #c0392b, #e74c3c);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: 600;
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 3px;
        }
        .student-email {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .student-courses {
            padding: 20px;
        }
        .courses-title {
            font-size: 1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .course-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f8f9fa;
        }
        .course-item:last-child {
            border-bottom: none;
        }
        .course-name {
            font-weight: 500;
            color: #2c3e50;
        }
        .score-input {
            width: 80px;
            padding: 6px 10px;
            border: 2px solid #e1e8ed;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .score-input:focus {
            outline: none;
            border-color: #c0392b;
            box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.1);
        }
        .no-courses {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 20px;
        }
        .save-section {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #f1f3f4;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .header-actions {
                width: 100%;
                justify-content: stretch;
            }
            .btn {
                flex: 1;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-chart-bar"></i>
                Student Scores Management
            </h1>
            <div class="header-actions">
                <a href="{{ url_for('student_details') }}" class="btn btn-secondary">
                    <i class="fas fa-users"></i> Student Details
                </a>
                <a href="{{ url_for('teacher_dashboard') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="color: #3498db;">
                    <i class="fas fa-user-graduate"></i>
                </div>
                <div class="stat-value" style="color: #3498db;">{{ students_info|length }}</div>
                <div class="stat-label">Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #27ae60;">
                    <i class="fas fa-book"></i>
                </div>
                <div class="stat-value" style="color: #27ae60;">{% set total_courses = students_info.values()|map(attribute='courses')|map('length')|sum %}{{ total_courses or 0 }}</div>
                <div class="stat-label">Course Enrollments</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #f39c12;">
                    <i class="fas fa-star"></i>
                </div>
                <div class="stat-value" style="color: #f39c12;">
                    {% set all_marks = [] %}
                    {% for student in students_info.values() %}
                        {% if student.marks %}
                            {% for mark in student.marks.values() %}
                                {{ all_marks.append(mark) or '' }}
                            {% endfor %}
                        {% endif %}
                    {% endfor %}
                    {{ "%.1f"|format(all_marks|sum / all_marks|length) if all_marks else "0" }}
                </div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="color: #e74c3c;">
                    <i class="fas fa-clipboard-check"></i>
                </div>
                <div class="stat-value" style="color: #e74c3c;">{{ all_marks|length if all_marks else 0 }}</div>
                <div class="stat-label">Total Grades</div>
            </div>
        </div>
        
        <form method="post">
            <div class="scores-container">
                <div class="table-header">
                    <div class="table-title">
                        <i class="fas fa-edit"></i> Grade Students
                    </div>
                </div>
                <div class="table-content">
                    {% if students_info %}
                    <div class="student-grid">
                        {% for student, info in students_info.items() %}
                        <div class="student-card">
                            <div class="student-header">
                                <div class="student-avatar">
                                    {{ student[0].upper() }}
                                </div>
                                <div class="student-info">
                                    <div class="student-name">{{ info.name or student }}</div>
                                    <div class="student-email">{{ info.email or (student.lower() + '@student.edu') }}</div>
                                </div>
                            </div>
                            <div class="student-courses">
                                {% if info.courses %}
                                <div class="courses-title">
                                    <i class="fas fa-book-open"></i> Enrolled Courses
                                </div>
                                {% for course in info.courses %}
                                <div class="course-item">
                                    <span class="course-name">{{ course }}</span>
                                    <input type="number" 
                                           name="mark__{{ student }}__{{ course }}" 
                                           class="score-input" 
                                           min="0" 
                                           max="100" 
                                           value="{{ info.marks.get(course, 0) }}"
                                           placeholder="0">
                                </div>
                                {% endfor %}
                                {% else %}
                                <div class="no-courses">
                                    <i class="fas fa-info-circle"></i> No courses enrolled
                                </div>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div style="text-align: center; padding: 60px 20px; color: #7f8c8d;">
                        <i class="fas fa-user-graduate" style="font-size: 3rem; margin-bottom: 20px; display: block;"></i>
                        <h3>No students found</h3>
                        <p>No students are currently enrolled in your courses.</p>
                    </div>
                    {% endif %}
                </div>
                {% if students_info %}
                <div class="save-section">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Save All Grades
                    </button>
                </div>
                {% endif %}
            </div>
        </form>
    </div>
    
    <script>
        // Add animation to student cards
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.student-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
        
        // Validate score inputs
        document.querySelectorAll('.score-input').forEach(input => {
            input.addEventListener('blur', function() {
                const value = parseInt(this.value);
                if (value < 0) this.value = 0;
                if (value > 100) this.value = 100;
            });
        });
        
        // Add confirmation for form submission
        document.querySelector('form').addEventListener('submit', function(e) {
            if (!confirm('Save all grade changes?')) {
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
    '''
    return render_template_string(template, students_info=students_info)

@app.route('/student_details')
def student_details():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Populate students_info with enrollment data if empty
    for i, (student, courses) in enumerate(student_enrollments.items()):
        if student not in students_info:
            students_info[student] = {
                'name': student,
                'email': f'{student.lower()}@student.edu',
                'phone': f'+1-555-{1000 + (i * 111) % 9000}',
                'address': f'{(i * 123) % 999 + 1} Education St, Learning City',
                'courses': courses,
                'marks': {course: 75 + ((i + len(course)) % 26) for course in courses},
                'parent_name': f'{student} Parent',
                'parent_phone': f'+1-555-{2000 + (i * 222) % 9000}',
                'parent_email': f'{student.lower()}.parent@email.com'
            }
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Details - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary {
            background: linear-gradient(45deg, #c0392b, #e74c3c);
            color: white;
        }
        .btn-secondary {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .search-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .search-bar {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .search-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .search-input:focus {
            outline: none;
            border-color: #c0392b;
            box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.1);
        }
        .filter-select {
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            cursor: pointer;
        }
        .students-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }
        .student-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .student-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        .student-header {
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
            color: white;
            padding: 25px;
            text-align: center;
            position: relative;
        }
        .student-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 auto 15px;
            border: 4px solid rgba(255, 255, 255, 0.3);
        }
        .student-name {
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .student-id {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        .student-body {
            padding: 25px;
        }
        .info-section {
            margin-bottom: 25px;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .info-grid {
            display: grid;
            gap: 12px;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f8f9fa;
        }
        .info-item:last-child {
            border-bottom: none;
        }
        .info-label {
            color: #5a6c7d;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .info-value {
            color: #2c3e50;
            font-weight: 500;
            text-align: right;
        }
        .courses-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .course-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .grades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
        }
        .grade-item {
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .grade-subject {
            font-size: 0.8rem;
            color: #5a6c7d;
            margin-bottom: 5px;
        }
        .grade-score {
            font-size: 1.2rem;
            font-weight: 700;
            color: #2c3e50;
        }
        .attendance-indicator {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .attendance-good {
            background: #d4edda;
            color: #155724;
        }
        .attendance-warning {
            background: #fff3cd;
            color: #856404;
        }
        .attendance-danger {
            background: #f8d7da;
            color: #721c24;
        }
        .contact-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .contact-btn {
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
        }
        .email-btn {
            background: #3498db;
            color: white;
        }
        .phone-btn {
            background: #27ae60;
            color: white;
        }
        .contact-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .stats-summary {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            text-align: center;
        }
        .summary-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .summary-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #c0392b;
        }
        .summary-label {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .students-grid {
                grid-template-columns: 1fr;
            }
            .search-bar {
                flex-direction: column;
            }
            .search-input, .filter-select {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-users"></i>
                Student Details
            </h1>
            <div class="header-actions">
                <a href="{{ url_for('teacher_student_scores') }}" class="btn btn-secondary">
                    <i class="fas fa-chart-bar"></i> Manage Scores
                </a>
                <a href="{{ url_for('teacher_dashboard') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
        
        <div class="stats-summary">
            <div class="summary-item">
                <div class="summary-value">{{ students_info|length }}</div>
                <div class="summary-label">Total Students</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">
                    {% set total_enrollments = students_info.values()|map(attribute='courses')|map('length')|sum %}
                    {{ total_enrollments or 0 }}
                </div>
                <div class="summary-label">Course Enrollments</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">85%</div>
                <div class="summary-label">Avg Attendance</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">
                    {% set all_marks = [] %}
                    {% for student in students_info.values() %}
                        {% if student.marks %}
                            {% for mark in student.marks.values() %}
                                {{ all_marks.append(mark) or '' }}
                            {% endfor %}
                        {% endif %}
                    {% endfor %}
                    {{ "%.1f"|format(all_marks|sum / all_marks|length) if all_marks else "0" }}
                </div>
                <div class="summary-label">Avg Score</div>
            </div>
        </div>
        
        <div class="search-section">
            <div class="search-bar">
                <input type="text" class="search-input" placeholder="Search students by name, email, or course..." id="searchInput">
                <select class="filter-select" id="courseFilter">
                    <option value="">All Courses</option>
                    <option value="Math">Math</option>
                    <option value="Science">Science</option>
                    <option value="History">History</option>
                </select>
            </div>
        </div>
        
        <div class="students-grid" id="studentsGrid">
            {% for student, info in students_info.items() %}
            <div class="student-card" data-student="{{ student }}" data-courses="{{ info.courses|join(',') }}">
                <div class="student-header">
                    <div class="student-avatar">
                        {{ student[0].upper() }}
                    </div>
                    <div class="student-name">{{ info.name or student }}</div>
                    <div class="student-id">ID: STU{{ loop.index0 + 1000 }}</div>
                </div>
                <div class="student-body">
                    <div class="info-section">
                        <div class="section-title">
                            <i class="fas fa-id-card"></i> Contact Information
                        </div>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-envelope"></i> Email
                                </div>
                                <div class="info-value">{{ info.email or (student.lower() + '@student.edu') }}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-phone"></i> Phone
                                </div>
                                <div class="info-value">{{ info.phone or '+1-555-0000' }}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-map-marker-alt"></i> Address
                                </div>
                                <div class="info-value">{{ info.address or 'N/A' }}</div>
                            </div>
                        </div>
                    </div>
                    
                    {% if info.parent_name %}
                    <div class="info-section">
                        <div class="section-title">
                            <i class="fas fa-users"></i> Parent Contact
                        </div>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-user"></i> Name
                                </div>
                                <div class="info-value">{{ info.parent_name }}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-phone"></i> Phone
                                </div>
                                <div class="info-value">{{ info.parent_phone }}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">
                                    <i class="fas fa-envelope"></i> Email
                                </div>
                                <div class="info-value">{{ info.parent_email }}</div>
                            </div>
                        </div>
                        <div class="contact-actions">
                            <a href="mailto:{{ info.parent_email }}" class="contact-btn email-btn">
                                <i class="fas fa-envelope"></i> Email Parent
                            </a>
                            <a href="tel:{{ info.parent_phone }}" class="contact-btn phone-btn">
                                <i class="fas fa-phone"></i> Call Parent
                            </a>
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="info-section">
                        <div class="section-title">
                            <i class="fas fa-book"></i> Enrolled Courses
                        </div>
                        {% if info.courses %}
                        <div class="courses-list">
                            {% for course in info.courses %}
                            <span class="course-tag">{{ course }}</span>
                            {% endfor %}
                        </div>
                        {% else %}
                        <div style="color: #7f8c8d; font-style: italic; text-align: center; padding: 10px;">
                            No courses enrolled
                        </div>
                        {% endif %}
                    </div>
                    
                    {% if info.marks %}
                    <div class="info-section">
                        <div class="section-title">
                            <i class="fas fa-star"></i> Current Grades
                        </div>
                        <div class="grades-grid">
                            {% for course, grade in info.marks.items() %}
                            <div class="grade-item">
                                <div class="grade-subject">{{ course }}</div>
                                <div class="grade-score">{{ grade }}%</div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="info-section">
                        <div class="section-title">
                            <i class="fas fa-calendar-check"></i> Attendance
                        </div>
                        <div class="info-item">
                            <div class="info-label">
                                <i class="fas fa-percentage"></i> Rate
                            </div>
                            <div class="info-value">
                                {% set attendance_rate = 85 + (loop.index0 % 16) %}
                                <span class="attendance-indicator {% if attendance_rate >= 90 %}attendance-good{% elif attendance_rate >= 75 %}attendance-warning{% else %}attendance-danger{% endif %}">
                                    <i class="fas fa-{% if attendance_rate >= 90 %}check-circle{% elif attendance_rate >= 75 %}exclamation-triangle{% else %}times-circle{% endif %}"></i>
                                    {{ attendance_rate }}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if not students_info %}
        <div style="text-align: center; padding: 80px 20px; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
            <i class="fas fa-user-graduate" style="font-size: 4rem; color: #bdc3c7; margin-bottom: 20px;"></i>
            <h3 style="color: #2c3e50; margin-bottom: 10px;">No Students Found</h3>
            <p style="color: #7f8c8d;">No students are currently enrolled in your courses.</p>
        </div>
        {% endif %}
    </div>
    
    <script>
        // Search and filter functionality
        const searchInput = document.getElementById('searchInput');
        const courseFilter = document.getElementById('courseFilter');
        const studentsGrid = document.getElementById('studentsGrid');
        const studentCards = document.querySelectorAll('.student-card');
        
        function filterStudents() {
            const searchTerm = searchInput.value.toLowerCase();
            const selectedCourse = courseFilter.value;
            
            studentCards.forEach(card => {
                const studentName = card.dataset.student.toLowerCase();
                const courses = card.dataset.courses.toLowerCase();
                const emailElement = card.querySelector('.info-value');
                const email = emailElement ? emailElement.textContent.toLowerCase() : '';
                
                const matchesSearch = studentName.includes(searchTerm) || 
                                    email.includes(searchTerm) || 
                                    courses.includes(searchTerm);
                                    
                const matchesCourse = !selectedCourse || courses.includes(selectedCourse.toLowerCase());
                
                if (matchesSearch && matchesCourse) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        searchInput.addEventListener('input', filterStudents);
        courseFilter.addEventListener('change', filterStudents);
        
        // Add animation to student cards
        document.addEventListener('DOMContentLoaded', function() {
            studentCards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
    '''
    return render_template_string(template, students_info=students_info)

# Admin Routes
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
        }
        .dashboard { display: flex; min-height: 100vh; }
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #2c3e50 0%, #8e44ad 100%);
            color: white;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar-header {
            padding: 25px 20px;
            background: rgba(0,0,0,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 25px;
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .nav-item:hover {
            background: rgba(255,255,255,0.1);
            color: white;
        }
        .main-content {
            flex: 1;
            margin-left: 280px;
        }
        .top-bar {
            background: white;
            padding: 20px 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .content-area {
            padding: 30px;
        }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .overview-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2><i class="fas fa-user-shield"></i> Edvision360</h2>
                <p>Admin Portal</p>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('add_users') }}" class="nav-item">
                    <i class="fas fa-user-plus"></i> Add Users
                </a>
                <a href="{{ url_for('logout') }}" class="nav-item">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </nav>
        
        <main class="main-content">
            <div class="top-bar">
                <h1>Admin Dashboard</h1>
            </div>
            
            <div class="content-area">
                <div class="overview-grid">
                    <div class="overview-card">
                        <h2>Students ({{ students|length }})</h2>
                        {% if students %}
                            <ul>{% for s in students %}<li>{{ s }}</li>{% endfor %}</ul>
                        {% else %}
                            <p>No students.</p>
                        {% endif %}
                        <p><a href="{{ url_for('admin_students') }}">View all students</a></p>
                    </div>
                    <div class="overview-card">
                        <h2>Teachers ({{ teachers|length }})</h2>
                        {% if teachers %}
                            <ul>{% for t in teachers %}<li>{{ t }}</li>{% endfor %}</ul>
                        {% else %}
                            <p>No teachers.</p>
                        {% endif %}
                        <p><a href="{{ url_for('admin_teachers') }}">View all teachers</a></p>
                    </div>
                    <div class="overview-card">
                        <h2>Admins ({{ admins|length }})</h2>
                        {% if admins %}
                            <ul>{% for a in admins %}<li>{{ a }}</li>{% endfor %}</ul>
                        {% else %}
                            <p>No admins.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </main>
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
                parent_name = (request.form.get('parent_name') or '').strip()
                parent_phone = (request.form.get('parent_phone') or '').strip()
                parent_email = (request.form.get('parent_email') or '').strip()
                selected_courses = request.form.getlist('courses')
                normalized = [c.strip() for c in selected_courses if c.strip()]
                marks = {c: 0 for c in normalized}
                students_info[username] = {
                    'name': name or username,
                    'email': email,
                    'address': address,
                    'courses': normalized,
                    'marks': marks,
                    'parent_name': parent_name,
                    'parent_phone': parent_phone,
                    'parent_email': parent_email
                }
            elif final_role == 'teacher':
                subject = (request.form.get('subject') or '').strip()
                parent_name = (request.form.get('parent_name') or '').strip()
                parent_phone = (request.form.get('parent_phone') or '').strip()
                parent_email = (request.form.get('parent_email') or '').strip()
                teachers_info[username] = {
                    'subject': subject or 'Unknown',
                    'parent_name': parent_name,
                    'parent_phone': parent_phone,
                    'parent_email': parent_email
                }
            message = "User added successfully"
        template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Users - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            text-align: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .page-subtitle {
            color: #7f8c8d;
            font-size: 1rem;
        }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        .form-input, .form-select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #9b59b6;
            box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.1);
        }
        .role-select {
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
            border: none;
            cursor: pointer;
        }
        .form-section {
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        .form-section.student-section {
            border-color: #3498db;
            background: #f8fbff;
        }
        .form-section.teacher-section {
            border-color: #e74c3c;
            background: #fef9f9;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .courses-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .course-checkbox {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: white;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .course-checkbox:hover {
            border-color: #3498db;
            background: #f8fbff;
        }
        .course-checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: #3498db;
        }
        .parent-info-section {
            background: #fff9f9;
            border: 2px solid #ffeaa7;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
        }
        .parent-info-title {
            color: #e17055;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .submit-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin: 0 10px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
        }
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .success-message {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            .courses-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-user-plus"></i>
                Add New User
            </h1>
            <p class="page-subtitle">Create new student, teacher, or admin accounts</p>
        </div>
        
        {% if message %}
        <div class="success-message">
            <i class="fas fa-check-circle"></i>
            {{ message }}
        </div>
        {% endif %}
        
        <form method="post">
            <div class="form-container">
                <div class="form-group">
                    <label class="form-label" for="username">
                        <i class="fas fa-user"></i> Username
                    </label>
                    <input type="text" id="username" name="username" class="form-input" placeholder="Enter username" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="password">
                        <i class="fas fa-lock"></i> Password
                    </label>
                    <input type="password" id="password" name="password" class="form-input" placeholder="Enter password" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="role">
                        <i class="fas fa-user-tag"></i> User Role
                    </label>
                    <select id="role" name="role" class="form-select role-select" required>
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                
                <div id="studentFields" class="form-section student-section">
                    <div class="section-title">
                        <i class="fas fa-user-graduate"></i> Student Information
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label" for="student_name">Full Name</label>
                            <input type="text" id="student_name" name="name" class="form-input" placeholder="Enter full name">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="student_email">Email Address</label>
                            <input type="email" id="student_email" name="email" class="form-input" placeholder="student@example.com">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="student_address">Address</label>
                        <input type="text" id="student_address" name="address" class="form-input" placeholder="Enter full address">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Select Courses</label>
                        <div class="courses-grid">
                            <label class="course-checkbox">
                                <input type="checkbox" name="courses" value="Math">
                                <span>Mathematics</span>
                            </label>
                            <label class="course-checkbox">
                                <input type="checkbox" name="courses" value="Science">
                                <span>Science</span>
                            </label>
                            <label class="course-checkbox">
                                <input type="checkbox" name="courses" value="History">
                                <span>History</span>
                            </label>
                            <label class="course-checkbox">
                                <input type="checkbox" name="courses" value="Coding">
                                <span>Coding</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="parent-info-section">
                        <div class="parent-info-title">
                            <i class="fas fa-users"></i> Parent/Guardian Contact Information
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="parent_name">Parent/Guardian Name</label>
                                <input type="text" id="parent_name" name="parent_name" class="form-input" placeholder="Enter parent name">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="parent_phone">Parent Phone Number</label>
                                <input type="tel" id="parent_phone" name="parent_phone" class="form-input" placeholder="+1-555-0000">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="parent_email">Parent Email Address</label>
                            <input type="email" id="parent_email" name="parent_email" class="form-input" placeholder="parent@example.com">
                        </div>
                    </div>
                </div>
                
                <div id="teacherFields" class="form-section teacher-section">
                    <div class="section-title">
                        <i class="fas fa-chalkboard-teacher"></i> Teacher Information
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="subject">Subject Taught</label>
                        <input type="text" id="subject" name="subject" class="form-input" placeholder="e.g., Mathematics, Science, History">
                    </div>
                    
                    <div class="parent-info-section">
                        <div class="parent-info-title">
                            <i class="fas fa-phone-alt"></i> Emergency Contact Information
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="teacher_parent_name">Emergency Contact Name</label>
                                <input type="text" id="teacher_parent_name" name="parent_name" class="form-input" placeholder="Enter emergency contact name">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="teacher_parent_phone">Emergency Contact Phone</label>
                                <input type="tel" id="teacher_parent_phone" name="parent_phone" class="form-input" placeholder="+1-555-0000">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="teacher_parent_email">Emergency Contact Email</label>
                            <input type="email" id="teacher_parent_email" name="parent_email" class="form-input" placeholder="emergency@example.com">
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="submit-section">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-user-plus"></i> Add User
                </button>
                <a href="{{ url_for('admin_dashboard') }}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </form>
    </div>
    
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
</body>
</html>
        '''
        return render_template_string(template, message=message)
    return redirect(url_for('login'))

@app.route('/admin/students')
def admin_students():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Populate students_info with enrollment data if empty
    for student, courses in student_enrollments.items():
        if student not in students_info:
            students_info[student] = {
                'name': student,
                'email': f'{student.lower()}@student.edu',
                'phone': f'+1-555-{(hash(student) % 9000) + 1000}',
                'address': f'{(hash(student) % 999) + 1} Education St, Learning City',
                'courses': courses,
                'marks': {course: 75 + (hash(student + course) % 26) for course in courses},
                'parent_name': f'{student} Parent',
                'parent_phone': f'+1-555-{(hash(student + "parent") % 9000) + 1000}',
                'parent_email': f'{student.lower()}.parent@email.com'
            }
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - Students Management - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary {
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
        }
        .btn-success {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            font-size: 0.8rem;
            padding: 6px 12px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .search-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .search-bar {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .search-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .search-input:focus {
            outline: none;
            border-color: #9b59b6;
            box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.1);
        }
        .table-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .table-header {
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .table-title {
            font-size: 1.3rem;
            font-weight: 600;
        }
        .table-stats {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .table-wrapper {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 1000px;
        }
        th, td {
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #f1f3f4;
        }
        th {
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .student-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .student-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .student-details {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .student-name {
            font-weight: 600;
            color: #2c3e50;
        }
        .student-id {
            font-size: 0.8rem;
            color: #7f8c8d;
        }
        .contact-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .contact-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            color: #5a6c7d;
        }
        .courses-list {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }
        .course-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .grades-summary {
            text-align: center;
        }
        .avg-grade {
            font-size: 1.2rem;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 2px;
        }
        .grade-count {
            font-size: 0.8rem;
            color: #7f8c8d;
        }
        .action-buttons {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .parent-contact {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .parent-name {
            font-weight: 500;
            color: #2c3e50;
            font-size: 0.85rem;
        }
        .parent-contact-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            color: #5a6c7d;
        }
        .quick-contact {
            display: flex;
            gap: 4px;
            margin-top: 4px;
        }
        .quick-btn {
            padding: 2px 6px;
            border: none;
            border-radius: 4px;
            font-size: 0.7rem;
            cursor: pointer;
            text-decoration: none;
        }
        .email-btn {
            background: #3498db;
            color: white;
        }
        .phone-btn {
            background: #27ae60;
            color: white;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }
        .empty-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .search-bar {
                flex-direction: column;
            }
            .search-input {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-user-graduate"></i>
                Students Management
            </h1>
            <div class="header-actions">
                <a href="{{ url_for('add_users') }}" class="btn btn-success">
                    <i class="fas fa-plus"></i> Add Student
                </a>
                <a href="{{ url_for('admin_teachers') }}" class="btn btn-primary">
                    <i class="fas fa-chalkboard-teacher"></i> Manage Teachers
                </a>
                <a href="{{ url_for('admin_dashboard') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
        
        <div class="search-section">
            <div class="search-bar">
                <input type="text" class="search-input" placeholder="Search students by name, email, course, or parent..." id="searchInput">
                <select class="search-input" style="max-width: 200px;" id="courseFilter">
                    <option value="">All Courses</option>
                    <option value="Math">Math</option>
                    <option value="Science">Science</option>
                    <option value="History">History</option>
                </select>
            </div>
        </div>
        
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">
                    <i class="fas fa-table"></i> Student Directory
                </div>
                <div class="table-stats">
                    {{ students_info|length }} Students Total
                </div>
            </div>
            <div class="table-wrapper">
                {% if students_info %}
                <table id="studentsTable">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Contact Info</th>
                            <th>Enrolled Courses</th>
                            <th>Academic Performance</th>
                            <th>Parent Contact</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for student, info in students_info.items() %}
                        <tr data-student="{{ student }}" data-courses="{{ info.courses|join(',') }}">
                            <td>
                                <div class="student-info">
                                    <div class="student-avatar">
                                        {{ student[0].upper() }}
                                    </div>
                                    <div class="student-details">
                                        <div class="student-name">{{ info.name or student }}</div>
                                        <div class="student-id">ID: STU{{ loop.index0 + 1000 }}</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="contact-info">
                                    <div class="contact-item">
                                        <i class="fas fa-envelope"></i>
                                        {{ info.email or (student.lower() + '@student.edu') }}
                                    </div>
                                    <div class="contact-item">
                                        <i class="fas fa-phone"></i>
                                        {{ info.phone or '+1-555-0000' }}
                                    </div>
                                    <div class="contact-item">
                                        <i class="fas fa-map-marker-alt"></i>
                                        {{ (info.address or 'N/A')[:30] }}{% if info.address and info.address|length > 30 %}...{% endif %}
                                    </div>
                                </div>
                            </td>
                            <td>
                                {% if info.courses %}
                                <div class="courses-list">
                                    {% for course in info.courses %}
                                    <span class="course-tag">{{ course }}</span>
                                    {% endfor %}
                                </div>
                                {% else %}
                                <span style="color: #7f8c8d; font-style: italic;">No courses</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if info.marks %}
                                <div class="grades-summary">
                                    <div class="avg-grade">
                                        {{ "%.1f"|format(info.marks.values()|sum / info.marks.values()|length) }}%
                                    </div>
                                    <div class="grade-count">{{ info.marks|length }} subjects</div>
                                </div>
                                {% else %}
                                <span style="color: #7f8c8d; font-style: italic;">No grades</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if info.parent_name %}
                                <div class="parent-contact">
                                    <div class="parent-name">{{ info.parent_name }}</div>
                                    <div class="parent-contact-item">
                                        <i class="fas fa-phone"></i>
                                        {{ info.parent_phone }}
                                    </div>
                                    <div class="parent-contact-item">
                                        <i class="fas fa-envelope"></i>
                                        {{ info.parent_email[:20] }}{% if info.parent_email|length > 20 %}...{% endif %}
                                    </div>
                                    <div class="quick-contact">
                                        <a href="mailto:{{ info.parent_email }}" class="quick-btn email-btn" title="Email Parent">
                                            <i class="fas fa-envelope"></i>
                                        </a>
                                        <a href="tel:{{ info.parent_phone }}" class="quick-btn phone-btn" title="Call Parent">
                                            <i class="fas fa-phone"></i>
                                        </a>
                                    </div>
                                </div>
                                {% else %}
                                <span style="color: #7f8c8d; font-style: italic;">No parent info</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <a href="{{ url_for('admin_edit_user', username=student) }}" class="btn btn-primary" style="font-size: 0.8rem; padding: 6px 12px;">
                                        <i class="fas fa-edit"></i> Edit
                                    </a>
                                    <form method="post" action="{{ url_for('admin_delete_user', username=student) }}" style="display: inline;" onsubmit="return confirm('Delete {{ student }}? This action cannot be undone.')">
                                        <button type="submit" class="btn btn-danger">
                                            <i class="fas fa-trash"></i> Delete
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-user-graduate empty-icon"></i>
                    <h3>No Students Found</h3>
                    <p>Start by adding your first student to the system.</p>
                    <a href="{{ url_for('add_users') }}" class="btn btn-success" style="margin-top: 20px;">
                        <i class="fas fa-plus"></i> Add First Student
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        // Search and filter functionality
        const searchInput = document.getElementById('searchInput');
        const courseFilter = document.getElementById('courseFilter');
        const tableRows = document.querySelectorAll('#studentsTable tbody tr');
        
        function filterStudents() {
            const searchTerm = searchInput.value.toLowerCase();
            const selectedCourse = courseFilter.value.toLowerCase();
            
            tableRows.forEach(row => {
                const studentName = row.dataset.student.toLowerCase();
                const courses = row.dataset.courses.toLowerCase();
                const cellText = row.textContent.toLowerCase();
                
                const matchesSearch = cellText.includes(searchTerm);
                const matchesCourse = !selectedCourse || courses.includes(selectedCourse);
                
                if (matchesSearch && matchesCourse) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        searchInput.addEventListener('input', filterStudents);
        courseFilter.addEventListener('change', filterStudents);
        
        // Add animation to table rows
        document.addEventListener('DOMContentLoaded', function() {
            tableRows.forEach((row, index) => {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    row.style.transition = 'all 0.5s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, index * 50);
            });
        });
    </script>
</body>
</html>
    '''
    return render_template_string(template, students_info=students_info)

@app.route('/admin/teachers')
def admin_teachers():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Populate teachers_info with data if empty
    for teacher in _users_by_role('teacher'):
        if teacher not in teachers_info:
            teachers_info[teacher] = {
                'name': teacher,
                'email': f'{teacher.lower()}@school.edu',
                'phone': f'+1-555-{(hash(teacher) % 9000) + 1000}',
                'subject': ['Math', 'Science', 'History'][hash(teacher) % 3],
                'experience': f'{(hash(teacher) % 15) + 1} years',
                'qualification': 'Master of Education',
                'parent_name': f'{teacher} Emergency Contact',
                'parent_phone': f'+1-555-{(hash(teacher + "emergency") % 9000) + 1000}',
                'parent_email': f'{teacher.lower()}.emergency@email.com'
            }
    
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - Teachers Management - Edvision360</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-title {
            font-size: 2rem;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header-actions {
            display: flex;
            gap: 15px;
        }
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
        }
        .btn-success {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            font-size: 0.8rem;
            padding: 6px 12px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .search-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
        .search-bar {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .search-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .search-input:focus {
            outline: none;
            border-color: #e74c3c;
            box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
        }
        .filter-dropdown {
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            cursor: pointer;
        }
        .content-section {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .table-container {
            overflow-x: auto;
        }
        .teachers-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }
        .teachers-table th {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .teachers-table td {
            padding: 15px;
            border-bottom: 1px solid #f1f3f4;
            vertical-align: top;
        }
        .teachers-table tr {
            transition: all 0.3s ease;
        }
        .teachers-table tr:hover {
            background: #fef9f9;
            transform: scale(1.01);
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.1);
        }
        .teacher-profile {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .teacher-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .teacher-details {
            flex: 1;
        }
        .teacher-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 4px;
        }
        .teacher-id {
            color: #7f8c8d;
            font-size: 0.85rem;
        }
        .contact-info {
            line-height: 1.8;
        }
        .contact-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
            color: #5a6c7d;
        }
        .contact-item i {
            width: 16px;
            color: #e74c3c;
        }
        .subject-badge {
            display: inline-block;
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 2px;
        }
        .experience-info {
            color: #5a6c7d;
            font-size: 0.9rem;
        }
        .experience-badge {
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
            color: #e74c3c;
        }
        .emergency-contact {
            background: #fef9f9;
            padding: 10px;
            border-radius: 8px;
            border-left: 3px solid #e74c3c;
        }
        .emergency-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .emergency-contact-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 3px;
            color: #5a6c7d;
            font-size: 0.85rem;
        }
        .emergency-contact-item i {
            width: 14px;
            color: #e74c3c;
        }
        .quick-contact {
            display: flex;
            gap: 5px;
            margin-top: 8px;
        }
        .quick-btn {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .email-btn {
            background: #3498db;
            color: white;
        }
        .phone-btn {
            background: #27ae60;
            color: white;
        }
        .action-buttons {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }
        .empty-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px 15px;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
            .search-bar {
                flex-direction: column;
            }
            .search-input {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="page-title">
                <i class="fas fa-chalkboard-teacher"></i>
                Teachers Management
            </h1>
            <div class="header-actions">
                <a href="{{ url_for('add_users') }}" class="btn btn-success">
                    <i class="fas fa-plus"></i> Add Teacher
                </a>
                <a href="{{ url_for('admin_students') }}" class="btn btn-primary">
                    <i class="fas fa-user-graduate"></i> Manage Students
                </a>
                <a href="{{ url_for('admin_dashboard') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
        
        <div class="search-section">
            <div class="search-bar">
                <i class="fas fa-search" style="color: #bdc3c7; margin-left: 15px; position: absolute; z-index: 1;"></i>
                <input type="text" class="search-input" placeholder="Search teachers by name, subject, or qualification..." 
                       style="padding-left: 45px;" onkeyup="filterTeachers()">
                <select class="filter-dropdown" onchange="filterTeachers()">
                    <option value="">All Subjects</option>
                    <option value="Math">Math</option>
                    <option value="Science">Science</option>
                    <option value="History">History</option>
                    <option value="English">English</option>
                </select>
            </div>
        </div>
        
        <div class="content-section">
            <div class="table-container">
                {% if teachers %}
                <table class="teachers-table" id="teachersTable">
                    <thead>
                        <tr>
                            <th>Teacher Profile</th>
                            <th>Contact Information</th>
                            <th>Subject & Experience</th>
                            <th>Emergency Contact</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for teacher in teachers %}
                        {% set info = teachers_info.get(teacher, {}) %}
                        <tr class="teacher-row">
                            <td>
                                <div class="teacher-profile">
                                    <div class="teacher-avatar">
                                        {{ teacher[0].upper() }}
                                    </div>
                                    <div class="teacher-details">
                                        <div class="teacher-name">{{ info.name or teacher }}</div>
                                        <div class="teacher-id">ID: TCH{{ loop.index0 + 1000 }}</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="contact-info">
                                    <div class="contact-item">
                                        <i class="fas fa-envelope"></i>
                                        {{ info.email or (teacher.lower() + '@school.edu') }}
                                    </div>
                                    <div class="contact-item">
                                        <i class="fas fa-phone"></i>
                                        {{ info.phone or '+1-555-0000' }}
                                    </div>
                                    <div class="contact-item">
                                        <i class="fas fa-graduation-cap"></i>
                                        {{ info.qualification or 'Not specified' }}
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="subject-badge">{{ info.subject or 'Not assigned' }}</div>
                                <div class="experience-info">
                                    <span class="experience-badge">{{ info.experience or '0 years' }}</span>
                                </div>
                            </td>
                            <td>
                                {% if info.parent_name %}
                                <div class="emergency-contact">
                                    <div class="emergency-name">{{ info.parent_name }}</div>
                                    <div class="emergency-contact-item">
                                        <i class="fas fa-phone"></i>
                                        {{ info.parent_phone }}
                                    </div>
                                    <div class="emergency-contact-item">
                                        <i class="fas fa-envelope"></i>
                                        {{ info.parent_email[:20] }}{% if info.parent_email|length > 20 %}...{% endif %}
                                    </div>
                                    <div class="quick-contact">
                                        <a href="mailto:{{ info.parent_email }}" class="quick-btn email-btn" title="Email Emergency Contact">
                                            <i class="fas fa-envelope"></i>
                                        </a>
                                        <a href="tel:{{ info.parent_phone }}" class="quick-btn phone-btn" title="Call Emergency Contact">
                                            <i class="fas fa-phone"></i>
                                        </a>
                                    </div>
                                </div>
                                {% else %}
                                <span style="color: #7f8c8d; font-style: italic;">No emergency contact</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <a href="{{ url_for('admin_edit_user', username=teacher) }}" class="btn btn-primary" style="font-size: 0.8rem; padding: 6px 12px;">
                                        <i class="fas fa-edit"></i> Edit
                                    </a>
                                    <form method="post" action="{{ url_for('admin_delete_user', username=teacher) }}" style="display: inline;" onsubmit="return confirm('Delete {{ teacher }}? This action cannot be undone.')">
                                        <button type="submit" class="btn btn-danger">
                                            <i class="fas fa-trash"></i> Delete
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-chalkboard-teacher empty-icon"></i>
                    <h3>No Teachers Found</h3>
                    <p>Start by adding your first teacher to the system.</p>
                    <a href="{{ url_for('add_users') }}" class="btn btn-success" style="margin-top: 20px;">
                        <i class="fas fa-plus"></i> Add First Teacher
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        function filterTeachers() {
            const searchInput = document.querySelector('.search-input').value.toLowerCase();
            const subjectFilter = document.querySelector('.filter-dropdown').value;
            const rows = document.querySelectorAll('.teacher-row');
            
            rows.forEach(row => {
                const teacherName = row.querySelector('.teacher-name').textContent.toLowerCase();
                const subject = row.querySelector('.subject-badge').textContent.toLowerCase();
                const qualification = row.querySelector('.contact-info .contact-item:nth-child(3)').textContent.toLowerCase();
                
                const matchesSearch = teacherName.includes(searchInput) || 
                                    subject.includes(searchInput) || 
                                    qualification.includes(searchInput);
                const matchesSubject = !subjectFilter || subject.includes(subjectFilter.toLowerCase());
                
                if (matchesSearch && matchesSubject) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
    '''
    return render_template_string(template, teachers=_users_by_role('teacher'), teachers_info=teachers_info)

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
            parent_name = (request.form.get('parent_name') or '').strip()
            parent_phone = (request.form.get('parent_phone') or '').strip()
            parent_email = (request.form.get('parent_email') or '').strip()
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
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_email': parent_email
            }
        elif role == 'teacher':
            subject = (request.form.get('subject') or '').strip()
            parent_name = (request.form.get('parent_name') or '').strip()
            parent_phone = (request.form.get('parent_phone') or '').strip()
            parent_email = (request.form.get('parent_email') or '').strip()
            teachers_info[username] = {
                'subject': subject or 'Unknown',
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_email': parent_email
            }
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
            <h4>Parent Contact Information</h4>
            <input type="text" name="parent_name" placeholder="Parent Name" value="{{ (s_info and s_info.parent_name) or '' }}">
            <input type="tel" name="parent_phone" placeholder="Parent Phone" value="{{ (s_info and s_info.parent_phone) or '' }}">
            <input type="email" name="parent_email" placeholder="Parent Email" value="{{ (s_info and s_info.parent_email) or '' }}">
        </fieldset>
        {% elif role == 'teacher' %}
        <fieldset>
            <legend>Teacher Details</legend>
            <input type="text" name="subject" placeholder="Subject taught" value="{{ (t_info and t_info.subject) or '' }}">
            <h4>Emergency Contact Information</h4>
            <input type="text" name="parent_name" placeholder="Emergency Contact Name" value="{{ (t_info and t_info.parent_name) or '' }}">
            <input type="tel" name="parent_phone" placeholder="Emergency Contact Phone" value="{{ (t_info and t_info.parent_phone) or '' }}">
            <input type="email" name="parent_email" placeholder="Emergency Contact Email" value="{{ (t_info and t_info.parent_email) or '' }}">
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







