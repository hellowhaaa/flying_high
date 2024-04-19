# views.py
from flask import request, redirect, url_for, render_template, flash, current_app
from models import User, Location
from select_data_from_mongo import get_arrive_flight_time
import logging


def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(username=username, email=email, password=password)
        user.hash_password()
        user.save()
        current_app.logger.info(f"User saved: {user.username}")
        flash('Registration successful, please login.', 'success')
        return redirect(url_for('login'))
    locations = Location.objects.all()
    return render_template('register.html', locations=locations)

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.objects(username=username).first()
        if user and user.check_password(password):
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))  # Assume there is a profile view
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

def success():
    return '登录成功!'

def index():
    return render_template('homepage.html')


def search_flight():
    return render_template('search_flight.html')



def arrive_flight_time():
    try:
        if request.method == 'POST':
            airline_code = request.form.get('airline')
            flight_number = request.form.get('flight_number')
            flight = airline_code + flight_number
        if request.method == 'GET':
            flight = airline_code + flight_number
        flight_result = get_arrive_flight_time(flight)
        current_app.logger.info(f"Flight time retrieved for {flight_result}")
    except Exception:
        current_app.logger.error("Catch an exception.", exc_info=True)
    share_code_list = []
    if flight_result:
        for each_air in flight_result['airline']:
            if each_air['airline_code'] == flight:
                main_code = flight
            else:
                share_code_list.append(each_air['airline_code'])
    print("main:",main_code)
    print("shared",share_code_list)
    if flight_result['status'] == '':
        flight_result['status'] = '已排定起飛時間'
    flight = {
        'main_code': main_code,
        'share_code': share_code_list, 
        'destination': flight_result['destination'],
        'gate': flight_result['gate'],
        'scheduled_arrive_time': flight_result['scheduled_arrive_time'],
        'actual_arrive_time': flight_result['actual_arrive_time'],
        'status': flight_result['status'],
        'terminal': flight_result['terminal']
    }
    print(flight)
    return render_template('arrive_flight_time.html',flight= flight)

def insurance():
    return render_template('insurance.html')


def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)
