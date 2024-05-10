from flask import Flask, request
from flask_wtf import CSRFProtect
from views import (sign_up, login, logout, dashboard, insurance, search_flight, index, arrive_flight_time,
                   fetch_insurance_amount, depart_flight_time, user_insurance, user_info, update_user,
                   update_insurance, my_insurance, user_notify, fetch_insurance_content, fetch_travel_insurance_content,
                   user_flight, fetch_depart_flight_code, fetch_arrive_flight_code, update_flight_info,
                   update_notify, setup_routes, flight_map, fetch_user_arrive_flight_code,
                   fetch_user_depart_flight_code, error_handlers)
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail
from dotenv import load_dotenv


def create_app():
    env_path = os.path.join(os.getcwd(), 'server', '.env')
    load_dotenv(env_path)
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    csrf = CSRFProtect(app)
    setup_routes(app, csrf)
    # Setup Flask-Mail
    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD")
    }
    app.config.update(mail_settings)
    mail = Mail(app)
    
    @app.context_processor
    def inject_user():
        access_token = request.cookies.get('access_token')
        return {'logged_in': True if access_token else False}
    
    @app.context_processor
    def inject_streamlit_url():
        # Add the URL for Streamlit
        return {"streamlit_url": 'https://www.flyinghigh.live/dashboard/'}
        
    # Setup logger
    if not app.debug:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        log_path = os.path.join(project_root, 'server', 'logs')
        os.makedirs(log_path, exist_ok=True)
        print("log_path:", log_path)
        file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=10240, backupCount=3)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')
    # 註冊錯誤處理器
    error_handlers(app)
    # Define routes
    # user ----
    app.add_url_rule('/user/log_in', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/user/sign_up', view_func=sign_up, methods=['GET', 'POST'])
    app.add_url_rule('/user/log_out', view_func=logout, methods=['GET', 'POST'])
    
    app.add_url_rule('/user/insurance.html', view_func=user_insurance, methods=['GET', 'POST'])
    app.add_url_rule('/user/info.html', view_func=user_info, methods=['GET', 'POST'])
    app.add_url_rule('/user/notify.html', view_func=user_notify, methods=['GET', 'POST'])
    app.add_url_rule('/user/flight.html', view_func=user_flight, methods=['GET', 'POST'])
    
    app.add_url_rule('/user/update_user', view_func=update_user, methods=['POST'])
    app.add_url_rule('/user/update_insurance', view_func=update_insurance, methods=['POST'])
    app.add_url_rule('/user/update_flight_info', view_func=update_flight_info, methods=['POST'])
    app.add_url_rule('/user/update_notify', view_func=update_notify, methods=['POST'])

    # flight ---
    app.add_url_rule('/search_flight', view_func=search_flight, methods=['GET', 'POST'])
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
    app.add_url_rule('/fetch_insurance_content', view_func=fetch_insurance_content, methods=['POST','GET'])
    app.add_url_rule('/fetch_travel_insurance_content', view_func=fetch_travel_insurance_content, methods=['POST','GET'])

    # dashboard
    app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET', 'POST'])
    app.add_url_rule('/', view_func=index, methods=['GET', 'POST'])

    # map
    app.add_url_rule('/flight_map', view_func=flight_map, methods=['GET', 'POST'])
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)