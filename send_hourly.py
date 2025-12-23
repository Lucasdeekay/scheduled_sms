#!/usr/bin/env python
# ~/myproject/cron_send_hourly.py
import os, django, sys

# 1. point to your virtualenv Python if you want
#    (PA already activates it for scheduled tasks, so optional)
venv_python = "/home/pappycoder/venv/bin/python"
sys.executable = venv_python

# 2. set up Django
os.chdir("/home/pappycoder/scheduled_sms")  # adjust to your project path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

# 3. fire the same function the scheduler uses
from sender.views import send_due_messages
send_due_messages()