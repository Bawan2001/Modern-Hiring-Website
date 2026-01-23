import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def get_database_uri():
    """Get database URI based on environment"""
    # First check for explicit DATABASE_URL (production databases like Neon, Supabase, etc.)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle postgres:// vs postgresql:// (some providers use postgres://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Check if running on Vercel (read-only file system)
    if os.environ.get('VERCEL'):
        return 'sqlite:////tmp/jobsphere.db'
    
    # Local development
    return 'sqlite:///' + os.path.join(basedir, 'jobsphere.db')


class Config:
    """Application configuration class"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jobsphere-super-secret-key-2026'
    WTF_CSRF_ENABLED = True
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File Uploads
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
    else:
        UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # Pagination
    JOBS_PER_PAGE = 12
    USERS_PER_PAGE = 20
