import os
import io
import re
from functools import wraps
from datetime import datetime, timedelta

from flask import (Flask, render_template, redirect, url_for, flash, request, 
                   jsonify, send_from_directory, abort)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Company, Category, Job, Application
from forms import (LoginForm, RegistrationForm, ProfileForm, CompanyForm, 
                   JobForm, ApplicationForm, CategoryForm, ApplicationStatusForm)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='public/static')
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ========== ROLE DECORATORS ==========
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_employer():
            flash('Employer access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def jobseeker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_jobseeker():
            flash('Job seeker access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ========== UTILITY FUNCTIONS ==========
def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(file, subfolder='resumes'):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        return os.path.join(subfolder, unique_filename)
    return None


def seed_database():
    """Seed initial data if database is empty"""
    # Create admin user if none exists
    if not User.query.filter_by(role='admin').first():
        admin = User(
            email='admin@jobsphere.com',
            name='Admin Master',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create demo employer
    if not User.query.filter_by(email='employer@demo.com').first():
        employer = User(
            email='employer@demo.com',
            name='Demo Employer',
            role='employer'
        )
        employer.set_password('employer123')
        db.session.add(employer)
        db.session.flush()
        
        # Add company for demo employer
        company = Company(
            user_id=employer.id,
            name='TechCorp Solutions',
            description='A leading technology company specializing in innovative solutions.',
            location='San Francisco, CA',
            industry='Technology',
            size='51-200'
        )
        db.session.add(company)
    
    # Create demo job seeker
    if not User.query.filter_by(email='user@example.com').first():
        seeker = User(
            email='user@example.com',
            name='John Doe',
            role='jobseeker',
            skills='Python, JavaScript, Flask, React'
        )
        seeker.set_password('user123')
        db.session.add(seeker)
    
    # Create categories if none exist
    if Category.query.count() == 0:
        categories = [
            Category(name='Technology', description='Software, IT, and tech roles', icon='💻'),
            Category(name='Design', description='UI/UX, Graphic Design roles', icon='🎨'),
            Category(name='Marketing', description='Digital marketing, SEO, content', icon='📢'),
            Category(name='Sales', description='Sales and business development', icon='💼'),
            Category(name='Finance', description='Accounting, finance, banking', icon='💰'),
            Category(name='Healthcare', description='Medical and healthcare roles', icon='🏥'),
            Category(name='Education', description='Teaching and training', icon='📚'),
            Category(name='Engineering', description='Engineering and construction', icon='⚙️'),
        ]
        db.session.add_all(categories)
    
    # Create sample jobs if none exist
    if Job.query.count() == 0:
        company = Company.query.first()
        if company:
            tech_cat = Category.query.filter_by(name='Technology').first()
            jobs = [
                Job(
                    company_id=company.id,
                    category_id=tech_cat.id if tech_cat else None,
                    title='Senior Python Developer',
                    description='We are looking for an experienced Python developer to join our team. You will work on building scalable web applications using Flask and Django.',
                    requirements='5+ years Python experience\nFlask/Django expertise\nSQL databases\nREST API development',
                    location='San Francisco, CA',
                    job_type='Full-time',
                    experience_level='Senior',
                    salary_min=120000,
                    salary_max=180000,
                    is_remote=True
                ),
                Job(
                    company_id=company.id,
                    category_id=tech_cat.id if tech_cat else None,
                    title='Full Stack Engineer',
                    description='Join our engineering team to build modern web applications using React and Node.js.',
                    requirements='3+ years full stack experience\nReact/Vue.js\nNode.js/Express\nMongoDB or PostgreSQL',
                    location='New York, NY',
                    job_type='Full-time',
                    experience_level='Mid',
                    salary_min=90000,
                    salary_max=140000
                ),
                Job(
                    company_id=company.id,
                    category_id=tech_cat.id if tech_cat else None,
                    title='DevOps Engineer',
                    description='We need a skilled DevOps engineer to manage our cloud infrastructure and CI/CD pipelines.',
                    requirements='AWS/GCP experience\nDocker/Kubernetes\nTerraform\nCI/CD tools',
                    location='Remote',
                    job_type='Remote',
                    experience_level='Senior',
                    salary_min=130000,
                    salary_max=170000,
                    is_remote=True
                ),
            ]
            db.session.add_all(jobs)
    
    db.session.commit()


# ========== MAIN ROUTES ==========
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    category_id = request.args.get('category', 0, type=int)
    
    # Build query for visible jobs
    query = Job.query.filter(
        Job.is_active == True,
        Job.is_approved == True,
        Job.expiry_date > datetime.utcnow()
    )
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%')
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if category_id:
        query = query.filter(Job.category_id == category_id)
    
    # Get paginated results
    jobs = query.order_by(Job.posted_date.desc()).paginate(
        page=page, per_page=app.config['JOBS_PER_PAGE'], error_out=False
    )
    
    categories = Category.query.all()
    
    return render_template('index.html', 
                         jobs=jobs, 
                         categories=categories,
                         search=search,
                         location=location,
                         job_type=job_type,
                         category_id=category_id)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if not job.is_visible() and (not current_user.is_authenticated or 
        (not current_user.is_admin() and 
         not (current_user.is_employer() and current_user.company and job.company_id == current_user.company.id))):
        abort(404)
    
    # Increment view count
    job.views += 1
    db.session.commit()
    
    # Check if user already applied
    has_applied = False
    if current_user.is_authenticated and current_user.is_jobseeker():
        has_applied = Application.query.filter_by(
            job_id=job_id, user_id=current_user.id
        ).first() is not None
    
    # Get similar jobs
    similar_jobs = Job.query.filter(
        Job.id != job_id,
        Job.category_id == job.category_id,
        Job.is_active == True,
        Job.is_approved == True
    ).limit(3).all()
    
    return render_template('job_detail.html', job=job, has_applied=has_applied, similar_jobs=similar_jobs)


# ========== AUTHENTICATION ROUTES ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('login.html', form=form)
            
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on role
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            elif user.is_employer():
                return redirect(url_for('employer_dashboard'))
            return redirect(url_for('index'))
        
        flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email exists
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Email already registered. Please login instead.', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            email=form.email.data.lower(),
            name=form.name.data,
            role=form.role.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        # Create company profile for employers
        if form.role.data == 'employer':
            company = Company(
                user_id=user.id,
                name=f"{form.name.data}'s Company"
            )
            db.session.add(company)
        
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ========== JOB SEEKER ROUTES ==========
@app.route('/profile', methods=['GET', 'POST'])
@login_required
@jobseeker_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        current_user.skills = form.skills.data
        
        if form.resume.data:
            resume_path = save_file(form.resume.data, 'resumes')
            if resume_path:
                current_user.resume_path = resume_path
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)


@app.route('/my-applications')
@login_required
@jobseeker_required
def my_applications():
    status_filter = request.args.get('status', '')
    
    query = Application.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications = query.order_by(Application.applied_date.desc()).all()
    
    return render_template('my_applications.html', applications=applications, status_filter=status_filter)


@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
@jobseeker_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if not job.is_visible():
        flash('This job is no longer accepting applications.', 'error')
        return redirect(url_for('index'))
    
    # Check if already applied
    existing = Application.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if existing:
        flash('You have already applied for this position.', 'warning')
        return redirect(url_for('job_detail', job_id=job_id))
    
    cover_letter = request.form.get('cover_letter', '')
    resume_file = request.files.get('resume')
    
    resume_path = None
    if resume_file and resume_file.filename:
        resume_path = save_file(resume_file, 'resumes')
    elif current_user.resume_path:
        resume_path = current_user.resume_path
    
    application = Application(
        job_id=job_id,
        user_id=current_user.id,
        cover_letter=cover_letter,
        resume_path=resume_path
    )
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('my_applications'))


@app.route('/ats')
@login_required
def ats():
    return render_template('ats.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_employer():
        return redirect(url_for('employer_dashboard'))
    return redirect(url_for('my_applications'))


# ========== EMPLOYER ROUTES ==========
@app.route('/employer/dashboard')
@login_required
@employer_required
def employer_dashboard():
    company = current_user.company
    if not company:
        flash('Please complete your company profile first.', 'warning')
        return redirect(url_for('employer_profile'))
    
    # Get stats
    total_jobs = Job.query.filter_by(company_id=company.id).count()
    active_jobs = Job.query.filter_by(company_id=company.id, is_active=True).count()
    
    # Get all applications for employer's jobs
    job_ids = [j.id for j in company.jobs]
    total_applications = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    pending_applications = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'Pending'
    ).count() if job_ids else 0
    
    # Recent applications
    recent_applications = Application.query.filter(
        Application.job_id.in_(job_ids)
    ).order_by(Application.applied_date.desc()).limit(5).all() if job_ids else []
    
    return render_template('employer/dashboard.html',
                         company=company,
                         total_jobs=total_jobs,
                         active_jobs=active_jobs,
                         total_applications=total_applications,
                         pending_applications=pending_applications,
                         recent_applications=recent_applications)


@app.route('/employer/profile', methods=['GET', 'POST'])
@login_required
@employer_required
def employer_profile():
    company = current_user.company
    if not company:
        company = Company(user_id=current_user.id, name=f"{current_user.name}'s Company")
        db.session.add(company)
        db.session.commit()
    
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        company.website = form.website.data
        company.location = form.location.data
        company.industry = form.industry.data
        company.size = form.size.data
        company.founded_year = form.founded_year.data
        
        if form.logo.data:
            logo_path = save_file(form.logo.data, 'logos')
            if logo_path:
                company.logo_path = logo_path
        
        db.session.commit()
        flash('Company profile updated!', 'success')
        return redirect(url_for('employer_dashboard'))
    
    return render_template('employer/profile.html', form=form, company=company)


@app.route('/employer/jobs')
@login_required
@employer_required
def employer_jobs():
    if not current_user.company:
        flash('Please complete your company profile first.', 'warning')
        return redirect(url_for('employer_profile'))
    
    jobs = Job.query.filter_by(company_id=current_user.company.id).order_by(Job.posted_date.desc()).all()
    return render_template('employer/jobs.html', jobs=jobs)


@app.route('/employer/jobs/new', methods=['GET', 'POST'])
@login_required
@employer_required
def employer_job_new():
    if not current_user.company:
        flash('Please complete your company profile first.', 'warning')
        return redirect(url_for('employer_profile'))
    
    form = JobForm()
    form.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        expiry_days = int(form.expiry_days.data)
        job = Job(
            company_id=current_user.company.id,
            category_id=form.category_id.data if form.category_id.data else None,
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            responsibilities=form.responsibilities.data,
            location=form.location.data,
            job_type=form.job_type.data,
            experience_level=form.experience_level.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            is_remote=form.is_remote.data,
            expiry_date=datetime.utcnow() + timedelta(days=expiry_days)
        )
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('employer_jobs'))
    
    return render_template('employer/job_form.html', form=form, is_edit=False)


