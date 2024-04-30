from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pendulum
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from datetime import datetime, tzinfo, timezone, timedelta
import pytz
import requests

API_ENDPOINT  = 'http://127.0.0.1:5000/send_arrive_email'

def get_arrive_flight_time():
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
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
    filter=filter
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
                print("train_time", train_time)
                
                
                
            #     username = send_email_dic['username']
            #     user_info = select_user_email(username)
            #     # 找出使用者的 email
            #     if user_info is not None:
            #         email = user_info['email']
            #         print("email", email)
            #         print("scheduled_arrive_time->", scheduled_arrive_time)
            #         print("status-->", status)
            #         data = {'email': email,
            #                 'scheduled_arrive_time':scheduled_arrive_time,
            #                 'status':status,
            #                 'airline_code':airline_code,
            #                 'username':username,
            #                 "actual_arrive_time":actual_arrive_time  # Could be None
            #             }
            #         response = requests.post(url=API_ENDPOINT, data=data)
            #         response_text = response.text
            #         print(response_text)        
                    
            #     else:
            #         print("no no email")
            # else:
            #     print("no no username")


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

    filter={
        'end_station': hsr_station,
        'hsr_utc_time': {
        '$eq': utc_midnight
    }
    }
    result = client['flying_high']['hsr_time'].find_one(
    filter=filter
    )
    return result
    
        
        
        
        
        
        
        
        
        
        
        

transform_result()

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False, 
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5)
# }

# with DAG(
#     dag_id="release_catch_flight_change",
#     schedule="*/10 * * * *", # 每十分鐘執行一次
#     start_date=pendulum.datetime(2024, 4, 25, tz="UTC"),
#     default_args=default_args,
#     catchup=False, # 不會去執行以前的任務
#     max_active_runs=1,
#     tags=['flight'],
# ) as dag:
#     task_start = EmptyOperator(
#     task_id="task_start",
#     dag=dag
#     )
#     task_end = EmptyOperator(
#     task_id="task_end",
#     dag=dag
#     )
    
#     task_depart_flight_change = PythonOperator(
#         task_id = "depart_flight_change",
#         python_callable=get_depart_flight_time,
#         dag = dag  
#     )
#     task_arrive_flight_change = PythonOperator(
#         task_id = "arrive_flight_change",
#         python_callable=get_arrive_flight_time,
#         dag = dag  
#     )
    
# (task_start >> [task_depart_flight_change, task_arrive_flight_change] >> task_end)