
from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from datetime import datetime, tzinfo, timezone
import pytz
load_dotenv()




def get_flight_time(airline_name,flight):  # airline_code 是 JL96 的組合\l
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    tw_now = datetime.now(taiwan_tz)
    tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
    utc_midnight = tw_midnight.astimezone(pytz.utc)  # UTC Time
    
    filter={
        'airline': {
            '$elemMatch': {
                airline_name: {
                    '$regex': flight
                }
            }
        },
        'updated_at': {
        '$gt': utc_midnight
    }
    }
    result = client['flying_high']['flight_arrive'].find(
    filter=filter
    )
    return list(result)

