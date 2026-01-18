from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'jobsphere_premium_secret_key'

DATA_FILE = 'data/jobs.json'

# Simple user storage for demonstration
USERS = {
    "user@example.com": {"password": "user123", "role": "user", "name": "John Doe"},
    "admin@jobsphere.com": {"password": "admin123", "role": "admin", "name": "Admin Master"}
}

def load_jobs():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_jobs(jobs):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(jobs, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = {"email": email, "role": user['role'], "name": user['name']}
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/ats')
def ats():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('ats.html', user=session.get('user'))

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'admin':
        return redirect(url_for('index'))
    return render_template('admin.html', user=session.get('user'))

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify(load_jobs())

@app.route('/api/jobs', methods=['POST'])
def add_job():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    job = request.json
    jobs = load_jobs()
    job['id'] = len(jobs) + 1
    jobs.append(job)
    save_jobs(jobs)
    return jsonify(job), 201

@app.route('/api/ats-score', methods=['POST'])
def calculate_ats():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    resume_text = data.get('resume', '').lower()
    job_desc = data.get('description', '').lower()
    
    if not resume_text or not job_desc:
        return jsonify({"error": "Missing input"}), 400
        
    # Simple keyword matching algorithm
    keywords = re.findall(r'\w+', job_desc)
    unique_keywords = set(keywords)
    
    if not unique_keywords:
        return jsonify({"score": 0, "matching_keywords": []})
        
    matched_keywords = [kw for kw in unique_keywords if kw in resume_text]
    score = (len(matched_keywords) / len(unique_keywords)) * 100
    
    return jsonify({
        "score": round(score, 2),
        "matched_count": len(matched_keywords),
        "total_keywords": len(unique_keywords),
        "matched_keywords": matched_keywords[:10], # Return top 10
        "suggestions": list(unique_keywords - set(matched_keywords))[:5] # Suggest some missing ones
    })

if __name__ == '__main__':
    app.run(debug=True)
