# views.py
from flask import (request, redirect, url_for, render_template, flash, 
                    current_app,jsonify, abort, make_response)
from models import RegisterForm, create_user, same_username, check_user_credentials
from select_data_from_mongo import *
from update_data_to_mongo import *
import os
from pymongo import MongoClient
from functools import wraps
import jwt
from datetime import datetime, timedelta
import re
from flask_mail import Message
import pytz


def error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500


def encode_auth_token(username):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time
            'iat': datetime.utcnow(),  # Token issued at
            'username': username  
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        current_app.logger.error(f"Error encoding token: {e}", exc_info=True)
        return e

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers: # check for token in headers
            token = request.headers["Authorization"].split(" ")[1]
        elif 'access_token' in request.cookies: # If not found, check for token in cookies
            token = request.cookies.get('access_token').split(" ")[1]
        current_app.logger.info(f"Token: {token}")
        if not token: # Token is missing
            return redirect(url_for('sign_up'))  
        
        try: # check if token is valid
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            current_user = data['username']
            current_app.logger.info(f"Current user: {current_user}")
        except jwt.ExpiredSignatureError:
            return redirect(url_for('sign_up'))
        except jwt.InvalidTokenError:
            return redirect(url_for('sign_up'))
        return f(current_user, *args, **kwargs)
    return decorated


def sign_up():
    try:
        mongo_client = MongoClient(os.getenv("MONGODB_URI_FLY"))
        db = mongo_client['flying_high']
        users_collection = db['user']
        form = RegisterForm()
        if request.method == 'POST':
            current_app.logger.info("Sign up post request received")
            if form.validate():
                username = form.username.data
                if same_username(users_collection, username):
                    flash('Username already exists')
                    return redirect(url_for('sign_up'))
                email = form.email.data
                address = form.address.data
                password = form.password.data
                user = create_user(username, password, email, address)  # 使用哈希密碼
                try:
                    # 將新用戶插入 MongoDB
                    users_collection.insert_one(user)
                    current_app.logger.info(f"User saved: {user['username']}")
                except Exception as e:
                    current_app.logger.error(f"Error saving user: {e}", exc_info=True)
                    flash('An error occurred while saving the user. Please try again.', 'danger')
                    return redirect(url_for('sign_up'))
                
                # 設置訪問令牌
                token = encode_auth_token(username)
                response = make_response(redirect(url_for('search_flight')))
                response.set_cookie('access_token', f'Bearer {token}', path='/')
                flash('You have been logged in!', 'success')
                return response
            else:
                for fieldName, errorMessages in form.errors.items():
                    for err in errorMessages:
                        current_app.logger.error(f"Error in {fieldName}: {err}")
                flash('Please correct the errors in the form.', 'danger')
        return render_template('sign_up.html', form=form)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)
    


def login():
    try:
        mongo_client = MongoClient(os.getenv("MONGODB_URI_FLY"))
        db = mongo_client['flying_high']
        users_collection = db['user']
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = check_user_credentials(users_collection, username, password)
            if user:
                current_app.logger.info(f"User Logged In: {user}")
                token = encode_auth_token(username)
                response = make_response(redirect(url_for('search_flight')))
                response.set_cookie('access_token', f'Bearer {token}', path='/')
                flash('You have been logged in!', 'success')
                return response
            else:
                flash('Username or Password is wrong', 'danger')
                return redirect(url_for('login'))
        return render_template('login.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)
    

def logout():
    try:
        response = make_response(redirect(url_for('search_flight')))
        response.delete_cookie("access_token", path='/')
        flash('You have been logged out.', 'success')
        return response
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)
    


@token_required
def user_insurance(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        current_app.logger.info(f"Current User: {current_user}")
        user_insurance = select_user_insurance(current_user, logger=current_app.logger)
        return render_template('user_insurance.html', user_info_dict=user_insurance)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)

