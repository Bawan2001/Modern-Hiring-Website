# Modern Hiring Website

![CI Pipeline](https://github.com/Bawan2001/Modern-Hiring-Website/workflows/CI%20Pipeline/badge.svg)
![Deploy to Production](https://github.com/Bawan2001/Modern-Hiring-Website/workflows/Deploy%20to%20Production/badge.svg)

## Group Information
- **Student 1:** D.M.B.R.Dissanayaka - ITBIN-2313-0029- Role: DevOps Engineer
- **Student 2:** J.W.A.Indumini Adarshya - ITBIN-2313-0004 - Role: Full-Stack Developer

## Project Description
A comprehensive job portal application designed to connect job seekers with employers. The platform facilitates the entire hiring process, from job posting and application management to resume scoring using an integrated Applicant Tracking System (ATS).

## Live Deployment
**Live URL:** https://modern-hiring-website.vercel.app/

## Technologies Used
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite (Development)
- **CI/CD**: GitHub Actions
- **Deployment**: Vercel Cloud Platform

## Features
- **User Roles**: Distinct portals for Job Seekers, Employers, and Administrators.
- **Job Management**: Complete workflow for posting, editing, and managing job listings.
- **Application Tracking System (ATS)**: Automated resume parsing and keyword matching score.
- **Application Dashboard**: Real-time status tracking for applied jobs.
- **Responsive Design**: fully optimized for mobile and desktop devices.

## Branch Strategy
We strictly followed a professional Git workflow:
- `main` - **Production Branch**: Contains stable, deployable code. Protected and strictly managed via Pull Requests.
- `develop` - **Integration Branch**: Serves as the main development branch where all features are merged before release.
- `feature/*` - **Feature Branches**: Isolated branches for each specific feature (e.g., `feature/auth-system`, `feature/ui-redesign`) to prevent conflicts.
- **Merge Logic**: Feature branches are merged into `develop` via PRs, and `develop` is merged into `main` for deployment.

## Individual Contributions
### D.M.B.R.Dissanayaka
- **Repository Initialization**: Set up the project structure and git configuration.
- **CI/CD Pipeline**: Configured `.github/workflows/ci.yml` for automated testing and linting.
- **Deployment**: Managed Vercel integration and `deploy.yml` workflow.
- **Merge Management**: Handled merge conflicts and PR reviews.

### J.W.A.Indumini Adarshya
- **Full-Stack Development**: Implemented core Backend API and Frontend UI.
- **Authentication**: Developed secure Login and Registration systems.
- **Business Logic**: Wrote core logic for Job and Application handling, Job posting and job listing features.
- **ATS Implementation**: Developed the resume keyword matching algorithm.







## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Git installed
- Vercel CLI (optional for local deployment testing)

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/Bawan2001/Modern-Hiring-Website.git
   cd Modern-Hiring-Website
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```
   The app will run at `http://127.0.0.1:5000`

### Deployment Process
Our deployment is fully automated using GitHub Actions:
- **Continuous Integration (CI)**: On every push to `develop` or `feature/*`, the CI pipeline (`ci.yml`) runs to install dependencies and lint the code using `flake8`.
- **Continuous Deployment (CD)**: When code is merged into `main`, the CD pipeline (`deploy.yml`) handles the deployment to Vercel production environment automatically.

# Challenges Faced
- **Static File Serving**: Resolving path issues between Flask's default static folder and Vercel's serverless structure.
- **Merge Conflicts**: Coordinating simultaneous edits to the `app.py` file during the integration phase.
- **Environment Variables**: Managing secure storage of configuration secrets across local and cloud environments.
