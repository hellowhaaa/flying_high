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
    
def update_user_flight_info(username,start_date,end_date,depart_flight, depart_fight_number, arrive_flight, arrive_fight_number):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    
    start_date_tw_midnight = taiwan_tz.localize(datetime(start_date_obj.year, start_date_obj.month, start_date_obj.day, 0, 0, 0))
    start_date_utc_midnight = start_date_tw_midnight.astimezone(pytz.utc)
    
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    end_date_tw_midnight = taiwan_tz.localize(datetime(end_date_obj.year, end_date_obj.month, end_date_obj.day, 0, 0, 0))
    end_date_utc_midnight = end_date_tw_midnight.astimezone(pytz.utc)
    
    filter = {"username": username}
    update = {
        "$set": {
            "start_date_utc": start_date_utc_midnight,
            "end_date_utc": end_date_utc_midnight,
            "depart_flight": depart_flight,
            "depart_fight_number": depart_fight_number,
            "arrive_flight": arrive_flight,
            "arrive_fight_number": arrive_fight_number,
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

def update_user_notify(username,flight_change,flight_delay):
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    filter = {"username": username}
    
    update = {
        "$set": {
            "flight_change": flight_change,
            "flight_delay": flight_delay,
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
    
def update_send_email(username):
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