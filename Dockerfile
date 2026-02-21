# =============================================================================
# Dockerfile — Modern Hiring Website (JobSphere)
# =============================================================================
# This Dockerfile packages the Flask-based job portal into a production-ready
# container image.  Design decisions are annotated inline.
# =============================================================================

# ---------- Stage 1: Base image ----------
# We choose python:3.11-slim over the full python image because it strips out
# compilers, man pages, and documentation, reducing the final image size by
# ~600 MB.  "slim" still includes the C library needed to build wheels for
# packages like psycopg2-binary and Werkzeug's C speedups.
FROM python:3.11-slim

# ---------- Metadata ----------
# Labels help identify the image in registries and tooling.
LABEL maintainer="D.M.B.R.Dissanayaka & J.W.A.Indumini Adarshya"
LABEL description="JobSphere — Modern Hiring Website containerised with Flask & Gunicorn"
LABEL version="2.0"

# ---------- Build arguments & environment ----------
# PYTHONDONTWRITEBYTECODE  – prevents .pyc files inside the container (cleaner)
# PYTHONUNBUFFERED         – ensures logs appear in real-time in `docker logs`
# FLASK_ENV                – can be overridden at runtime via docker-compose
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# ---------- System-level dependencies ----------
# curl is required by the HEALTHCHECK instruction later.
# We clean up the apt cache in the same RUN layer to avoid inflating image size.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# ---------- Working directory ----------
# All subsequent commands run relative to /app.
WORKDIR /app

# ---------- Install Python dependencies FIRST ----------
# Copying requirements.txt separately from the rest of the source code means
# Docker can cache the expensive "pip install" layer.  As long as
# requirements.txt doesn't change, rebuilds skip this step entirely.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- Copy application source ----------
# This layer is invalidated on every code change, but the pip layer above
# remains cached, keeping rebuilds fast.
COPY . .

# ---------- Create directories for runtime data ----------
# uploads/  – user-uploaded resumes and company logos
# data/     – will hold the SQLite database when volume-mounted
RUN mkdir -p uploads data

# ---------- Non-root user (Principle of Least Privilege) ----------
# Running as root inside a container is a security anti-pattern.  We create a
# dedicated "appuser" with no login shell and switch to it.  The application
# directories are owned by this user so it can write to uploads/ and data/.
RUN groupadd --system appuser && \
    useradd --system --gid appuser --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

# ---------- Expose the application port ----------
# EXPOSE is documentation; the actual port mapping happens in docker-compose.
EXPOSE ${PORT}

# ---------- Health check ----------
# Docker (and orchestrators like Swarm / ECS) will probe this endpoint every
# 30 seconds.  If three consecutive checks fail the container is marked
# "unhealthy", enabling automatic restarts via the restart policy.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# ---------- Start the application ----------
# Gunicorn is a production-grade WSGI server.  We bind to 0.0.0.0 so the
# container is reachable from the host network.  Four workers handle
# concurrent requests; adjust based on available CPU cores.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--preload", "app:app"]
