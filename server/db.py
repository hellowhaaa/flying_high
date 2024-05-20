import pytz
from config import Config
from datetime import datetime, timezone
from pymongo import MongoClient,DESCENDING
from werkzeug.security import generate_password_hash, check_password_hash

url = Config.MONGODB_URI_FLY
client = MongoClient(url)
taiwan_tz = pytz.timezone('Asia/Taipei')
tw_now = datetime.now(taiwan_tz)
tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
utc_midnight = tw_midnight.astimezone(pytz.utc)


def get_arrive_flight_time(flight, logger):
    logger.info("Start Fetching Arrive Flight Time from MongoDB")
    try:
        
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
        result = client['flying_high']['flight_depart2'].find()
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_user_depart_flight_code: {str(e)}")
        return None


def select_user_arrive_flight_code(logger):
    logger.info("Start Fetching User's All Arrive Flight Time from MongoDB")
    try:
        result = client['flying_high']['flight_arrive2'].find()
        return list(result)
    except Exception as e:
        logger.error(f"Error in select_user_arrive_flight_code: {str(e)}")
        return None


def select_insurance_amount(plan, insurance_amount,insurance_company, insurance_days, logger):
    logger.info("Start Fetching Insurance Amount from MongoDB")
    try:
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
    
    
# update--
def update_user_insurance(username, insurance_company, plan, insured_amount, days, logger):
    logger.info("Start Updating User Insurance to MongoDB")
    try:
        filter = {"username": username}

        update = {
            "$set": {
                "insurance_company": insurance_company,
                "plan": plan,
                "insured_amount": insured_amount,
                "days": days,
                "updated_at": datetime.now(timezone.utc)
            },
            "$setOnInsert": {
                "created_at": datetime.now(timezone.utc)  # Only set this field on insert (upsert)
            }
        }
        result = client['flying_high']['user_insurance'].update_many(
            filter=filter,
            update=update,
            upsert=True)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": result.upserted_id
        }
    except Exception as e:
        logger.error(f"Error in update_user_insurance: {str(e)}")
        return None


def update_user_flight_info(username, depart_taiwan_date, arrive_taiwan_date, flight_depart_taoyuan,
                            flight_arrive_taoyuan, logger):
    logger.info("Start Updating User Flight Info to MongoDB")
    try:
        taiwan_tz = pytz.timezone('Asia/Taipei')
        # UTC time for departure flight from Taoyuan Airport
        start_date_obj = datetime.strptime(depart_taiwan_date, '%Y-%m-%d')
        start_date_tw_midnight = taiwan_tz.localize(
            datetime(start_date_obj.year, start_date_obj.month, start_date_obj.day, 0, 0, 0))
        start_date_utc_midnight = start_date_tw_midnight.astimezone(pytz.utc)
        # UTC time fot arrival flight at Taoyuan Airport
        end_date_obj = datetime.strptime(arrive_taiwan_date, '%Y-%m-%d')
        end_date_tw_midnight = taiwan_tz.localize(
            datetime(end_date_obj.year, end_date_obj.month, end_date_obj.day, 0, 0, 0))
        end_date_utc_midnight = end_date_tw_midnight.astimezone(pytz.utc)

        filter = {"username": username}
        update = {
            "$set": {
                "depart_taiwan_date": start_date_utc_midnight,
                "arrive_taiwan_date": end_date_utc_midnight,
                "flight_depart_taoyuan": flight_depart_taoyuan,
                "flight_arrive_taoyuan": flight_arrive_taoyuan,
                "updated_at": datetime.now(timezone.utc)
            },
            "$setOnInsert": {
                "created_at": datetime.now(timezone.utc)  # Only set this field on insert (upsert)
            }
        }
        result = client['flying_high']['user_flight'].update_many(
            filter=filter,
            update=update,
            upsert=True)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": result.upserted_id
        }
    except Exception as e:
        logger.error(f"Error in update_user_flight_info: {str(e)}")
        return None


def update_user_notify(username, flight_change, flight_delay, hsr, logger):
    logger.info("Start Updating User Notify to MongoDB")
    try:
        filter = {"username": username}

        update = {
            "$set": {
                "flight_change": flight_change,
                "flight_delay": flight_delay,
                "hsr_station": hsr,
                "updated_at": datetime.now(timezone.utc)
            },
            "$setOnInsert": {
                "depart_email_send": False,
                "arrive_email_send": False,
                "created_at": datetime.now(timezone.utc)  # Only set this field on insert (upsert)
            }
        }
        result = client['flying_high']['user_notify'].update_many(
            filter=filter,
            update=update,
            upsert=True)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": result.upserted_id
        }
    except Exception as e:
        logger.error(f"Error in update_user_notify: {str(e)}")
        return None


def update_depart_email_send(username, logger):
    logger.info("Start Updating Depart Email Function Set False to True in MongoDB")
    try:
        filter = {"username": username}
        update = {
            "$set": {
                "depart_email_send": True
            }
        }
        result = client['flying_high']['user_notify'].update_one(
            filter=filter,
            update=update
        )
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }
    except Exception as e:
        logger.error(f"Error in update_depart_email_send: {str(e)}")
        return None


def update_arrive_email_send(username, logger):
    logger.info("Start Updating Arrive Email Function Set False to True in MongoDB")
    try:
        filter = {"username": username}
        update = {
            "$set": {
                "arrive_email_send": True
            }
        }
        result = client['flying_high']['user_notify'].update_one(
            filter=filter,
            update=update
        )
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }
    except Exception as e:
        logger.error(f"Error in update_arrive_email_send: {str(e)}")
        return None
    
    
    
# user--register
def create_user(username, password, email, address):
    hashed_password = generate_password_hash(password)
    return {
        'username': username,
        'password': hashed_password,
        'email': email,
        'address': address,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

# Return True if the username already exists in the database
def same_username(username):
    collection = client['flying_high']['user']  
    return collection.find_one({'username': username}) is not None


def check_user_credentials(username, password):
    collection = client['flying_high']['user']
    user = collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return user
    return None

def insert_new_user(user, logger):
    logger.info("Start Inserting New User to MongoDB")
    collection = client['flying_high']['user']
    result = collection.insert_one(user)
    return result.inserted_id