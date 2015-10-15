from flask import Flask

import os

app = Flask(__name__)

app.config.from_object('default_settings')
if os.getenv('CLEANSWEEP-SMS_SETTINGS'):
    app.config.from_envvar('CLEANSWEEP-SMS_SETTINGS')

from app import views
