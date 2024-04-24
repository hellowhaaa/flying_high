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
    