@app.route('/employer/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@employer_required
def employer_job_edit(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.company_id != current_user.company.id:
        abort(403)
    
    form = JobForm(obj=job)
    form.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        job.category_id = form.category_id.data if form.category_id.data else None
        job.title = form.title.data
        job.description = form.description.data
        job.requirements = form.requirements.data
        job.responsibilities = form.responsibilities.data
        job.location = form.location.data
        job.job_type = form.job_type.data
        job.experience_level = form.experience_level.data
        job.salary_min = form.salary_min.data
        job.salary_max = form.salary_max.data
        job.is_remote = form.is_remote.data
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('employer_jobs'))
    
    return render_template('employer/job_form.html', form=form, job=job, is_edit=True)


@app.route('/employer/jobs/<int:job_id>/toggle', methods=['POST'])
@login_required
@employer_required
def employer_job_toggle(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.company_id != current_user.company.id:
        abort(403)
    
    job.is_active = not job.is_active
    db.session.commit()
    
    status = 'activated' if job.is_active else 'deactivated'
    flash(f'Job {status} successfully!', 'success')
    return redirect(url_for('employer_jobs'))


@app.route('/employer/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
@employer_required
def employer_job_delete(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.company_id != current_user.company.id:
        abort(403)
    
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('employer_jobs'))


@app.route('/employer/jobs/<int:job_id>/applicants')
@login_required
@employer_required
def employer_job_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.company_id != current_user.company.id:
        abort(403)
    
    applications = Application.query.filter_by(job_id=job_id).order_by(Application.applied_date.desc()).all()
    return render_template('employer/applicants.html', job=job, applications=applications)


@app.route('/employer/applications/<int:app_id>/status', methods=['POST'])
@login_required
@employer_required
def employer_update_status(app_id):
    application = Application.query.get_or_404(app_id)
    
    if application.job.company_id != current_user.company.id:
        abort(403)
    
    new_status = request.form.get('status')
    notes = request.form.get('notes')
    
    if new_status:
        application.status = new_status
    if notes:
        application.notes = notes
    
    db.session.commit()
    
    flash('Application status updated!', 'success')
    return redirect(url_for('employer_job_applicants', job_id=application.job_id))


@app.route('/download/resume/<path:filename>')
@login_required
def download_resume(filename):
    # Security check - only the owner, employer of applied job, or admin can download
    if current_user.is_admin():
        pass  # Admin can download any
    elif current_user.is_employer():
        # Check if this resume belongs to an applicant of their job
        app = Application.query.filter_by(resume_path=filename).first()
        if not app or app.job.company_id != current_user.company.id:
            user = User.query.filter_by(resume_path=filename).first()
            if not user:
                abort(403)
            app = Application.query.filter(
                Application.user_id == user.id,
                Application.job_id.in_([j.id for j in current_user.company.jobs])
            ).first()
            if not app:
                abort(403)
    elif current_user.is_jobseeker():
        # Job seekers can only download their own resume
        if current_user.resume_path != filename:
            abort(403)
    else:
        abort(403)
    
    directory = os.path.dirname(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)


# ========== ADMIN ROUTES ==========
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Statistics
    total_users = User.query.count()
    total_employers = User.query.filter_by(role='employer').count()
    total_jobseekers = User.query.filter_by(role='jobseeker').count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True, is_approved=True).count()
    pending_jobs = Job.query.filter_by(is_approved=False).count()
    total_applications = Application.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_employers=total_employers,
                         total_jobseekers=total_jobseekers,
                         total_jobs=total_jobs,
                         active_jobs=active_jobs,
                         pending_jobs=pending_jobs,
                         total_applications=total_applications,
                         recent_users=recent_users,
                         recent_jobs=recent_jobs)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=app.config['USERS_PER_PAGE'], error_out=False
    )
    
    return render_template('admin/users.html', users=users, role_filter=role_filter)


