import os
from flogask.gunicorn import gunicorn_access_log_format, gunicorn_logconfig_dict

timeout = 30
workers = 1
preload = True
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:5000")

access_log_format = gunicorn_access_log_format
logconfig_dict = gunicorn_logconfig_dict