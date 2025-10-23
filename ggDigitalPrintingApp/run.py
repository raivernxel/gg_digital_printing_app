import os
import sys
import subprocess
import webbrowser
import time

# Set the correct Django project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)  # Ensure Django finds the project

# Set the Django settings module explicitly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggDigitalPrintingApp.settings")

# Run the Django development server
server = subprocess.Popen([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])

# Wait for Django to start
time.sleep(3)

# Open in the default web browser
webbrowser.open("http://127.0.0.1:8000/")

# Keep the server running
server.wait()
