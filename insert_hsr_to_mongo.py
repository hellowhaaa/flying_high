import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
# URL to send the request
URL= "https://superiorapis-creator.cteam.com.tw/manager/feature/proxy/534480ccb85539bba80486617b843b6f96/pub_4f12308f3bc8f08dc6617b85b1fda9"


# 獲取當前UTC日期
current_date = datetime.now(ZoneInfo("Asia/Taipei")).date()

# 在當前UTC日期基礎上創建一個午夜時間點的 datetime 對象
midnight = datetime(current_date.year, current_date.month, current_date.day, tzinfo=ZoneInfo("Asia/Taipei"))

# 格式化日期時間為 "YYYY-MM-DDT00:00:00Z" 格式
formatted_midnight = midnight.strftime("%Y-%m-%dT%H:%M:%SZ")


# Define enum
# Origin path:start_station_no

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
def insert_json():
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
            response_data['utc_time'] = midnight_utc
            collection = insert_mongodb_atlas()
            collection.insert_one(response_data)


def insert_mongodb_atlas():
    uri = "mongodb+srv://root:HCadEw7bWkMlybDF@cluster0.ddhtgvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    conn = MongoClient(uri)
    try:
        conn.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # Create a MongoClient instance
    db = conn['flying_high']
    # Access a collection (similar to a table in relational databases)
    collection = db['hsr_time']

    mongo_dblist = conn.list_database_names()
    if "flying_high" in mongo_dblist:
        print("flying_high database 已存在！")
    else:
        print('flying_high database 不存在')
    
    return collection
# insert_mongodb_atlas()
insert_json()