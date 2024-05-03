from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pendulum
from dotenv import load_dotenv
from pymongo import MongoClient,DESCENDING
import os
from datetime import datetime, tzinfo, timezone, timedelta, time
import pytz
import requests
import json

API_ENDPOINT  = 'http://13.230.61.140/send_arrive_email'

def get_arrive_flight_time():
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    #  今天凌晨
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

def transform_result():
    result_ls = get_arrive_flight_time()
    for collection in result_ls:
        print(collection)
        print("-------")
        airlines = collection['airline']
        scheduled_arrive_time = collection['scheduled_arrive_time']
        status = collection['status']
        actual_arrive_time = collection['actual_arrive_time'] if collection['actual_arrive_time'] != "" else None
        print(actual_arrive_time)
        if actual_arrive_time is not None:
            print("actual_arrive_time", actual_arrive_time)
            train_ls = []
            print(type(actual_arrive_time))
            actual_arrive_time = datetime.strptime(actual_arrive_time, "%H:%M").time()
            print("這", type(actual_arrive_time))
            for airline in airlines:
                airline_code = airline['airline_code']
                # 找出需要發送 email的 user
                send_email_dic = select_user_flight(airline_code)
                print("send_email_dic")
                if send_email_dic is not None:
                    # 找出大於 actual_arrive_time 的高鐵班次
                    hsr_station = send_email_dic['hsr_station']
                    print("hsr_station", hsr_station)
                    train_time = select_hsr_train(hsr_station)
                    if train_time is not None:     
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
                        print("train_ls", train_ls)
                        username = send_email_dic['username']
                        user_info = select_user_email(username)
                        # 找出使用者的 email
                        if user_info is not None:
                            email = user_info['email']
                            print("email", email)
                            print("scheduled_arrive_time->", scheduled_arrive_time)
                            print("status-->", status)
                            actual_arrive_time = actual_arrive_time.strftime("%H:%M") if actual_arrive_time else None
                            data = {'email': email,
                                    'scheduled_arrive_time':scheduled_arrive_time,
                                    'status':status,
                                    'airline_code':airline_code,
                                    'username':username,
                                    'train_ls':train_ls,
                                    "actual_arrive_time":actual_arrive_time  # Could be None
                                }
                            print("data", data)
                            try:
                                headers = {'Content-Type': 'application/json'}
                                response = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
                                response_text = response.text
                                print(response_text)
                                response.raise_for_status()
                            except requests.exceptions.HTTPError as err:
                                print(f"HTTP error occurred: {err}")
                            except requests.exceptions.ConnectionError as err:
                                print(f"Connection error occurred: {err}")
                            except Exception as err:
                                print(f"An error occurred: {err}")        
                            
                        else:
                            print("no no email")
                else:
                    print("no no username")
        else:
            print("no actual_arrive_time, means flight has been canceled or time is not fixed yet.")
            for airline in airlines:
                airline_code = airline['airline_code']
                # 找出需要發送 email的 user
                send_email_dic = select_user_flight(airline_code)
                print("send_email_dic, find out who need to be notified.")
                if send_email_dic is not None:
                    username = send_email_dic['username']
                    user_info = select_user_email(username)
                    # 找出使用者的 email
                    if user_info is not None:
                        email = user_info['email']
                        print("email", email)
                        print("scheduled_arrive_time->", scheduled_arrive_time)
                        print("status-->", status)
                        data = {'email': email,
                                'scheduled_arrive_time':scheduled_arrive_time,
                                'status':status,
                                'airline_code':airline_code,
                                'username':username
                                # 'train_ls':train_ls,
                                # "actual_arrive_time":actual_arrive_time  # Could be None
                            }
                        print("data", data)
                        try:
                            headers = {'Content-Type': 'application/json'}
                            response = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
                            response_text = response.text
                            print(response_text)
                            response.raise_for_status()
                        except requests.exceptions.HTTPError as err:
                            print(f"HTTP error occurred: {err}")
                        except requests.exceptions.ConnectionError as err:
                            print(f"Connection error occurred: {err}")
                        except Exception as err:
                            print(f"An error occurred: {err}") 
            


def select_user_email(username):
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
        print(str(e))
        
        
def select_user_flight(airline_code):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        #  今天凌晨
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        # 轉換成 UTC 時間
        utc_midnight = tw_midnight.astimezone(pytz.utc)
        print("使用者的utc---->", utc_midnight)
        
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
        
        for user_flight_col in result:
            username = user_flight_col['username']
            # 找出 需要寄送通知, 但是還沒有寄送過的人 
            filter={
                'username': username, 
                'flight_delay': True,
                'arrive_email_send':False
                    }
            send_email = client['flying_high']['user_notify'].find_one(
            filter=filter
            )
            if send_email is not None:
                print("test success")
                return send_email #dict
    except Exception as e:
        print(str(e))

def select_hsr_train(hsr_station):
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
    client = MongoClient(url)
    #  今天凌晨
    taiwan_tz = pytz.timezone('Asia/Taipei')
    tw_now = datetime.now(taiwan_tz)
    tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
    utc_midnight = tw_midnight.astimezone(pytz.utc)
    print("hsr_staiton_inside_filter", hsr_station)
    filter={
        'end_station': hsr_station,
    #     'hsr_utc_time': {
    #     # '$eq': utc_midnight
    # }
    }
    print("filter", filter)
    result = client['flying_high']['hsr_time'].find_one(
    filter=filter
    )
    print("train_time:----->", result)
    return result
    
        
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
    schedule="*/10 * * * *", # 每十分鐘執行一次
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