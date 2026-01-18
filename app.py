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

APP_DATA_FILE = 'data/applications.json'

def load_applications():
    if not os.path.exists(APP_DATA_FILE):
        return []
    with open(APP_DATA_FILE, 'r') as f:
        return json.load(f)

def save_applications(apps):
    os.makedirs(os.path.dirname(APP_DATA_FILE), exist_ok=True)
    with open(APP_DATA_FILE, 'w') as f:
        json.dump(apps, f, indent=4)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/api/apply', methods=['POST'])
def apply_job():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    job_id = data.get('job_id')
    cover_letter = data.get('cover_letter', '')
    
    if not job_id:
        return jsonify({"error": "Missing job ID"}), 400
        
    applications = load_applications()
    
    # Check if already applied
    for app in applications:
        if app['user_email'] == session['user']['email'] and app['job_id'] == job_id:
             return jsonify({"error": "Already applied to this job"}), 400

    new_app = {
        "id": len(applications) + 1,
        "job_id": job_id,
        "user_email": session['user']['email'],
        "user_name": session['user']['name'],
        "cover_letter": cover_letter,
        "status": "Pending",
        "date": "Just now" # simplified date
    }
    
    applications.append(new_app)
    save_applications(applications)
    return jsonify(new_app), 201

@app.route('/api/applications', methods=['GET'])
def get_applications():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    apps = load_applications()
    jobs = {job['id']: job for job in load_jobs()}
    
    # Attach job details to applications
    for app in apps:
        job = jobs.get(app['job_id'])
        if job:
            app['job_title'] = job['title']
            app['company'] = job['company']
            
    if session['user']['role'] == 'admin':
        return jsonify(apps)
    else:
        # Users see only their own
        user_apps = [app for app in apps if app['user_email'] == session['user']['email']]
        return jsonify(user_apps)

@app.route('/api/applications/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    status = request.json.get('status')
    if not status:
         return jsonify({"error": "Missing status"}), 400
         
    applications = load_applications()
    for app in applications:
        if app['id'] == app_id:
            app['status'] = status
            save_applications(applications)
            return jsonify(app)
            
    return jsonify({"error": "Application not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
