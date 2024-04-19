# views.py
from flask import request, redirect, url_for, render_template, flash, current_app
from models import User, Location
from select_data_from_mongo import get_flight_time


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
    selected_airline = request.form.get('airline')
    flight_number = request.form.get('flight_number')
    selected_airline = selected_airline.split(',')
    airline_code = selected_airline[0]
    flight = airline_code + flight_number
    airline_name = selected_airline[1]
    ci_flights = get_flight_time(airline_name,flight)
    
    print('ci_flight_', ci_flights)
    for i in ci_flights:
        print(i)
    
    
    
    return render_template('flight_time.html', airline_name=airline_name, flight= flight)

def insurance():
    return render_template('insurance.html')


def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)
