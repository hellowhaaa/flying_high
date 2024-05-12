from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import requests
import json
from datetime import timedelta
from pymongo import MongoClient
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os
import pendulum
import logging

# URL to send the request to
URL= "https://superiorapis-creator.cteam.com.tw/manager/feature/proxy/534480ccb85539bba80486617b843b6f96/pub_4f12308f3bc8f08dc6617b85b1fda9"


# Get the current date
current_date = datetime.now(ZoneInfo("Asia/Taipei")).date()

# Create a datetime object for a midnight time point on the current date, and specify the time zone as Asia/Taipei
midnight = datetime(current_date.year, current_date.month, current_date.day, tzinfo=ZoneInfo("Asia/Taipei"))

# Convert the local midnight time point to UTC
formatted_midnight = midnight.strftime("%Y-%m-%dT%H:%M:%SZ")

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

enum1 = {
    "南港": 1,
    "台北": 2,
    "板橋": 3,
    "桃園": 4,
    "新竹": 5,
    "苗栗": 6,
    "台中": 7,
    "彰化": 8,
    "雲林": 9,
    "嘉義": 10,
    "台南": 11,
    "左營": 12
    }

    # Origin path:end_station_no
enum2 = {
    "南港": 1,
    "台北": 2,
    "板橋": 3,
    "桃園": 4,
    "新竹": 5,
    "苗栗": 6,
    "台中": 7,
    "彰化": 8,
    "雲林": 9,
    "嘉義": 10,
    "台南": 11,
    "左營": 12
    }
def insert_hsr_time():
    # token token to be sent with the request
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjZXJ0IjoiNzI4MDY2NmMxNjU2Mzg4YWVmMGI4M2ZhOGI3NjdlZTU1MmE2NmRjMSIsImlhdCI6MTcxMjgzMDUzMX0.NCi5K4gG9l67E1J7GG1rTsHBlIkuaVaaAKjn2PIu2NI"
    # Query parameters to be sent with the request
    params = {}
    # Headers to be sent with the request
    headers = {
    'Content-type': 'application/json',
    'token': token,
    }
    for x in range(1,13):
        # Data to be sent with the request
        postData = json.dumps({
        "start_station_no": 4,
        "end_station_no": x, 
        # "datetime": "2024-04-16T00:00:00Z"
        "datetime":formatted_midnight
        })
        try:
            if x != 4:
                # Send the request using requests library
                response = requests.post(URL, params = params, data = postData, headers = headers)
                response_data = response.json()
                logging.info(f"Response data: {response_data}")
                current_local_date = datetime.now().date()
                midnight_local = datetime(current_local_date.year, current_local_date.month, current_local_date.day, tzinfo=ZoneInfo("Asia/Taipei"))
                midnight_utc = midnight_local.astimezone(ZoneInfo("UTC"))
                response_data['hsr_utc_time'] = midnight_utc
                response_data["updated_at"] = datetime.utcnow()
                response_data["created_at"] =  datetime.utcnow()
                collection = insert_mongodb_atlas()
                collection.insert_one(response_data)
                logging.info(f"Data inserted successfully for end_station_no: {x}")
        except Exception as e:
            logging.error(f"An exception occurred: {str(e)}", exc_info=True)


def insert_mongodb_atlas():
    load_dotenv()
    uri = os.getenv("MONGODB_URI_FLY")
    conn = MongoClient(uri)
    try:
        conn.admin.command('ping')
        logging.info(f"You successfully connected to MongoDB!")
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)
    db = conn['flying_high']
    collection = db['hsr_time']
    return collection


default_args = {
    'owner': 'airflow',
    'depends_on_past': False, 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="release_hsr_time",
    schedule="0 17 * * *", # every day at UTC's 17:00 which is 01:00 at Asia/Taipei
    start_date=pendulum.datetime(2024, 4, 15, tz="UTC"),
    default_args=default_args,
    catchup=False, # won't run any previous tasks
    max_active_runs=1,
    tags=['hsr_time'],
) as dag:
    task_start = EmptyOperator(
    task_id="task_start",
    dag=dag
    )
    task_end = EmptyOperator(
    task_id="task_end",
    dag=dag
    )
    
    task_hsr_time = PythonOperator(
        task_id = "insert_hsr_time_mongodb",
        python_callable=insert_hsr_time,
        dag = dag  
    )
    
(task_start >> task_hsr_time >> task_end)