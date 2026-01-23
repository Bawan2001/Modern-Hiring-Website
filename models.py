from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for all roles: admin, employer, jobseeker"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='jobseeker')  # admin, employer, jobseeker
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    resume_path = db.Column(db.String(255))
    skills = db.Column(db.Text)  # Comma-separated skills
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='owner', uselist=False, lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_employer(self):
        return self.role == 'employer'
    
    def is_jobseeker(self):
        return self.role == 'jobseeker'
    
    def __repr__(self):
        return f'<User {self.email}>'


class Company(db.Model):
    """Company/Employer profile model"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    location = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # e.g., "1-10", "11-50", "51-200", etc.
    founded_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'


class Category(db.Model):
    """Job category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))  # Icon class name
    
    # Relationships
    jobs = db.relationship('Job', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Job(db.Model):
    """Job posting model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Part-time, Contract, Remote, Internship
    experience_level = db.Column(db.String(50))  # Entry, Mid, Senior, Lead
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10), default='USD')
    is_remote = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=True)  # Admin approval
    views = db.Column(db.Integer, default=0)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_expired(self):
        return datetime.utcnow() > self.expiry_date if self.expiry_date else False
    
    def is_visible(self):
        return self.is_active and self.is_approved and not self.is_expired()
    
    def format_salary(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Competitive"
    
    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    """Job application model"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    resume_path = db.Column(db.String(255))  # Custom resume for this application
    status = db.Column(db.String(50), default='Pending')  # Pending, Reviewed, Shortlisted, Rejected, Hired
    notes = db.Column(db.Text)  # Employer notes
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one application per job per user
    __table_args__ = (
        db.UniqueConstraint('job_id', 'user_id', name='unique_application'),
    )
    
    def __repr__(self):
        return f'<Application {self.id} - Job {self.job_id}>'
