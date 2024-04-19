# views.py
from flask import request, redirect, url_for, render_template, flash, current_app
from models import User, Location
from select_data_from_mongo import get_flight_time
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




def flight_time():
    try:
        selected_airline = request.form.get('airline')
        flight_number = request.form.get('flight_number')
        selected_airline = selected_airline.split(',')
        airline_code = selected_airline[0]
        flight = airline_code + flight_number
        airline_name = selected_airline[1]
        ci_flights = get_flight_time(airline_name,flight)
        current_app.logger.info(f"Flight time retrieved for {flight}")
    except Exception:
        current_app.logger.error("Catch an exception.", exc_info=True)
    share_code_list = []
    if ci_flights:
        flight_info = ci_flights[0]
        print(flight_info)
        for airline_entry in flight_info['airline']:
            if airline_name in airline_entry:
                # 如果主航空公司的名称是这个字典的键，获取它的代码
                main_code = airline_entry[airline_name]
            else:
                # 否则，迭代这个字典的值并添加到共享代码列表
                for code in airline_entry.values():
                    share_code_list.append(code)
    print("main:",main_code)
    print("shared",share_code_list)
    
    if flight_info['status'] == '':
        flight_info['status'] = '已排定起飛時間'

    flight = {
        'main_code': main_code,
        'share_code': share_code_list,  # 确保这是一个列表
        'destination': flight_info['destination'],
        'gate': flight_info['gate'],
        'scheduled_arrive_time': flight_info['scheduled_arrive_time'],
        'actual_arrive_time': flight_info['actual_arrive_time'],
        'status': flight_info['status'],
        'terminal': flight_info['terminal']
    }
    print(flight)
    
    
    return render_template('flight_time.html', airline_name=airline_name, flight= flight)

def insurance():
    return render_template('insurance.html')


def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)
