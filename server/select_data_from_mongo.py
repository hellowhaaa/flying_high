
from pymongo import MongoClient,DESCENDING
import os 
from dotenv import load_dotenv
from datetime import datetime
import pytz
load_dotenv()


def get_arrive_flight_time(flight, logger):
    logger.info("Start Fetching Arrive Flight Time from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
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
        result = client['flying_high']['flight_arrive2'].find_one(
        filter=filter,
        sort=[('updated_at', DESCENDING)]
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_arrive_flight_time: {str(e)}")
        return None


def get_depart_flight_time(flight, logger):
    logger.info("Start Fetching Depart Flight Time from MongoDB")
    try:
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
        filter=filter,
        sort=[('updated_at', DESCENDING)]
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_depart_flight_time: {str(e)}")
        return None


def select_today_depart_flight_code(logger):
    logger.info("Start Fetching Today's Depart Flight Time from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        utc_midnight = tw_midnight.astimezone(pytz.utc)
        filter={
            'updated_at': {
                '$gt': utc_midnight
            }
        }
        result = client['flying_high']['flight_depart2'].find(
        filter=filter
        )
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_today_depart_flight_code: {str(e)}")
        return None


def select_today_arrive_flight_code(logger):
    logger.info("Start Fetching Today's Arrive Flight Time from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        utc_midnight = tw_midnight.astimezone(pytz.utc)
        filter={
            'updated_at': {
                '$gt': utc_midnight
            }
        }
        result = client['flying_high']['flight_arrive2'].find(
        filter=filter
        )
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_today_arrive_flight_code: {str(e)}")
        return None


def select_user_depart_flight_code(logger):
    logger.info("Start Fetching User's All Depart Flight Time from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        result = client['flying_high']['flight_depart2'].find()
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_user_depart_flight_code: {str(e)}")
        return None


def select_user_arrive_flight_code(logger):
    logger.info("Start Fetching User's All Arrive Flight Time from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        result = client['flying_high']['flight_arrive2'].find()
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_user_arrive_flight_code: {str(e)}")
        return None


def select_insurance_amount(plan, insurance_amount,insurance_company, insurance_days, logger):
    logger.info("Start Fetching Insurance Amount from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        insurance_amount = int(insurance_amount) * 10000 if int(insurance_amount) < 3000 else insurance_amount
        filter={
            'insured_amount.price': insurance_amount,
            'plan.plan_name': plan,
            'days': int(insurance_days)
        }
        result = client['flying_high']['insurance_'+insurance_company].find_one(
            filter=filter
        )  
        return result
    except Exception as e:
        logger.error(f"Error in select_insurance_amount: {str(e)}")
        return None


def select_user_information(username, logger):
    logger.info("Start Fetching User Information from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
            'username': username
        }
        result = client['flying_high']['user'].find_one(
        filter=filter
        )
        return result
    except Exception as e:
        logger.error(f"Error in select_user_information: {str(e)}")
        return None


def select_user_insurance(username, logger):
    logger.info("Start Fetching User Insurance from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
            'username': username
        }
        result = client['flying_high']['user_insurance'].find_one(
        filter=filter
        )
        return result
    except Exception as e:
        logger.error(f"Error in select_user_insurance: {str(e)}")
        return None
    
    
def select_user_notify(username, logger):
    logger.info("Start Fetching User Notify from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
            'username': username
        }
        result = client['flying_high']['user_notify'].find_one(
        filter=filter
        )
        return result
    except Exception as e:
        logger.error(f"Error in select_user_notify: {str(e)}")
        return None


def select_user_flight(username, logger):
    logger.info("Start Fetching User Flight from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
            'username': username
        }
        result = client['flying_high']['user_flight'].find_one(
        filter=filter
        )
        return result
    except Exception as e:
        logger.error(f"Error in select_user_notify: {str(e)}")
        return None


def select_depart_flight_difference(depart_taiwan_date, flight_depart_taoyuan,logger):
    logger.info("Start Fetching Depart Flight Difference from MongoDB")
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
            'airline': {
                '$elemMatch': {
                    'airline_code': flight_depart_taoyuan
                }
            },
            'updated_at': {
                '$gt': depart_taiwan_date
        }
        }
        result = client['flying_high']['flight_depart2'].find_one(
        filter=filter,
        sort=[('updated_at', DESCENDING)]
        )
        return result
    except Exception as e:
        logger.error(f"Error in select_depart_flight_difference: {str(e)}")
        return None