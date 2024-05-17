import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    # Flask 
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # MongoDB
    MONGODB_URI_FLY = os.getenv('MONGODB_URI_FLY')
    
    # Gmail
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    TEST_RECIPIENTS = os.getenv('TEST_RECIPIENTS')
    
    # Google API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    