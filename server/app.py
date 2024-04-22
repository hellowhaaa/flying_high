# app.py
from flask import Flask
# from models2 import db
from views import (sign_up, login, logout,success, dashboard, insurance,search_flight,
                    index,arrive_flight_time,fetch_insurance_amount)
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

env_path = os.path.join(os.getcwd(), 'server', '.env')
log_path = os.path.join(os.getcwd(), 'server', 'logs')
load_dotenv(env_path)
app = Flask(__name__)

# Logger 配置
if not app.debug:
    file_handler = RotatingFileHandler(log_path+'/app.log', maxBytes=10240, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info(' App startup')


app.add_url_rule('/search_flight', view_func=search_flight, methods=['GET', 'POST'])
app.add_url_rule('/insurance', view_func=insurance, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET', 'POST'])
app.add_url_rule('/user/log_in', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/success', view_func=success, methods=['GET', 'POST'])
app.add_url_rule('/user/sign_up', view_func=sign_up, methods=['GET', 'POST'])
app.add_url_rule('/user/log_out', view_func=logout, methods=['GET', 'POST'])
app.add_url_rule('/arrive_flight_time', view_func=arrive_flight_time, methods=['POST','GET'])
app.add_url_rule('/fetch_insurance_amount', view_func=fetch_insurance_amount, methods=['POST','GET'])
app.add_url_rule('/', view_func=index, methods=['GET', 'POST'])
if __name__ == '__main__':
    app.secret_key = os.getenv("SECRET_KEY")
    app.run(debug=True)