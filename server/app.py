# app.py
from flask import Flask
from models import db
from views import register, login, success, dashboard, insurance,flight_information
import os

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv("MONGODB_URI")
}

db.init_app(app)

# 注册视图函数
app.add_url_rule('/flight_information', view_func=flight_information, methods=['GET', 'POST'])
app.add_url_rule('/insurance', view_func=insurance, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/success', view_func=success, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)