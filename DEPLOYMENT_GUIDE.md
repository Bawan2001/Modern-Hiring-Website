# 🚀 PythonAnywhere Deployment Guide

This guide will help you deploy the Modern Hiring Website to PythonAnywhere (FREE, no credit card required).

---

## Step 1: Create PythonAnywhere Account

1. Go to [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **"Pricing & signup"** → Select **"Create a Beginner account"** (FREE)
3. Create your account (remember your username!)

---

## Step 2: Clone Repository on PythonAnywhere

1. Once logged in, click **"Consoles"** in the top menu
2. Under "Start a new console", click **"Bash"**
3. In the Bash console, run:

```bash
# Clone the repository
git clone https://github.com/Bawan2001/Modern-Hiring-Website.git

# Go into the project folder
cd Modern-Hiring-Website

# Install dependencies
pip3.9 install --user -r requirements.txt
```

---

## Step 3: Create the Web App

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Click **"Next"** (accept the free subdomain: `YOUR_USERNAME.pythonanywhere.com`)
4. Select **"Manual configuration"** (NOT Flask!)
5. Select **Python 3.9**
6. Click **"Next"** to create the web app

---

## Step 4: Configure WSGI File

1. In the Web tab, scroll to **"Code"** section
2. Click on the **WSGI configuration file** link (something like `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
3. **Delete ALL existing content** and replace with:

```python
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
```

4. **IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username
5. Click **"Save"**

---

## Step 5: Configure Static Files

1. In the Web tab, scroll to **"Static files"** section
2. Click **"Enter URL"** and add:
   - **URL:** `/static/`
   - **Directory:** `/home/YOUR_USERNAME/Modern-Hiring-Website/Frontend/static`

3. Click the checkmark to save

---

## Step 6: Create uploads folder (for resume uploads)

1. Go to **"Files"** tab
2. Navigate to: `/home/YOUR_USERNAME/Modern-Hiring-Website/Backend/`
3. Create a new directory called `uploads`

Or in Bash console:
```bash
mkdir -p ~/Modern-Hiring-Website/Backend/uploads
```

---

## Step 7: Reload the Web App

1. Go back to **"Web"** tab
2. Click the big green **"Reload"** button at the top
3. Wait for it to complete

---

## Step 8: Test Your Deployment!

1. Click on your website URL: `https://YOUR_USERNAME.pythonanywhere.com`
2. Your site should be live! 🎉

---

## (Optional) Step 9: Set Up GitHub Actions Auto-Deploy

To enable automatic deployment when you push to `main`:

### 9.1 Get PythonAnywhere API Token
1. Go to PythonAnywhere → **"Account"** → **"API Token"**
2. Click **"Create a new API token"**
3. Copy the token

### 9.2 Add GitHub Secrets
1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - **`PA_USERNAME`**: Your PythonAnywhere username
   - **`PA_API_TOKEN`**: The API token you copied

Now when you merge to `main`, GitHub Actions will automatically update your deployed site!

---

## Demo Login Credentials

After deployment, you can test with these accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@jobsphere.com | admin123 |
| Employer | employer@demo.com | employer123 |
| Job Seeker | user@example.com | user123 |

---

## Troubleshooting

### Error: "Something went wrong"
- Check the **Error log** in PythonAnywhere Web tab
- Make sure all paths use your correct username

### Error: "Module not found"
- Run `pip3.9 install --user -r requirements.txt` again in Bash console

### Static files not loading
- Check the Static files configuration in Web tab
- Make sure the path is correct

### Need to update code?
In PythonAnywhere Bash console:
```bash
cd ~/Modern-Hiring-Website
git pull origin main
```
Then click **"Reload"** in the Web tab.

---

## Questions?

If you have any issues, check:
1. PythonAnywhere Error Log (Web tab)
2. PythonAnywhere Help: https://help.pythonanywhere.com/

Good luck! 🎓
