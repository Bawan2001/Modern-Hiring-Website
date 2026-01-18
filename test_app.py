import pytest
from app import app, USERS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        yield client

def test_get_jobs(client):
    rv = client.get('/api/jobs')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

def test_login_success(client):
    rv = client.post('/login', data=dict(
        email='user@example.com',
        password='user123'
    ), follow_redirects=True)
    assert b'Hi, <span>John</span>' in rv.data

def test_login_fail(client):
    rv = client.post('/login', data=dict(
        email='user@example.com',
        password='wrongpassword'
    ), follow_redirects=True)
    assert b'Invalid credentials' in rv.data

def test_admin_access_restricted(client):
    # No login -> redirects to login
    rv = client.get('/admin', follow_redirects=True)
    assert b'Welcome Back' in rv.data
    
    # User login -> redirects to home
    with client.session_transaction() as sess:
        sess['user'] = {"email": "user@example.com", "role": "user", "name": "John Doe"}
    rv = client.get('/admin', follow_redirects=True)
    assert b'Featured Opportunities' in rv.data

def test_ats_score_calculation(client):
    with client.session_transaction() as sess:
        sess['user'] = {"email": "user@example.com", "role": "user", "name": "John Doe"}
    
    rv = client.post('/api/ats-score', json={
        "resume": "python flask developer with experience in javascript",
        "description": "we need a flask developer"
    })
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['score'] > 0

def test_application_flow(client):
    # 1. Login as User
    with client.session_transaction() as sess:
        sess['user'] = {"email": "user@example.com", "role": "user", "name": "John Doe"}
    
    # 2. Apply for a job
    rv = client.post('/api/apply', json={
        "job_id": 1,
        "cover_letter": "I am the best candidate."
    })
    assert rv.status_code == 201
    
    # 3. Check Dashboard
    rv = client.get('/api/applications')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['status'] == 'Pending'
    
    # 4. Login as Admin
    with client.session_transaction() as sess:
        sess['user'] = {"email": "admin@jobsphere.com", "role": "admin", "name": "Admin"}
        
    # 5. Update Status
    app_id = data[0]['id']
    rv = client.post(f'/api/applications/{app_id}/status', json={"status": "Interviewing"})
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'Interviewing'
