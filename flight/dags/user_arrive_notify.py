from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pendulum
from dotenv import load_dotenv
from pymongo import MongoClient,DESCENDING
import os
from datetime import datetime,timedelta
import pytz
import requests
import json
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

API_ENDPOINT  = 'https://www.flyinghigh.live/send_arrive_email'


def transform_result():
    try:
        logging.info("Start to fetch the flight data and send email")
        result_ls = get_arrive_flight_time()
        for collection in result_ls:
            logging.info("Canceled or Delayed Arrive Flight %s", collection)
            airlines = collection['airline']
            scheduled_arrive_time = collection['scheduled_arrive_time']
            status = collection['status']
            actual_arrive_time = collection['actual_arrive_time'] if collection['actual_arrive_time'] != "" else None
            logging.info("Actual Arrive Time: %s", actual_arrive_time)
            if actual_arrive_time is not None: # check if the flight has been canceled or time is fixed
                train_ls = []
                actual_arrive_time = datetime.strptime(actual_arrive_time, "%H:%M").time()
                for airline in airlines:
                    airline_code = airline['airline_code']
                    send_email_dic = select_user_flight(airline_code)
                    if send_email_dic is not None: # check if there are users need to be send email
                        logging.info("Who need to be notified: %s", send_email_dic)
                        hsr_station = send_email_dic['hsr_station']
                        train_time = select_hsr_train(hsr_station)
                        logging.info("Train time: %s", train_time)
                        if train_time is not None: # check if there are trains available
                            for each_train in train_time['train_item']:
                                train_departure_time_str = each_train['departure_time']
                                if train_departure_time_str: # departure_time could be None
                                    train_departure_time = datetime.strptime(train_departure_time_str, "%H:%M").time()
                                    if is_within_five_hours(actual_arrive_time, train_departure_time):
                                        train_destination_time = each_train['destination_time']
                                        non_reserved_car = each_train['non_reserved_Car']
                                        train_id = each_train['id']
                                        formatted_time_str = train_departure_time.strftime("%H:%M")
                                        train_ls.append((train_id,formatted_time_str, train_destination_time, non_reserved_car))
                            logging.info("Train list: %s", train_ls)
                            username = send_email_dic['username']
                            user_info = select_user_email(username)
                            logging.info("User Information: %s", user_info)
                            if user_info is not None: 
                                email = user_info['email']
                                actual_arrive_time = actual_arrive_time.strftime("%H:%M") if actual_arrive_time else None
                                data = {'email': email,
                                        'scheduled_arrive_time':scheduled_arrive_time,
                                        'status':status,
                                        'airline_code':airline_code,
                                        'username':username,
                                        'train_ls':train_ls,
                                        "actual_arrive_time":actual_arrive_time  # Could be None
                                    }
                                logging.info("Data post to API: %s", data)
                                try:
                                    headers = {'Content-Type': 'application/json'}
                                    response = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
                                    response_text = response.text
                                    logging.info("Response after Post: %s", response_text)
                                    response.raise_for_status()
                                except requests.exceptions.HTTPError as err:
                                    logging.error(f"HTTP error occurred: {err}")
                                except requests.exceptions.ConnectionError as err:
                                    logging.error(f"Connection error occurred: {err}")
                                except Exception as err:
                                    logging.error(f"An error occurred: {err}")    
                            else:
                                logging.info("No email found")
                        else:
                            logging.info("No train found")
                    else:
                        logging.info("No user found")
            else: # flight canceled or time is not fixed
                logging.info("No actual_arrive_time, Flight has been canceled or time is not fixed yet.")
                for airline in airlines:
                    airline_code = airline['airline_code']
                    send_email_dic = select_user_flight(airline_code)
                    if send_email_dic is not None: # check if there are users need to be send email
                        logging.info("Who need to be notified: %s", send_email_dic)
                        username = send_email_dic['username']
                        user_info = select_user_email(username)
                        if user_info is not None:
                            email = user_info['email']
                            data = {'email': email,
                                    'scheduled_arrive_time':scheduled_arrive_time,
                                    'status':status,
                                    'airline_code':airline_code,
                                    'username':username
                                    # 'train_ls':train_ls,
                                    # "actual_arrive_time":actual_arrive_time  # Could be None
                                }
                            logging.info("Data post to API: %s", data)
                            try:
                                headers = {'Content-Type': 'application/json'}
                                response = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
                                response_text = response.text
                                logging.info("Response after Post: %s", response_text)
                                response.raise_for_status()
                            except requests.exceptions.HTTPError as err:
                                logging.error(f"HTTP error occurred: {err}")
                            except requests.exceptions.ConnectionError as err:
                                logging.error(f"Connection error occurred: {err}")
                            except Exception as err:
                                logging.error(f"An error occurred: {err}")  
                        else:
                            logging.info("No email found")
                    else:
                        logging.info("No user found")
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)
                    
                    
def get_arrive_flight_time():
    logging.info("Start to get time canceled or time changed flight.")
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")  
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        #  midnight of today
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        utc_midnight = tw_midnight.astimezone(pytz.utc)  # UTC Time
        filter={
            'status': {
            '$in': [
                '預計時間變更.', '時間未定', '取消'
                ]
            },
            'updated_at': {
            '$gt': utc_midnight
        }
        }
        result = client['flying_high']['flight_arrive2'].find(
        filter=filter,
        sort=[('updated_at', DESCENDING)]
        )
        return list(result)
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)

