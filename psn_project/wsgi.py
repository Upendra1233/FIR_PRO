import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
project_home = '/home/danlawtechu/FIR_PRO'
if project_home not in sys.path:
    sys.path.append(project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psn_project.settings')
application = get_wsgi_application()
