import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration class"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jobsphere-super-secret-key-2026'
    WTF_CSRF_ENABLED = True
    
    # SQLite Database (Free, no server required)
    # SQLite Database (Free, no server required)
    # Check if running on Vercel (read-only file system)
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/jobsphere.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'jobsphere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # Pagination
    JOBS_PER_PAGE = 12
    USERS_PER_PAGE = 20
