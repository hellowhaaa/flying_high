# views.py
from flask import (request, redirect, url_for, render_template, flash, 
                    current_app,jsonify, abort, session, make_response)
from models2 import RegisterForm, create_user, same_username, check_user_credentials
from select_data_from_mongo import (get_arrive_flight_time, get_depart_flight_time, select_insurance_amount,
                                select_user_information, select_user_insurance, select_today_depart_flight_code)
from update_data_to_mongo import update_user_insurance
import os
from pymongo import MongoClient
from functools import wraps
import jwt
from datetime import datetime, timedelta
import re


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
            # return jsonify({'message': 'Token is missing'}), 401
            return redirect(url_for('sign_up'))  
        
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



@token_required
def user_insurance(current_user):
    user_insurance = select_user_insurance(current_user)
    print("user_insurance print from route: ", user_insurance)
    return render_template('user_insurance.html', user_info_dict=user_insurance)

@token_required
def user_info(current_user):
    user_info_dict = select_user_information(current_user) # dict
    return render_template('user_info.html',user_info_dict=user_info_dict) 

@token_required
def user_notify(current_user):
    return render_template('user_notify.html')

@token_required
def user_flight(current_user):
    return render_template('user_flight.html')

def update_user():
    if request.method == "POST":
        json_data = request.get_json()
        print(json_data)
        response = {
            "status": "success",
            "data" : json_data
        }
        return jsonify(response)
    return render_template('homepage.html')

@token_required
def update_insurance(current_user):
    if request.method == "POST":
        json_data = request.get_json()
        print("json_data:" , json_data)
        print("current_user", current_user)
        insurance_company = json_data['insurance_company']
        plan = json_data["plan"]
        insured_amount = json_data["insured_amount"]
        days = json_data["days"]
        response = {
            "status": "success",
            "data": json_data
        }
        update_info = update_user_insurance(current_user,insurance_company,plan, insured_amount, days)
        print(update_info)
        print(response)
        return jsonify(response)
    return render_template('homepage.html')

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
    if flight_result is not None:
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
    if flight_result is not None:
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



@token_required
def my_insurance(current_user):
    user_insurance = select_user_insurance(current_user)
    insurance_company = user_insurance["insurance_company"]
    plan = user_insurance["plan"]
    insured_amount = user_insurance["insured_amount"]
    days = user_insurance["days"]
    insurance_content = select_insurance_amount(plan, insured_amount,insurance_company, days)
    insurance_content["insurance_company"] = insurance_company
    print("insurance_content print from route: ", insurance_content)
    return render_template('my_insurance.html', user_insurance = user_insurance, insurance_content= insurance_content)




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

def fetch_insurance_content():
    if request.method == "POST":
        selected_inconvenience_insurance = request.form.get("convenienceOption")
        plan = request.form.get("plan")
        days = request.form.get("days")
        insured_amount = request.form.get("insuredAmount")
        insurance_company = request.form.get("insuranceCompany")
        result = select_insurance_amount(plan, insured_amount,insurance_company, days)
        content = result['travel_inconvenience_insurance']['content'][0][selected_inconvenience_insurance]
        print("content------->",content)
        response = {
            'status': 'success',
            'data': {
                'pay_type': content['pay_type'],
                'price': content['price'],
                'name': content['name'],
                'count': content['count'],
                'description':content['description'],
                'explain': content['explain'],
                'necessities':content['necessities']
            }
        }
        return jsonify(response)
    return render_template("homepage.html")

def fetch_travel_insurance_content():
    if request.method == "POST":
        selected_insurance = request.form.get("travelInsuranceOption")
        plan = request.form.get("plan")
        days = request.form.get("days")
        insured_amount = request.form.get("insuredAmount")
        insurance_company = request.form.get("insuranceCompany")
        print("plan, insured_amount,insurance_company, days, selected_insurance", (plan, insured_amount,insurance_company, days, selected_insurance))
        result = select_insurance_amount(plan, insured_amount,insurance_company, days)
        content = result['travel_insurance']['content'][0][selected_insurance]
        print("content------->",content)
        necessities = content['necessities'] if 'necessities' in content and content['necessities'] else ''
        response = {
            'status': 'success',
            'data': {
                'pay_type': content['pay_type'],
                'price': content['price'],
                'name': content['name'],
                'description':content['description'],
                'necessities':necessities
            }
        }
        return jsonify(response)
    return render_template("homepage.html")

def split_alpha_numeric(s):
    parts = re.findall(r'[A-Za-z]+|\d+', s)
    return parts

# TODO: ---------        
def fetch_flight_code():
    return_code_dic = {} 
    result = select_today_depart_flight_code() 
    # print(result)
    for each in result:
        airlines = each['airline']  
        for airline in airlines:
            airline_code = airline['airline_code']
            print(airline_code)
            split_code = split_alpha_numeric(airline_code)  
            print(split_code)
            if len(split_code) == 2:  
                letter_part, number_part = split_code
                if letter_part in return_code_dic:
                    return_code_dic[letter_part].append(number_part)
                else:
                    return_code_dic[letter_part] = [number_part]

    print("dic--->", return_code_dic)
    return return_code_dic

def dashboard():  
    streamlit_url = "http://localhost:8501"
    return render_template('dashboard.html', streamlit_url=streamlit_url)

