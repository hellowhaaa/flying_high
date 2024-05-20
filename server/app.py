import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask_wtf import CSRFProtect
from flask_mail import Mail
from views import *
from config import Config

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # configuration
    app.config.from_object(Config)
    
    # Secret key
    app.secret_key = app.config['SECRET_KEY']
    
    # CSRF protection, Send CSRF token with every form
    csrf = CSRFProtect(app)
    
    # Setup Mail
    setup_routes(app, csrf)
    mail_settings = app.config['MAIL_SETTINGS']
    app.config.update(mail_settings) # Update all mail_settings with all keys and values once
    mail = Mail(app)
    
    # Let all variables can be used in jinja2 template
    @app.context_processor
    def inject_user():
        access_token = request.cookies.get('access_token')
        return {'logged_in': True if access_token else False}
    
    @app.context_processor
    def inject_streamlit_url():
        return {"streamlit_url": 'https://www.flyinghigh.live/dashboard/'}
        
    # Setup logger
    if not app.debug:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        current_date = datetime.now().strftime("%Y%m%d")
        log_path = os.path.join(project_root, 'server', 'logs')
        os.makedirs(log_path, exist_ok=True)
        file_handler = RotatingFileHandler(os.path.join(log_path, f'app_{current_date}.log'), maxBytes=10240, backupCount=5)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')
        
    # Register error handlers
    error_handlers(app)
    
    # Routes
    # user 
    app.add_url_rule('/user/log_in', view_func=login, methods=['GET','POST'])
    app.add_url_rule('/user/sign_up', view_func=sign_up, methods=['GET','POST'])
    app.add_url_rule('/user/log_out', view_func=logout, methods=['GET'])
    
    app.add_url_rule('/user/insurance.html', view_func=user_insurance, methods=['GET'])
    app.add_url_rule('/user/info.html', view_func=user_info, methods=['GET'])
    app.add_url_rule('/user/notify.html', view_func=user_notify, methods=['GET'])
    app.add_url_rule('/user/flight.html', view_func=user_flight, methods=['GET'])
    
    app.add_url_rule('/user/update_user', view_func=update_user, methods=['POST'])
    app.add_url_rule('/user/update_insurance', view_func=update_insurance, methods=['POST'])
    app.add_url_rule('/user/update_flight_info', view_func=update_flight_info, methods=['POST'])
    app.add_url_rule('/user/update_notify', view_func=update_notify, methods=['POST'])

    # flight 
    app.add_url_rule('/search_flight', view_func=search_flight, methods=['GET'])
    app.add_url_rule('/arrive_flight_time', view_func=arrive_flight_time, methods=['POST','GET'])
    app.add_url_rule('/depart_flight_time', view_func=depart_flight_time, methods=['POST','GET'])
    app.add_url_rule('/fetch_depart_flight_code', view_func=fetch_depart_flight_code, methods=['GET'])
    app.add_url_rule('/fetch_arrive_flight_code', view_func=fetch_arrive_flight_code, methods=['GET'])
    app.add_url_rule('/fetch_user_depart_flight_code', view_func=fetch_user_depart_flight_code, methods=['GET'])
    app.add_url_rule('/fetch_user_arrive_flight_code', view_func=fetch_user_arrive_flight_code, methods=['GET'])

    # insurance
    app.add_url_rule('/insurance', view_func=insurance, methods=['GET', 'POST'])
    app.add_url_rule('/my_insurance', view_func=my_insurance, methods=['GET', 'POST'])
    app.add_url_rule('/fetch_insurance_amount', view_func=fetch_insurance_amount, methods=['POST'])
    app.add_url_rule('/fetch_insurance_content', view_func=fetch_insurance_content, methods=['POST'])
    app.add_url_rule('/fetch_travel_insurance_content', view_func=fetch_travel_insurance_content, methods=['POST'])

    # index
    app.add_url_rule('/', view_func=index, methods=['GET'])

    # map
    app.add_url_rule('/flight_map', view_func=flight_map, methods=['GET'])
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()