@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin():
        flash('Cannot deactivate admin accounts.', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/jobs')
@login_required
@admin_required
def admin_jobs():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Job.query
    if status_filter == 'pending':
        query = query.filter_by(is_approved=False)
    elif status_filter == 'active':
        query = query.filter_by(is_active=True, is_approved=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    jobs = query.order_by(Job.posted_date.desc()).paginate(
        page=page, per_page=app.config['JOBS_PER_PAGE'], error_out=False
    )
    
    return render_template('admin/jobs.html', jobs=jobs, status_filter=status_filter)


@app.route('/admin/jobs/<int:job_id>/approve', methods=['POST'])
@login_required
@admin_required
def admin_approve_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_approved = True
    db.session.commit()
    
    flash(f'Job "{job.title}" has been approved.', 'success')
    return redirect(url_for('admin_jobs'))


@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('admin_jobs'))


@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', form=form, categories=categories)


@app.route('/admin/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    
    # Check if category has jobs
    if category.jobs.count() > 0:
        flash('Cannot delete category with existing jobs.', 'error')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully.', 'success')
    return redirect(url_for('admin_categories'))


@app.route('/admin/applications')
@login_required
@admin_required
def admin_applications():
    page = request.args.get('page', 1, type=int)
    applications = Application.query.order_by(Application.applied_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/applications.html', applications=applications)


# ========== API ROUTES ==========
@app.route('/api/jobs')
def api_get_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    category_id = request.args.get('category', 0, type=int)
    
    query = Job.query.filter(
        Job.is_active == True,
        Job.is_approved == True,
        Job.expiry_date > datetime.utcnow()
    )
    
    if search:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%')
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if category_id:
        query = query.filter(Job.category_id == category_id)
    
    jobs_page = query.order_by(Job.posted_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    jobs_data = []
    for job in jobs_page.items:
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'company': job.company.name,
            'location': job.location,
            'job_type': job.job_type,
            'salary': job.format_salary(),
            'posted_date': job.posted_date.strftime('%Y-%m-%d'),
            'category': job.category.name if job.category else None,
            'is_remote': job.is_remote
        })
    
    return jsonify({
        'jobs': jobs_data,
        'total': jobs_page.total,
        'pages': jobs_page.pages,
        'current_page': jobs_page.page
    })


@app.route('/api/categories')
def api_get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'icon': c.icon
    } for c in categories])


