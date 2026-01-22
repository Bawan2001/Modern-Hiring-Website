from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, TextAreaField, SelectField, 
                     IntegerField, BooleanField, DateField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """User registration form"""
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be 2-100 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('I am a', choices=[
        ('jobseeker', 'Job Seeker - Looking for opportunities'),
        ('employer', 'Employer - Hiring talent')
    ], default='jobseeker')
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])


class ProfileForm(FlaskForm):
    """Job seeker profile form"""
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('About Me', validators=[Optional(), Length(max=2000)])
    skills = StringField('Skills (comma-separated)', validators=[Optional(), Length(max=500)])
    resume = FileField('Resume/CV', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, DOCX files allowed')
    ])


class CompanyForm(FlaskForm):
    """Employer company profile form"""
    name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required'),
        Length(min=2, max=150)
    ])
    description = TextAreaField('Company Description', validators=[
        Optional(),
        Length(max=5000)
    ])
    website = StringField('Website', validators=[Optional(), Length(max=255)])
    location = StringField('Headquarters Location', validators=[Optional(), Length(max=100)])
    industry = StringField('Industry', validators=[Optional(), Length(max=100)])
    size = SelectField('Company Size', choices=[
        ('', 'Select size'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees')
    ], validators=[Optional()])
    founded_year = IntegerField('Founded Year', validators=[
        Optional(),
        NumberRange(min=1800, max=2030, message='Please enter a valid year')
    ])
    logo = FileField('Company Logo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files allowed')
    ])


class JobForm(FlaskForm):
    """Job posting form"""
    title = StringField('Job Title', validators=[
        DataRequired(message='Job title is required'),
        Length(min=5, max=200)
    ])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    description = TextAreaField('Job Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=50, max=10000, message='Description must be 50-10000 characters')
    ])
    requirements = TextAreaField('Requirements', validators=[
        Optional(),
        Length(max=5000)
    ])
    responsibilities = TextAreaField('Responsibilities', validators=[
        Optional(),
        Length(max=5000)
    ])
    location = StringField('Job Location', validators=[
        DataRequired(message='Location is required'),
        Length(max=100)
    ])
    job_type = SelectField('Job Type', choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote'),
        ('Internship', 'Internship')
    ], default='Full-time')
    experience_level = SelectField('Experience Level', choices=[
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
        ('Lead', 'Lead / Manager')
    ], validators=[Optional()])
    salary_min = IntegerField('Minimum Salary', validators=[
        Optional(),
        NumberRange(min=0, message='Salary must be positive')
    ])
    salary_max = IntegerField('Maximum Salary', validators=[
        Optional(),
        NumberRange(min=0, message='Salary must be positive')
    ])
    is_remote = BooleanField('Remote Work Available')
    expiry_days = SelectField('Listing Duration', choices=[
        ('30', '30 days'),
        ('60', '60 days'),
        ('90', '90 days')
    ], default='30')


class ApplicationForm(FlaskForm):
    """Job application form"""
    job_id = HiddenField('Job ID', validators=[DataRequired()])
    cover_letter = TextAreaField('Cover Letter', validators=[
        Optional(),
        Length(max=5000)
    ])
    resume = FileField('Resume (optional - use profile resume if not provided)', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, DOCX files allowed')
    ])


class CategoryForm(FlaskForm):
    """Category form for admin"""
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = StringField('Description', validators=[
        Optional(),
        Length(max=255)
    ])
    icon = StringField('Icon Class', validators=[Optional(), Length(max=50)])


class ApplicationStatusForm(FlaskForm):
    """Form for updating application status"""
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired')
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
