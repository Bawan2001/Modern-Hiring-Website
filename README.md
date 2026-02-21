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
- **WSGI Server**: Gunicorn (Production / Docker)
- **Containerisation**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Vercel Cloud Platform / Docker

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
- **Docker Containerisation**: Created `Dockerfile`, `docker-compose.yml`, and `.dockerignore` for container-based deployment.
- **Merge Management**: Handled merge conflicts and PR reviews.

### J.W.A.Indumini Adarshya
- **Full-Stack Development**: Implemented core Backend API and Frontend UI.
- **Authentication**: Developed secure Login and Registration systems.
- **Business Logic**: Wrote core logic for Job and Application handling, Job posting and job listing features.
- **ATS Implementation**: Developed the resume keyword matching algorithm.

---

## Setup Instructions

### Option 1: Run with Docker (Recommended)

This is the easiest way to get the application running. The entire stack is containerised and can be started with a single command.

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+ — included with Docker Desktop)

#### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bawan2001/Modern-Hiring-Website.git
   cd Modern-Hiring-Website
   ```

2. **Build and start the container**
   ```bash
   docker compose up --build
   ```
   The application will be available at **http://localhost:5000**.

3. **Run in detached (background) mode**
   ```bash
   docker compose up --build -d
   ```

4. **Check container health**
   ```bash
   docker compose ps
   ```
   The `STATUS` column should show `healthy` after approximately 30 seconds.

5. **View application logs**
   ```bash
   docker compose logs -f web
   ```

6. **Stop the application**
   ```bash
   docker compose down
   ```

7. **Stop and remove all data (database + uploads)**
   ```bash
   docker compose down -v
   ```

#### Environment Variables

The following environment variables can be configured in a `.env` file or passed directly:

| Variable       | Description                         | Default                               |
|----------------|-------------------------------------|---------------------------------------|
| `SECRET_KEY`   | Flask secret key for session security | `jobsphere-docker-secret-key-2026` |
| `FLASK_ENV`    | Application environment (`production` / `development`) | `production` |
| `PORT`         | Port the application listens on     | `5000`                                |
| `DATABASE_URL` | External database URL (optional)    | SQLite (file-based)                   |

Example `.env` file:
```env
SECRET_KEY=my-super-secure-key
FLASK_ENV=production
PORT=5000
```

#### Docker Architecture

```
┌─────────────────────────────────────────────────┐
│              Docker Compose Stack                │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │           web (jobsphere-web)            │    │
│  │  ┌────────────┐   ┌─────────────────┐    │    │
│  │  │  Gunicorn   │──▶│   Flask App     │    │    │
│  │  │  (4 workers)│   │  (app.py)       │    │    │
│  │  └────────────┘   └─────────────────┘    │    │
│  │        │                    │             │    │
│  │   Port 5000           Health Check       │    │
│  └────────┼────────────────────┼────────────┘    │
│           │                    │                 │
│  ┌────────▼────────┐  ┌───────▼──────────┐      │
│  │   app-data      │  │   app-uploads    │      │
│  │ (SQLite Volume) │  │ (Uploads Volume) │      │
│  └─────────────────┘  └──────────────────┘      │
│                                                  │
│        Network: jobsphere-net (bridge)           │
└─────────────────────────────────────────────────┘
```

#### Key Docker Files

| File                 | Purpose                                                        |
|----------------------|----------------------------------------------------------------|
| `Dockerfile`         | Defines how the application image is built (Python 3.11, Gunicorn, non-root user, health check) |
| `docker-compose.yml` | Orchestrates the application service with volumes, networking, and environment configuration    |
| `.dockerignore`      | Excludes unnecessary files from the build context for security and smaller images              |

---

### Option 2: Run Locally (Without Docker)

#### Prerequisites
- Python 3.9 or higher
- Git installed
- Vercel CLI (optional for local deployment testing)

#### Installation
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

---

## Default Demo Accounts

| Role       | Email                | Password      |
|------------|----------------------|---------------|
| Admin      | admin@jobsphere.com  | admin123      |
| Employer   | employer@demo.com    | employer123   |
| Job Seeker | user@example.com     | user123       |

## Deployment Process
Our deployment is fully automated using GitHub Actions:
- **Continuous Integration (CI)**: On every push to `develop` or `feature/*`, the CI pipeline (`ci.yml`) runs to install dependencies and lint the code using `flake8`.
- **Continuous Deployment (CD)**: When code is merged into `main`, the CD pipeline (`deploy.yml`) handles the deployment to Vercel production environment automatically.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `port is already allocated` | Another process is using port 5000 | Run with a different host port: `PORT=5001 docker compose up` |
| Container shows `unhealthy` | App failed to start or crashed | Check logs: `docker compose logs web` and look for Python errors |
| Data missing after rebuild | Used `docker compose down -v` | The `-v` flag removes volumes. Use `docker compose down` (without `-v`) to preserve data |
| `Permission denied` on uploads/ or data/ | Volume ownership mismatch (Linux) | Run `docker compose down -v && docker compose up --build` to recreate volumes with correct ownership |
| Image build fails at `pip install` | Network issue or dependency conflict | Run `docker compose build --no-cache` to retry from scratch |
| Container keeps restarting | Application crash loop | Run `docker compose logs --tail=50 web` to identify the error, then fix and rebuild |

## Challenges Faced
- **Static File Serving**: Resolving path issues between Flask's default static folder and Vercel's serverless structure.
- **Merge Conflicts**: Coordinating simultaneous edits to the `app.py` file during the integration phase.
- **Environment Variables**: Managing secure storage of configuration secrets across local and cloud environments.
- **Docker Volume Persistence**: Ensuring that the SQLite database and user-uploaded files persist across container restarts using named Docker volumes.