def select_user_email(username):
    logging.info("Start to get user email.")
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
        'username': username
        }
        result = client['flying_high']['user'].find_one(
        filter=filter
        )   
        return result # dict      
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)
        
        
def select_user_flight(airline_code):
    logging.info("Start to get username for specific flight which assigned for today.")
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        #  Midnight of today
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        # UTC Time
        utc_midnight = tw_midnight.astimezone(pytz.utc)
        logging.info("User's UTC time: %s", utc_midnight)
        # 找出有登記 此飛機 且出發日期為今天 （utc時間）的 user
        filter = {
            'flight_arrive_taoyuan': airline_code,
            'arrive_taiwan_date': {
                '$eq': utc_midnight
            }
        } 
        result = client['flying_high']['user_flight'].find(
        filter=filter)
        result = list(result)
        logging.info("Start to find the user who needs email but has not been sent email")
        for user_flight_col in result: # find the user who needs email but has not been sent email
            username = user_flight_col['username']
            filter={
                'username': username, 
                'flight_delay': True,
                'arrive_email_send':False
                    }
            send_email = client['flying_high']['user_notify'].find_one(
            filter=filter
            )
            return send_email # dict
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)

def select_hsr_train(hsr_station):
    try:
        logging.info("Start to get HSR train time.")
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
        'end_station': hsr_station
        }
        sort=list({
            'updated_at': -1
        }.items())
        result = client['flying_high']['hsr_time'].find_one(
        filter=filter,
        sort=sort
        )
        return result
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)
    
        
def is_within_five_hours(start_time, end_time):
    # check if the difference between start_time and end_time is within 5 hours
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    return 0 <= (end_minutes - start_minutes) <= 5 * 60         
        

default_args = {
    'owner': 'airflow',
    'depends_on_past': False, 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="release_catch_arrive_flight_change",
    schedule="*/20 * * * *", # 每20分鐘執行一次
    start_date=pendulum.datetime(2024, 4, 25, tz="UTC"),
    default_args=default_args,
    catchup=False, # 不會去執行以前的任務
    max_active_runs=1,
    tags=['flight'],
) as dag:
    task_start = EmptyOperator(
    task_id="task_start",
    dag=dag
    )
    task_end = EmptyOperator(
    task_id="task_end",
    dag=dag
    )
    
    task_arrive_flight_change = PythonOperator(
        task_id = "arrive_flight_change",
        python_callable=transform_result,
        dag = dag  
    )
    
(task_start >> task_arrive_flight_change >> task_end)