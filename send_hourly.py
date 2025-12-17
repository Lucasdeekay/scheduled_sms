#!/usr/bin/env python
# ~/myproject/cron_send_hourly.py
import os, django, sys

# 1. point to your virtualenv Python if you want
#    (PA already activates it for scheduled tasks, so optional)
venv_python = "/home/<youruser>/.virtualenvs/<venv-name>/bin/python"
sys.executable = venv_python

# 2. set up Django
os.chdir("/home/<youruser>/myproject")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_project.settings")
django.setup()

# 3. fire the same function the scheduler uses
from sender.views import send_due_messages
send_due_messages()