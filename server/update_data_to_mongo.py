from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from datetime import datetime, tzinfo, timezone, timedelta
import pytz
load_dotenv()


def update_user_insurance():
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    
    try:
        result = collection.update_many(
            {
                "taiwan_title_time": taiwan_title_time_element,  # 符合的日期時間
                "airline": alphabet_ls  # 符合的航空公司
            },
            {
                "$set": {
                    "scheduled_arrive_time": scheduled_arrive_time_element,
                    "actual_arrive_time": actual_arrive_time_element,
                    "destination": destination_element,
                    "airline": alphabet_ls,
                    "terminal": terminal_element,
                    "gate": gate_element,
                    "status": status_element,
                    "updated_at": datetime.datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.datetime.utcnow()  # 只有在首次創建時 insert
                }
            },
            upsert=True  # 如果沒有找到 match 'taiwan_title_time', 'airline'的 document，就 insert 一個新的
        )
        logging.info(f"Matched count: {result.matched_count}")
        logging.info(f"Modified count: {result.modified_count}")
        if result.upserted_id:
            logging.info(f'Upserted ID: {result.upserted_id}')  # 新建 document 的 ID
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True) 



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
            "updated_at": datetime.datetime.utcnow()
        },
        "$setOnInsert": {
            "created_at": datetime.datetime.utcnow()  # Only set this field on insert (upsert)
        }
    }
    result = client['flying_high']['user_insurance'].update_many(
    filter=filter,
    update = update,
    upsert = True)
    # Returns the result of the update operation
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": result.upserted_id
    }
    


