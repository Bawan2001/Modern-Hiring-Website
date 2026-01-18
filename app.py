from flask import Flask, jsonify, request, render_template
import json
import os

app = Flask(__name__)

DATA_FILE = 'data/jobs.json'

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
    return render_template('index.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify(load_jobs())

@app.route('/api/jobs', methods=['POST'])
def add_job():
    job = request.json
    jobs = load_jobs()
    job['id'] = len(jobs) + 1
    jobs.append(job)
    save_jobs(jobs)
    return jsonify(job), 201

if __name__ == '__main__':
    app.run(debug=True)