@token_required
def user_info(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        current_app.logger.info(f"Current User: {current_user}")
        user_info_dict = select_user_information(current_user, logger=current_app.logger) # dict
        return render_template('user_info.html',user_info_dict=user_info_dict)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)

@token_required
def user_notify(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        current_app.logger.info(f"Current User: {current_user}")
        user_info_dict = select_user_notify(current_user, logger=current_app.logger)
        return render_template('user_notify.html',user_info_dict = user_info_dict)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


@token_required
def user_flight(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        current_app.logger.info(f"Current User: {current_user}")
        
        user_info_dict = select_user_flight(current_user, logger=current_app.logger)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        
        depart_taiwan_date = user_info_dict['depart_taiwan_date'].replace(tzinfo=pytz.utc).astimezone(taiwan_tz)
        user_info_dict['depart_taiwan_date'] = depart_taiwan_date.strftime('%Y-%m-%d')
        
        arrive_taiwan_date = user_info_dict['arrive_taiwan_date'].replace(tzinfo=pytz.utc).astimezone(taiwan_tz)
        user_info_dict['arrive_taiwan_date'] = arrive_taiwan_date.strftime('%Y-%m-%d')
        
        return render_template('user_flight.html', user_info_dict=user_info_dict)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


def update_user():
    try:
        if request.method == "POST":
            json_data = request.get_json()
            current_app.logger.info(f"Data received from update user page: {json_data}")
            response = {
                "status": "success",
                "data" : json_data
            }
            return jsonify(response)
        return render_template('homepage.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@token_required
def update_insurance(current_user):
    try:
        if request.method == "POST":
            insurance_company = request.form.get("insurance_company")
            plan = request.form.get("insurance_plan")
            insured_amount = request.form.get("insured_amount")
            matched_numbers = re.search(r"(\d+)萬", insured_amount)
            if matched_numbers:
                numeric_part = matched_numbers.group(1)
            else:
                numeric_part = None
            days = request.form.get("days")
            matched_days = re.search(r"(\d+)天", days)
            if matched_days:
                day_part = matched_days.group(1)
            else:
                day_part = None
            current_app.logger.info(f"Data received from update insurance page: {insurance_company}, {plan}, {numeric_part}, {day_part}")
            update_insurance_result = update_user_insurance(current_user,insurance_company,plan, numeric_part, day_part, logger=current_app.logger)
            current_app.logger.info(f"Update Insurance Result: {update_insurance_result}")
            return redirect(url_for('user_insurance'))
        return render_template('homepage.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@token_required
def update_flight_info(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        if request.method == "POST":
            depart_taiwan_date = request.form.get("startDate")
            arrive_taiwan_date = request.form.get("endDate")
            # Depart Flights
            depart_flight = request.form.get("departFlight")
            depart_flight = depart_flight.split()[0]
            depart_fight_number = request.form.get("departFlightNumber")
            flight_depart_taoyuan = depart_flight+depart_fight_number
            
            # Arrive Flights
            arrive_flight = request.form.get("arriveFlight")
            arrive_flight = arrive_flight.split()[0]
            arrive_fight_number = request.form.get("arriveFlightNumber")
            flight_arrive_taoyuan = arrive_flight+arrive_fight_number
            current_app.logger.info(f"Data received from update flight page: {depart_taiwan_date}, {arrive_taiwan_date}, {flight_depart_taoyuan}, {flight_arrive_taoyuan}")
            update_flight_info = update_user_flight_info(current_user,depart_taiwan_date,arrive_taiwan_date,flight_depart_taoyuan,flight_arrive_taoyuan, logger=current_app.logger)
            current_app.logger.info(f"Update Flight Info: {update_flight_info}")
            response = {
                "status": "success",
                "data": "Flight Information Updated Successfully.",
                "redirect_url": url_for('user_flight')
            }  
            return jsonify(response)
        return render_template('homepage.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@token_required
def update_notify(current_user):
    try:
        current_app.logger.info(f"Token: {request.headers.get('X-CSRFToken')}")
        if request.method == "POST":
            flight_change = request.form.get('flight_change') == '1' # return False or True
            flight_delay = request.form.get('flight_delay') == '1' # return False or True
            hsr = request.form.get('hsr_station')
            result = update_user_notify(current_user,flight_change,flight_delay,hsr, logger=current_app.logger)
            current_app.logger.info(f"Update Notification: {result}")
            response = {"status": 'success', 
                        "message": "Flight information updated successfully.",
                        "redirect_url": url_for('user_notify')}
            return jsonify(response)
        return render_template("homepage.html")
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500
        


def index():
    try:
        return render_template('homepage.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


def search_flight():
    try:
        return render_template('search_flight.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


def setup_routes(app, csrf):
    @app.route('/send_depart_email', methods=['GET', 'POST'])
    @csrf.exempt
    def send_depart_email():
        current_app.logger.info("Depart email request received")
        try:
            email = request.form.get('email')
            scheduled_depart_time = request.form.get('scheduled_depart_time')
            status = request.form.get('status')
            airline_code = request.form.get('airline_code')
            username = request.form.get('username')
            current_app.logger.info(f"Data received: {email}, {scheduled_depart_time}, {status}, {airline_code}, {username}")
            current_app.logger.info(f"Current app MAIL USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            mail = current_app.extensions['mail']
            msg = Message(subject="Hello",
                        sender=current_app.config.get("MAIL_USERNAME"),
                        recipients=[email], # replace with your email for testing
                        body=f"Hi! {username}  your flight {airline_code} 's time has been changed.\n\
                            Your flight's scheduled depart time {scheduled_depart_time} which status is now {status}.\n\
                            For more detail, please click the link below to trace your flight!")
            # ! -- 這邊再提供 search flight URL ---
            mail.send(msg)
            update_result = update_depart_email_send(username, logger=current_app.logger)
            current_app.logger.info(f"Update Success: {update_result}")
            return jsonify({"status": "Success", "message": "Depart email sent successfully."})
        except Exception as e:
            current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return jsonify({"status": "Failed", "error": str(e)}), 500 


    @app.route('/send_arrive_email', methods=['GET', 'POST'])
    @csrf.exempt
    def send_arrive_email():
        try:
            email = request.json.get('email')
            scheduled_arrive_time = request.json.get('scheduled_arrive_time')
            status = request.json.get('status')
            airline_code = request.json.get('airline_code')
            username = request.json.get('username')
            train_ls = request.json.get('train_ls', [])
            actual_arrive_time = request.json.get('actual_arrive_time', None)
            current_app.logger.info(f"Data received: {email}, {scheduled_arrive_time}, {status}, {airline_code}, {username},{actual_arrive_time}")
            current_app
        except Exception as e:
            current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)    
        try: 
            if actual_arrive_time is not None: # Time changed Flight
                email_body = create_email_body(username, airline_code, scheduled_arrive_time, status, train_ls, actual_arrive_time)
            else: # Cancelled Flight
                email_body = create_cancel_email_body(username, airline_code, scheduled_arrive_time, status)
            current_app.logger.info(f"Email Body Created")
            mail = current_app.extensions['mail']
            msg = Message(subject="Hello",
                            sender=current_app.config.get("MAIL_USERNAME"),
                            recipients=[email], # replace with your email for testing
                            body=email_body)
            mail.send(msg)
            update_result = update_arrive_email_send(username, logger=current_app.logger)
            current_app.logger.info(f"Update Arrive Email Send (Set True to False in MongoDB): {update_result}")
            return jsonify({"status": "Success", "message": " Arrive email sent successfully."})
        except Exception as e:
            current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return jsonify({"status": "Failed", "error": str(e)}), 500
        
    # Email Body
    def create_email_body(username, airline_code, scheduled_arrive_time, status, train_ls, actual_arrive_time):
        train_times_str = '\n'.join([f" Train ID: {train[0]} Departure : {train[1]}, Arrival: {train[2]}, Non-reserved Car: {train[3]}" for train in train_ls])
        
        body = (
            f"Hi! {username}, your flight {airline_code} 's time has been changed. "
            f"Your flight's scheduled depart time is {scheduled_arrive_time} which status is now {status}. "
            f"The predicted arrival time is {actual_arrive_time}."
            "For more detail, please click the link below to trace your flight!\n\n"
            "Here are your train times:\n(after arrive within 5 hours):\n"
            f"{train_times_str}"
        )
        return body
    
    # Cancel Email Body
    def create_cancel_email_body(username, airline_code, scheduled_arrive_time, status):
        body = (
            f"Hi! {username}, your flight {airline_code} 's time has been changed. "
            f"Your flight's scheduled depart time is {scheduled_arrive_time} which status is now {status}. "
            "For more detail, please click the link to trace your flight!\n\n"
        )
        return body
    
def depart_flight_time():
    flight_result = None
    try:
        airline_code = request.form.get('airline') if request.method == 'POST' else request.args.get('airline_code')
        flight_number = request.form.get('flight_number') if request.method == 'POST' else request.args.get('flight_number')
        airline_code = airline_code.split()[0]
        flight = airline_code + flight_number
        flight_result = get_depart_flight_time(flight,logger=current_app.logger)
        current_app.logger.info(f"Flight time retrieved for {flight_result}")
    except Exception:
        current_app.logger.error("Catch an exception.", exc_info=True)
    try:
        share_code_list = []
        if flight_result is not None:
            for each_air in flight_result['airline']:
                if each_air['airline_code'] == flight:
                    main_code = flight
                    airline_name = each_air['airline_name']
                else:
                    share_code_list.append(each_air['airline_code'])
            current_app.logger.info(f"Main code: {main_code}, Share code: {share_code_list}")
            if flight_result['status'] == '':
                flight_result['status'] = '已排定起飛時間'
            taiwan_tz = pytz.timezone('Asia/Taipei')
            updated_at_local = flight_result['updated_at'].replace(tzinfo=pytz.utc).astimezone(taiwan_tz)
            flight_result['updated_at'] = updated_at_local.strftime('%m-%d %H:%M')
            flight = {
                "airline_name":airline_name,
                'main_code': main_code,
                'share_code': share_code_list, 
                'destination': flight_result['destination'],
                'gate': flight_result['gate'],
                'scheduled_depart_time': flight_result['scheduled_depart_time'],
                'actual_depart_time': flight_result['actual_depart_time'],
                'status': flight_result['status'],
                'terminal': flight_result['terminal'],
                'updated_at':flight_result['updated_at']
            }
            return render_template('flight_time.html',flight= flight)
        else:
            flash('No flight found. Please search another flight.', 'alert-danger')
            return redirect(url_for('search_flight'))
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)

def arrive_flight_time():
    flight_result = None
    try:
        airline_code = request.form.get('airline') if request.method == 'POST' else request.args.get('airline_code')
        flight_number = request.form.get('flight_number') if request.method == 'POST' else request.args.get('flight_number')
        airline_code = airline_code.split()[0]
        flight = airline_code + flight_number 
        flight_result = get_arrive_flight_time(flight, logger=current_app.logger)
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
        current_app.logger.info(f"Main code: {main_code}, Share code: {share_code_list}")
        if flight_result['status'] == '':
            flight_result['status'] = '已排定起飛時間'
        taiwan_tz = pytz.timezone('Asia/Taipei')
        updated_at_local = flight_result['updated_at'].replace(tzinfo=pytz.utc).astimezone(taiwan_tz)
        flight_result['updated_at'] = updated_at_local.strftime('%m-%d %H:%M')
        flight = {
            "airline_name":airline_name,
            'main_code': main_code,
            'share_code': share_code_list, 
            'destination': flight_result['destination'],
            'gate': flight_result['gate'],
            'scheduled_arrive_time': flight_result['scheduled_arrive_time'],
            'actual_arrive_time': flight_result['actual_arrive_time'],
            'status': flight_result['status'],
            'terminal': flight_result['terminal'],
            'updated_at':flight_result['updated_at']
        }
        return render_template('flight_time.html',flight= flight)
    else:
        flash('No flight found. Please search another flight.', 'alert-danger')
        return redirect(url_for('search_flight'))


@token_required
def my_insurance(current_user):
    try:
        user_insurance = select_user_insurance(current_user, logger=current_app.logger)
        current_app.logger.info(f"User's Insurance Plans Retrieved from MongoDB Successfully")
        if user_insurance is not None:
            insurance_company = user_insurance["insurance_company"]
            plan = user_insurance["plan"]
            insured_amount = user_insurance["insured_amount"]
            days = user_insurance["days"]
            insurance_content = select_insurance_amount(plan, insured_amount,insurance_company, days, logger=current_app.logger)
            current_app.logger.info(f"Insurance Content Retrieved from MongoDB Successfully")
            insurance_content["insurance_company"] = insurance_company
            
            # !-- start register flight information
            user_flight = select_user_flight(current_user, logger=current_app.logger)
            depart_taiwan_date = user_flight['depart_taiwan_date']
            flight_depart_taoyuan = user_flight['flight_depart_taoyuan']
            depart_flight = select_depart_flight_difference(depart_taiwan_date, flight_depart_taoyuan,logger=current_app.logger)
            depart_taiwan_date = depart_flight['created_at']
            taiwan_tz = pytz.timezone('Asia/Taipei')
            depart_taiwan_date.replace(tzinfo=pytz.utc).astimezone(taiwan_tz)
            depart_taiwan_date = depart_taiwan_date.strftime('%Y-%m-%d')
            return render_template('my_insurance.html', user_insurance = user_insurance, insurance_content= insurance_content, 
                                depart_flight = depart_flight,flight_depart_taoyuan=flight_depart_taoyuan,depart_taiwan_date=depart_taiwan_date)
        else:
            return redirect(url_for('user_insurance'))
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


def insurance():
    try:
        return render_template('insurance.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)


def fetch_insurance_amount():
    try:
        insurance_company = request.form.get('insuranceCompany')
        plan = request.form.get('plan')  
        insurance_amount = request.form.get('insuranceAmount')
        insurance_days = request.form.get('insuranceDays')
        current_app.logger.info(f"Data received from fetch insurance amount: {insurance_company}, {plan}, {insurance_amount}, {insurance_days}")
    except Exception as e:
        current_app.logger.error(f"Catch an exception. + {e}", exc_info=True)
    try:
        result = select_insurance_amount(plan, insurance_amount,insurance_company, insurance_days, logger=current_app.logger)
        current_app.logger.info(f"Insurance amount retrieved from MongoDB successfully")
        if result:
            price = result['insurance_premium']['price']
        else:
            price = '不在試算範圍內, 請重新輸入'
        response = {
                'status': 'success',
                'data': {
                    'insurance_price': price
                }
            }
        current_app.logger.info(f"Insurance price: {price}")
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def fetch_insurance_content():
    try:
        if request.method == "POST":
            selected_inconvenience_insurance = request.form.get("convenienceOption")
            plan = request.form.get("plan")
            days = request.form.get("days")
            insured_amount = request.form.get("insuredAmount")
            insurance_company = request.form.get("insuranceCompany")
            current_app.logger.info(f"Data received from fetch insurance content: {selected_inconvenience_insurance}, {plan}, {days}, {insured_amount}, {insurance_company}")
            result = select_insurance_amount(plan, insured_amount,insurance_company, days, logger=current_app.logger)
            content = result['travel_inconvenience_insurance']['content'][0][selected_inconvenience_insurance]
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
            current_app.logger.info(f"Response In fetch_insurance_content Route: {response}")
            return jsonify(response)
        return render_template("homepage.html")
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def fetch_travel_insurance_content():
    try:
        if request.method == "POST":
            selected_insurance = request.form.get("travelInsuranceOption")
            plan = request.form.get("plan")
            days = request.form.get("days")
            insured_amount = request.form.get("insuredAmount")
            insurance_company = request.form.get("insuranceCompany")
            current_app.logger.info(f"Data received from fetch travel insurance content: {selected_insurance}, {plan}, {days}, {insured_amount}, {insurance_company}")
            result = select_insurance_amount(plan, insured_amount,insurance_company, days, logger=current_app.logger)
            content = result['travel_insurance']['content'][0][selected_insurance]
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
            current_app.logger.info(f"Response In fetch_insurance_content Route: {response}")
            return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500
    

def split_alpha_numeric(s):
    parts = re.findall(r'[A-Za-z]+|\d+', s)
    return parts


def fetch_depart_flight_code():
    try:
        return_code_dic = {}
        result = select_today_depart_flight_code(logger=current_app.logger)
        current_app.logger.info(f"Retrieved today's Depart Flight Code Successfully")
        for each in result:
            airlines = each['airline']
            for airline in airlines:
                airline_code = airline['airline_code']
                split_code = split_alpha_numeric(airline_code)
                if len(split_code) == 2:
                    letter_part, number_part = split_code
                    key = f"{letter_part} {airline['airline_name']}"
                    if key in return_code_dic:
                        if number_part not in return_code_dic[key]:
                            return_code_dic[key].append(number_part) 
                    else:
                        return_code_dic[key] = [number_part] 
        return return_code_dic
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def fetch_arrive_flight_code():
    try:
        return_code_dic = {}
        result = select_today_arrive_flight_code(logger=current_app.logger)
        current_app.logger.info(f"Retrieved today's Arrive Flight Code Successfully")
        for each in result:
            airlines = each['airline']
            for airline in airlines:
                airline_code = airline['airline_code']
                split_code = split_alpha_numeric(airline_code)
                if len(split_code) == 2:
                    letter_part, number_part = split_code
                    key = f"{letter_part} {airline['airline_name']}"
                    if key in return_code_dic:
                        if number_part not in return_code_dic[key]:
                            return_code_dic[key].append(number_part) 
                    else:
                        return_code_dic[key] = [number_part] 
        return return_code_dic
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def fetch_user_depart_flight_code():
    try:
        return_code_dic = {}
        result = select_user_depart_flight_code(logger=current_app.logger)
        current_app.logger.info(f"Retrieved All Depart Flights Information")
        for each in result:
            airlines = each['airline']
            for airline in airlines:
                airline_code = airline['airline_code']
                split_code = split_alpha_numeric(airline_code)
                if len(split_code) == 2:
                    letter_part, number_part = split_code
                    key = f"{letter_part} {airline['airline_name']}"
                    if key in return_code_dic:
                        if number_part not in return_code_dic[key]:
                            return_code_dic[key].append(number_part) 
                    else:
                        return_code_dic[key] = [number_part] 
        return return_code_dic
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def fetch_user_arrive_flight_code():
    try:
        return_code_dic = {}
        result = select_user_arrive_flight_code(logger=current_app.logger)
        current_app.logger.info(f"Retrieved All Arrive Flights Information")
        for each in result:
            airlines = each['airline']
            for airline in airlines:
                airline_code = airline['airline_code']
                split_code = split_alpha_numeric(airline_code)
                if len(split_code) == 2:
                    letter_part, number_part = split_code
                    key = f"{letter_part} {airline['airline_name']}"
                    if key in return_code_dic:
                        if number_part not in return_code_dic[key]:
                            return_code_dic[key].append(number_part) 
                    else:
                        return_code_dic[key] = [number_part] 
        return return_code_dic
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500


def flight_map():
    try:
        return render_template('map_with_layers.html')
    except Exception as e:
        current_app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        abort(500)