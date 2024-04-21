# app.py
from flask import Flask
from models import db
from views import (register, login, success, dashboard, insurance,search_flight,
                    index,arrive_flight_time,fetch_insurance_amount)
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv


env_path = os.path.join(os.getcwd(), 'server', '.env')
log_path = os.path.join(os.getcwd(), 'server', 'logs')

# 然后使用这个路径来加载 .env 文件
load_dotenv(env_path)
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv("MONGODB_URI_FLY"),
    "db": "flying_high"
}
db.init_app(app)

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
    
# app.logger.info("env_path: " + env_path)
# app.logger.info("log_path: " + log_path)
app.logger.info(app.config['MONGODB_SETTINGS'])

app.add_url_rule('/search_flight', view_func=search_flight, methods=['GET', 'POST'])
app.add_url_rule('/insurance', view_func=insurance, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/success', view_func=success, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/arrive_flight_time', view_func=arrive_flight_time, methods=['POST','GET'])
app.add_url_rule('/fetch_insurance_amount', view_func=fetch_insurance_amount, methods=['POST','GET'])
app.add_url_rule('/', view_func=index, methods=['GET', 'POST'])
if __name__ == '__main__':
    app.secret_key = os.getenv("SE  RET_KEY")
    app.run(debug=True)