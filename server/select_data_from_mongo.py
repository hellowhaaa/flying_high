
from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from datetime import datetime, tzinfo, timezone, timedelta
import pytz
load_dotenv()




def get_arrive_flight_time(flight):  # airline_code 是 JL96 的組合\l
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    #  今天凌晨
    tw_now = datetime.now(taiwan_tz)
    tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
    utc_midnight = tw_midnight.astimezone(pytz.utc)  # UTC Time
    
    # 兩天前測試
    # two_days_ago = tw_now - timedelta(days=2)
    # tw_midnight = taiwan_tz.localize(datetime(two_days_ago.year, two_days_ago.month, two_days_ago.day, 0, 0, 0))
    # utc_midnight = tw_midnight.astimezone(pytz.utc)
    
    
    filter={
        'airline': {
            '$elemMatch': {
                'airline_code': flight
            }
        },
        'updated_at': {
        '$gt': utc_midnight
    }
    }
    result = client['flying_high']['flight_arrive2'].find_one(
    filter=filter
    )
    return result

def get_depart_flight_time(flight):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    #  今天凌晨
    tw_now = datetime.now(taiwan_tz)
    tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
    utc_midnight = tw_midnight.astimezone(pytz.utc)  # UTC Time

    filter={
        'airline': {
            '$elemMatch': {
                'airline_code': flight
            }
        },
        'updated_at': {
        '$gt': utc_midnight
    }
    }
    result = client['flying_high']['flight_depart2'].find_one(
    filter=filter
    )
    return result




def select_insurance_amount(plan, insurance_amount,insurance_company, insurance_days):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    insurance_amount = int(insurance_amount) * 10000 if int(insurance_amount) < 3000 else insurance_amount
    print(insurance_amount)
    filter={
    'insured_amount.price': insurance_amount, 
    'plan.plan_name': plan,
    'days': int(insurance_days)
    }
    print("filter->", filter)
    result = client['flying_high']['insurance_'+insurance_company].find_one(
        filter = filter
    )  
    print(result)
    return result

def select_user_information(username):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter={
    'username': username
    }
    result = client['flying_high']['user'].find_one(
    filter=filter
    )
    print("user", result)
    return result

def select_user_insurance(username):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter={
    'username': username
    }
    result = client['flying_high']['user_insurance'].find_one(
    filter=filter
    )
    print("user_insurance", result)
    return result
    
    
    
    