from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from datetime import datetime, tzinfo, timezone, timedelta
import pytz
load_dotenv()
def update_user_insurance(username,insurance_company,plan, insured_amount, days):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter = {"username": username}
    
    update = {
        "$set": {
            "insurance_company": insurance_company,
            "plan": plan,
            "insured_amount": insured_amount,
            "days": days,
            "updated_at": datetime.utcnow()
        },
        "$setOnInsert": {
            "created_at": datetime.utcnow()  # Only set this field on insert (upsert)
        }
    }
    result = client['flying_high']['user_insurance'].update_many(
    filter=filter,
    update = update,
    upsert = True)
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": result.upserted_id
    }

def update_user_flight_info(username,depart_taiwan_date,arrive_taiwan_date,flight_depart_taoyuan,flight_arrive_taoyuan):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    # 桃園機場出發的班機 算出當天的 utc時間
    start_date_obj = datetime.strptime(depart_taiwan_date, '%Y-%m-%d')
    start_date_tw_midnight = taiwan_tz.localize(datetime(start_date_obj.year, start_date_obj.month, start_date_obj.day, 0, 0, 0))
    start_date_utc_midnight = start_date_tw_midnight.astimezone(pytz.utc)
    # 抵達桃園機場的班機 算出當天的 utc時間
    end_date_obj = datetime.strptime(arrive_taiwan_date, '%Y-%m-%d')
    end_date_tw_midnight = taiwan_tz.localize(datetime(end_date_obj.year, end_date_obj.month, end_date_obj.day, 0, 0, 0))
    end_date_utc_midnight = end_date_tw_midnight.astimezone(pytz.utc)
    
    filter = {"username": username}
    update = {
        "$set": {
            "depart_taiwan_date": start_date_utc_midnight,
            "arrive_taiwan_date": end_date_utc_midnight,
            "flight_depart_taoyuan":flight_depart_taoyuan,
            "flight_arrive_taoyuan":flight_arrive_taoyuan,
            "updated_at": datetime.utcnow()
        },
        "$setOnInsert": {
            "created_at": datetime.utcnow()  # Only set this field on insert (upsert)
        }
    }
    result = client['flying_high']['user_flight'].update_many(
    filter=filter,
    update = update,
    upsert = True)
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": result.upserted_id
    }

def update_user_notify(username,flight_change,flight_delay,hsr):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter = {"username": username}
    
    update = {
        "$set": {
            "flight_change": flight_change,
            "flight_delay": flight_delay,
            "hsr_station": hsr,
            "updated_at": datetime.utcnow()
        },
        "$setOnInsert": {
            "depart_email_send":False,
            "arrive_email_send":False,
            "created_at": datetime.utcnow()  # Only set this field on insert (upsert)
        }
    }
    result = client['flying_high']['user_notify'].update_many(
    filter=filter,
    update = update,
    upsert = True)
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": result.upserted_id
    }
    
def update_depart_email_send(username):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter = {"username": username}
    update = {
        "$set": {
            "depart_email_send": True
            }
        }
    result = client['flying_high']['user_notify'].update_one(
    filter=filter,
    update = update
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }
    
def update_arrive_email_send(username):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter = {"username": username}
    update = {
        "$set": {
            "arrive_email_send": True
            }
        }
    result = client['flying_high']['user_notify'].update_one(
    filter=filter,
    update = update
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }