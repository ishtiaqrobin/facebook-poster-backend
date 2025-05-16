import os
import sys

# Adjust the path to your Django project
project_root = "/home/ezbitlyc/facebook-poster-backend.ezbitly.com"
sys.path.insert(0, project_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
