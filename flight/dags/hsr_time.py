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

# 使用相對路徑
# relative_path = '../.env'  # 回到兩層目錄再進入 config 目錄
# dotenv_path = os.path.join(os.path.dirname(__file__), relative_path)


# URL to send the request
URL= "https://superiorapis-creator.cteam.com.tw/manager/feature/proxy/534480ccb85539bba80486617b843b6f96/pub_4f12308f3bc8f08dc6617b85b1fda9"


# 獲取當前UTC日期
current_date = datetime.now(ZoneInfo("Asia/Taipei")).date()

# 在當前UTC日期基礎上創建一個午夜時間點的 datetime 對象
midnight = datetime(current_date.year, current_date.month, current_date.day, tzinfo=ZoneInfo("Asia/Taipei"))

# 格式化日期時間為 "YYYY-MM-DDT00:00:00Z" 格式
formatted_midnight = midnight.strftime("%Y-%m-%dT%H:%M:%SZ")


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
        "end_station_no": x, # x
        # "datetime": "2024-04-16T00:00:00Z"
        "datetime":formatted_midnight
        })
        
        if x != 4:
            # Send the request using requests library
            response = requests.post(URL, params = params, data = postData, headers = headers)
            response_data = response.json()
            # 獲取當前本地日期
            current_local_date = datetime.now().date()
            # 在當前日期基礎上創建一個午夜時間點的 datetime 對象，並指定本地時區
            midnight_local = datetime(current_local_date.year, current_local_date.month, current_local_date.day, tzinfo=ZoneInfo("Asia/Taipei"))
            # 將本地午夜時間點轉換為 UTC
            midnight_utc = midnight_local.astimezone(ZoneInfo("UTC"))
            response_data['hsr_utc_time'] = midnight_utc
            response_data["updated_at"] = datetime.utcnow()
            response_data["created_at"] =  datetime.utcnow()
            collection = insert_mongodb_atlas()
            collection.insert_one(response_data)


def insert_mongodb_atlas():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    conn = MongoClient(uri)
    try:
        conn.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
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
    schedule="0 17 * * *", # 每天 UTC 17:00，對應台灣時間 01:00
    start_date=pendulum.datetime(2024, 4, 15, tz="UTC"),
    default_args=default_args,
    catchup=False, # 不會去執行以前的任務
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