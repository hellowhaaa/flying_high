import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    # Flask 
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # MongoDB
    MONGODB_URI_FLY = os.getenv('MONGODB_URI_FLY')
    MONGODB_DATABASE_FLY = os.getenv('MONGODB_DATABASE_FLY')
    
    # Gmail
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    TEST_RECIPIENTS = os.getenv('TEST_RECIPIENTS')
    MAIL_SETTINGS = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD")
    }
    
    # Google API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    
class TestingConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY')
    TESTING = True
    DATABASE_URI = os.getenv("MONGODB_URI_TEST")
    WTF_CSRF_ENABLED = False
    MONGODB_DATABASE_TEST = os.getenv("MONGODB_DATABASE_TEST")
    