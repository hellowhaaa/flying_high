from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pendulum
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from datetime import datetime, tzinfo, timezone, timedelta
import pytz



    




def get_depart_flight_time():
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
    result = client['flying_high']['flight_depart2'].find(
    filter=filter
    )
    return list(result)

def transform_result():
    result_ls = get_depart_flight_time()
    for collection in result_ls:
        # print(collection)
        print("-------")
        airlines = collection['airline']
        for airline in airlines:
            airline_code = airline['airline_code']
            email_dic = select_user_flight(airline_code)
            print(email_dic)
            

            

def select_user_flight(airline_code):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={'flight_depart_taoyuan': airline_code}
        result = client['flying_high']['user_flight'].find(
        filter=filter)
        result = list(result)
        
        for user_flight_col in result:
            username = user_flight_col['username']
            filter={
                'username': username, 
                'flight_change': True
                    }
            send_email = client['flying_high']['user_notify'].find_one(
            filter=filter
            )
            if send_email is not None:
                print("test success")
                return send_email #dict
    except Exception as e:
        print(str(e))
            
        




transform_result()
# print("arrive->: ", get_arrive_flight_time())
# print("depart->", get_depart_flight_time())

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
    
#     task_arrive_flight_change = PythonOperator(
#         task_id = "arrive_flight_change",
#         python_callable=get_arrive_flight_time,
#         dag = dag  
#     )
    
# (task_start >> task_arrive_flight_change >> task_end)