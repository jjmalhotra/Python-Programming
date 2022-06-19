import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "b'f3\x7f\xa8\x96\x91\xd6O\xb1\x906\xf0\x11\x8f\xb8\x89'"

    MONGODB_SETTINGS = { 'db' : 'ATA_Enrollment'}
    