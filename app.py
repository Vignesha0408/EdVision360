from flask import Flask, request, redirect, url_for, session, render_template_string
import random

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Needed for session management

# Store candidates and votes in memory
candidates = []
votes = {}
total_votes_needed = 0
result_password = 'SDMIT'  # Password to access results
captcha_value = ''  # CAPTCHA value for validation

# Admin login
@app.route('/', methods=['GET', 'POST'])
def admin_authentication():
    global result_password
    if request.method == 'POST':
        input_password = request.form['password']
        if input_password == result_password:
            return redirect(url_for('setup_candidates'))
        else:
            return '<h3>Incorrect password. Please try again.</h3>'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Admin Authentication</title></head>
    <body>
        <h1>Admin Login</h1>
        <form method="POST">
            <label for="password">Enter Password:</label>
            <input type="password" name="password" required><br><br>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    '''

# Setup voting system (only accessible after admin login)
@app.route('/setup', methods=['GET', 'POST'])
def setup_candidates():
    if request.method == 'POST':
        num_candidates = int(request.form['num_candidates'])
        global candidates, votes, total_votes_needed
        candidates = [request.form[f'candidate_{i+1}'] for i in range(num_candidates)]
        votes = {candidate: 0 for candidate in candidates}
        total_votes_needed = int(request.form['total_votes_needed'])
        session['votes_cast'] = 0
        return redirect(url_for('vote'))

    # Setup form to enter candidates and voter count
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Setup Voting</title></head>
    <body>
        <h1>Set up your voting machine</h1>
        <form method="POST">
            <label for="num_candidates">Number of Candidates:</label>
            <input type="number" name="num_candidates" min="1" required><br><br>
            <div id="candidate_inputs"></div>
            <button type="button" onclick="generateCandidateInputs()">Generate Candidate Inputs</button><br><br>
            <label for="total_votes_needed">Number of Total Voters:</label>
            <input type="number" name="total_votes_needed" min="1" required><br><br>
            <button type="submit">Set up</button>
        </form>
        <script>
        function generateCandidateInputs() {
            const numCandidates = document.querySelector('input[name="num_candidates"]').value;
            const candidateInputsDiv = document.getElementById("candidate_inputs");
            candidateInputsDiv.innerHTML = "";
            for (let i = 1; i <= numCandidates; i++) {
                candidateInputsDiv.innerHTML += `
                    <label for="candidate_${i}">Candidate ${i} Name:</label>
                    <input type="text" name="candidate_${i}" required><br><br>
                `;
            }
        }
        </script>
    </body>
    </html>
    '''

# CAPTCHA generation
def generate_captcha():
    global captcha_value
    captcha_value = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=3))

# Vote casting
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    global captcha_value
    if request.method == 'POST':
        candidate = request.form['candidate']
        captcha_input = request.form['captcha']
        if captcha_input != captcha_value:
            return '<h3>Invalid CAPTCHA. Please try again.</h3><a href="/vote">Go Back</a>'

        if candidate in votes:
            votes[candidate] += 1
            session['votes_cast'] += 1

        # Confirmation after voting
        if session['votes_cast'] >= total_votes_needed:
            return redirect(url_for('enter_password'))

        return '<h3>Vote cast successfully!</h3><a href="/vote">Vote again</a>'

    # Voting form with CAPTCHA
    generate_captcha()
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Voting</title></head>
    <body bgcolor='pink'>
        <h1>Vote for Your Candidate</h1>
        <form method="POST">
            {}
            <br>
            <label for="captcha">Enter CAPTCHA: {}</label>
            <input type="text" name="captcha" required><br><br>
            <button type="submit">Submit Vote</button>
        </form>
    </body>
    </html>
    '''.format(''.join(f'<label><input type="radio" name="candidate" value="{candidate}"> {candidate}</label><br>' for candidate in candidates), captcha_value)

# Enter password to view results
@app.route('/enter_password', methods=['GET', 'POST'])
def enter_password():
    if request.method == 'POST':
        password = request.form['password']
        if password == result_password:
            return redirect(url_for('results'))
        else:
            return '<h3>Incorrect password. Please try again.</h3><a href="/enter_password">Try again</a>'

    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Enter Password</title></head>
    <body>
        <h1>Enter the password to view the results</h1>
        <form method="POST">
            <label for="password">Password:</label>
            <input type="password" name="password" required><br><br>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    '''

# Display voting results with charts
@app.route('/results')
def results():
    labels = list(votes.keys())
    data = list(votes.values())

    # Display results and Chart.js for voting data
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voting Results</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Final Voting Results</h1>
        <ul>
            {% for candidate, vote_count in votes.items() %}
            <li>{{ candidate }}: {{ vote_count }} votes</li>
            {% endfor %}
        </ul>

        <canvas id="resultsChart"></canvas>
        <script>
        var ctx = document.getElementById('resultsChart').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: {{ labels }},
                datasets: [{
                    label: 'Votes',
                    data: {{ data }},
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        </script>
    </body>
    </html>
    ''', votes=votes, labels=labels, data=data)

if __name__ == '__main__':
    app.run(debug=True)