@app.route('/api/stats')
@login_required
@admin_required
def api_get_stats():
    return jsonify({
        'total_users': User.query.count(),
        'total_employers': User.query.filter_by(role='employer').count(),
        'total_jobseekers': User.query.filter_by(role='jobseeker').count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True, is_approved=True).count(),
        'total_applications': Application.query.count()
    })


@app.route('/api/ats-score', methods=['POST'])
@login_required
def api_ats_score():
    """Analyze resume against job description and return ATS match score"""
    try:
        resume_text = ''
        job_description = ''
        
        # Check for file upload
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                filename = file.filename.lower()
                
                if filename.endswith('.pdf'):
                    # Extract text from PDF
                    try:
                        from PyPDF2 import PdfReader
                        pdf_reader = PdfReader(io.BytesIO(file.read()))
                        resume_text = ''
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text() or ''
                    except Exception as e:
                        return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 400
                
                elif filename.endswith('.docx'):
                    # Extract text from DOCX
                    try:
                        from docx import Document
                        doc = Document(io.BytesIO(file.read()))
                        resume_text = '\n'.join([para.text for para in doc.paragraphs])
                    except Exception as e:
                        return jsonify({'error': f'Failed to read DOCX: {str(e)}'}), 400
                
                elif filename.endswith('.doc'):
                    return jsonify({'error': 'Legacy .doc format not supported. Please convert to .docx or .pdf'}), 400
                
                else:
                    return jsonify({'error': 'Unsupported file format. Please upload PDF or DOCX'}), 400
        
        # Check for text input (fallback or primary)
        if request.is_json:
            data = request.get_json()
            if not resume_text:
                resume_text = data.get('resume', '')
            job_description = data.get('description', '')
        else:
            if not resume_text:
                resume_text = request.form.get('resume', '')
            job_description = request.form.get('description', '')
        
        if not resume_text:
            return jsonify({'error': 'Please provide a resume (file upload or text)'}), 400
        if not job_description:
            return jsonify({'error': 'Please provide a job description'}), 400
        
        # Extract keywords from job description
        job_keywords = extract_keywords(job_description)
        resume_keywords = extract_keywords(resume_text)
        
        # Calculate matches
        matched = set(job_keywords) & set(resume_keywords)
        missing = set(job_keywords) - set(resume_keywords)
        
        # Calculate score
        if len(job_keywords) > 0:
            score = (len(matched) / len(job_keywords)) * 100
        else:
            score = 0
        
        return jsonify({
            'score': round(score, 1),
            'matched_keywords': sorted(list(matched)),
            'suggestions': sorted(list(missing))[:15],  # Limit to top 15 missing
            'total_job_keywords': len(job_keywords),
            'total_matched': len(matched)
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


def extract_keywords(text):
    """Extract important keywords from text"""
    # Common stop words to filter out
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'as', 'is', 'it', 'be', 'are', 'was', 'were', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they',
        'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'just', 'also', 'now', 'here', 'there', 'then', 'once', 'if', 'any',
        'about', 'after', 'before', 'above', 'below', 'between', 'into', 'through',
        'during', 'under', 'again', 'further', 'while', 'our', 'your', 'their',
        'its', 'my', 'his', 'her', 'up', 'down', 'out', 'off', 'over', 'etc',
        'able', 'work', 'working', 'experience', 'skills', 'skill', 'years', 'year',
        'including', 'include', 'role', 'position', 'job', 'company', 'team',
        'looking', 'seeking', 'required', 'requirements', 'responsibility', 'responsibilities',
        'must', 'preferred', 'strong', 'excellent', 'good', 'knowledge', 'understanding',
        'using', 'use', 'new', 'well', 'within', 'across', 'based', 'related',
        've', 'll', 're', 'd', 'm', 's', 't', 'don', 'won', 'isn', 'aren', 'wasn', 'weren',
        'haven', 'hasn', 'hadn', 'doesn', 'didn', 'wouldn', 'couldn', 'shouldn', 'ain',
    }
    
    # Convert to lowercase and extract words
    text = text.lower()
    words = re.findall(r'\b[a-z][a-z0-9+#.-]*[a-z0-9+#]\b|\b[a-z]{2,}\b', text)
    
    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) >= 2]
    
    # Return unique keywords
    return list(set(keywords))


# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ========== CREATE TABLES & SEED DATA ==========
with app.app_context():
    try:
        db.create_all()
        # Only seed if tables were just created (naive check, but safe)
        if not User.query.first():
            seed_database()
    except Exception as e:
        print(f"Database initialization error: {e}")
        # On Vercel, we might not be able to seed if unrelated errors occur, but app should still start
        pass


if __name__ == '__main__':
    app.run(debug=True)
