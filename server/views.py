# views.py
from flask import (request, redirect, url_for, render_template, flash, 
                    current_app,jsonify, abort, session, make_response)
from models2 import RegisterForm, create_user, same_username, check_user_credentials
from select_data_from_mongo import get_arrive_flight_time, get_depart_flight_time, select_insurance_amount
import os
from pymongo import MongoClient
from functools import wraps
import jwt
from datetime import datetime, timedelta

def encode_auth_token(username):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),  # Token的過期時間
            'iat': datetime.utcnow(),  # Token的發行時間
            # 'sub': user_id,  # 訂閱識別
            'username': username  # 使用者名稱
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 確認是否有 token
        if 'Authorization' in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        # If not found, check for token in cookies
        elif 'access_token' in request.cookies:
            token = request.cookies.get('access_token').split(" ")[1]
        print("token:", token)
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # 確認是否為有效的 token
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            current_user = data['username']
            print("current_user:", current_user)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated





def sign_up():
    # Mongodb Init
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    collection = client['flying_high']['user']
    # Form Init
    form = RegisterForm(request.form)
    if request.method == 'POST':
        print("POST request received")
        if form.validate():
            print("Form validated")
            username = form.username.data
            if same_username(collection, username):
                print('same user!!!!')
                flash('Username already exists')
                return redirect(url_for('sign_up'))
            email = form.email.data
            address = form.address.data
            password = form.password.data
            form.set_password(password)  # Hashes the password and stores it in the form
            user = create_user(username, form.password_hash, email, address)
            try:
                collection.insert_one(user)
                current_app.logger.info(f"User saved: {user['username']}")
            except Exception as e:
                current_app.logger.error(f"Error saving user: {e}", exc_info=True)
                
            token = encode_auth_token(username)
            # Storing the token in session or cookie
            print("token:", token)
            response = make_response(redirect(url_for('search_flight')))
            response.set_cookie('access_token', f'Bearer {token}')
            # Redirect to homepage after successful login
            flash('You have been logged in!', 'success')
            return response
        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    current_app.logger.error(f"Error in {fieldName}: {err}")
    return render_template('sign_up.html', form=form)



def login():
    if request.method == 'POST':
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        collection = client['flying_high']['user']
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        user = check_user_credentials(collection,username, password)
        print("user-->", user)
        if user:
            # user_id_str = str(user['_id'])
            token = encode_auth_token(username)
            # Storing the token in session or cookie
            print("token:", token)
            response = make_response(redirect(url_for('search_flight')))
            response.set_cookie('access_token', f'Bearer {token}')
            flash('You have been logged in!', 'success')
            return response
        else:
            flash('Username or Password is wrong', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

def logout():
    response = make_response(redirect(url_for('search_flight')))
    response.delete_cookie("access_token", path='/')
    flash('You have been logged out.', 'success')
    return response

# TODO: ---------

def user_insurance():
    return render_template('user_insurance.html')

@token_required
def user_info(current_user):
    # 若 token 存在 direct到 user_info.html 的頁面, 
    
    
    
    # 若 token 不存在 則 導向 sign in 頁面

    return render_template('user_info.html')



def index():
    return render_template('homepage.html')


def search_flight():
    return render_template('search_flight.html')



def depart_flight_time():
    flight_result = None
    try:
        airline_code = request.form.get('airline') if request.method == 'POST' else request.args.get('airline_code')
        flight_number = request.form.get('flight_number') if request.method == 'POST' else request.args.get('flight_number')
        flight = airline_code + flight_number
        print(flight)
        flight_result = get_depart_flight_time(flight)
        print(flight_result)
        current_app.logger.info(f"Flight time retrieved for {flight_result}")
    except Exception:
        current_app.logger.error("Catch an exception.", exc_info=True)
    share_code_list = []
    if flight_result:
        for each_air in flight_result['airline']:
            if each_air['airline_code'] == flight:
                main_code = flight
                airline_name = each_air['airline_name']
            else:
                share_code_list.append(each_air['airline_code'])
        print("main:",main_code)
        print("shared",share_code_list)
        if flight_result['status'] == '':
            flight_result['status'] = '已排定起飛時間'
        flight = {
            "airline_name":airline_name,
            'main_code': main_code,
            'share_code': share_code_list, 
            'destination': flight_result['destination'],
            'gate': flight_result['gate'],
            'scheduled_depart_time': flight_result['scheduled_depart_time'],
            'actual_depart_time': flight_result['actual_depart_time'],
            'status': flight_result['status'],
            'terminal': flight_result['terminal']
        }
        print(flight)
        return render_template('flight_time.html',flight= flight)
    else:
        flash('No flight found. Please search another flight.', 'alert-danger')
        return redirect(url_for('search_flight'))

def arrive_flight_time():
    flight_result = None
    try:
        airline_code = request.form.get('airline') if request.method == 'POST' else request.args.get('airline_code')
        flight_number = request.form.get('flight_number') if request.method == 'POST' else request.args.get('flight_number')
        flight = airline_code + flight_number
        print(flight)
        flight_result = get_arrive_flight_time(flight)
        print(flight_result)
        current_app.logger.info(f"Flight time retrieved for {flight_result}")
    except Exception:
        current_app.logger.error("Catch an exception.", exc_info=True)
    share_code_list = []
    if flight_result:
        for each_air in flight_result['airline']:
            if each_air['airline_code'] == flight:
                main_code = flight
                airline_name = each_air['airline_name']
            else:
                share_code_list.append(each_air['airline_code'])
        print("main:",main_code)
        print("shared",share_code_list)
        if flight_result['status'] == '':
            flight_result['status'] = '已排定起飛時間'
        flight = {
            "airline_name":airline_name,
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
        return render_template('flight_time.html',flight= flight)
    else:
        flash('No flight found. Please search another flight.', 'alert-danger')
        return redirect(url_for('search_flight'))




def insurance():
    return render_template('insurance.html')


def fetch_insurance_amount():
    try:
        insurance_company = request.form.get('insuranceCompany')
        plan = request.form.get('plan')  
        insurance_amount = request.form.get('insuranceAmount')
        insurance_days = request.form.get('insuranceDays')
        current_app.logger.info(f"get insurance information!")
        print(insurance_company, plan, insurance_amount, insurance_days)
    except Exception as e:
        current_app.logger.error(f"Catch an exception. + {e}", exc_info=True)
    result = select_insurance_amount(plan, insurance_amount,insurance_company, insurance_days)
    print(result)
    if result:
        price = result['insurance_premium']['price']
    else:
        price = '不在試算範圍內, 請重新輸入'
        print('價格:',price)
        response = {
                'status': 'success',
                'data': {
                    'insurance_price': price
                }
            }
        return jsonify(response)
        

def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)
