# PythonAnywhere WSGI Configuration File
# Copy this content to your PythonAnywhere WSGI configuration file

import sys
import os

# Add your project directory to the path
project_home = '/home/YOUR_USERNAME/Modern-Hiring-Website'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set up the backend path
backend_path = os.path.join(project_home, 'Backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Change to the backend directory for relative imports
os.chdir(backend_path)

# Import your Flask app
from app import app as application

# PythonAnywhere will use this 'application' object
