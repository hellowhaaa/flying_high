# views.py
from flask import request, redirect, url_for, render_template, flash, current_app
from models import User, Location



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


def flight_information():
    return render_template('flight_info.html')



def insurance():
    return render_template('insurance.html')


def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)
