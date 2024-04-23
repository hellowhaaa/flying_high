# app.py
from flask import Flask, request
# from models2 import db
from views import (sign_up, login, logout, dashboard, insurance,search_flight,
                    index,arrive_flight_time,fetch_insurance_amount, depart_flight_time,
                    user_insurance, user_info)
import logging
from logging.handlers import RotatingFileHandler
import os

from dotenv import load_dotenv

def create_app():
    env_path = os.path.join(os.getcwd(), 'server', '.env')
    load_dotenv(env_path)
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    
    @app.context_processor
    def inject_user():
        access_token = request.cookies.get('access_token')
        return {'logged_in': True if access_token else False}
    
    # Setup logger
    if not app.debug:
        log_path = os.path.join(os.getcwd(), 'server', 'logs')
        # Ensure the directory exists
        os.makedirs(log_path, exist_ok=True)
        # Initialize logging handler
        file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=10240, backupCount=3)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')
        
    # Define routes
    # user ----
    app.add_url_rule('/user/log_in', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/user/sign_up', view_func=sign_up, methods=['GET', 'POST'])
    app.add_url_rule('/user/log_out', view_func=logout, methods=['GET', 'POST'])
    app.add_url_rule('/user/insurance.html', view_func=user_insurance, methods=['GET', 'POST'])
    app.add_url_rule('/user/info.html', view_func=user_info, methods=['GET', 'POST'])
    
    # flight ---
    app.add_url_rule('/search_flight', view_func=search_flight, methods=['GET', 'POST'])
    app.add_url_rule('/arrive_flight_time', view_func=arrive_flight_time, methods=['POST','GET'])
    app.add_url_rule('/depart_flight_time', view_func=depart_flight_time, methods=['POST','GET'])
    
    # insurance
    app.add_url_rule('/insurance', view_func=insurance, methods=['GET', 'POST'])
    app.add_url_rule('/fetch_insurance_amount', view_func=fetch_insurance_amount, methods=['POST','GET'])
    
    # dashboard
    app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET', 'POST'])
    app.add_url_rule('/', view_func=index, methods=['GET', 'POST'])
    
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)