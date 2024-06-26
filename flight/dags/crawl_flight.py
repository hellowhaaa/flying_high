from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta
import pendulum
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from pymongo.mongo_client import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import pytz
import os
import datetime
import logging
from selenium import webdriver
import boto3
import json
from botocore.exceptions import ClientError
import requests
import certifi

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
DEPART_API_ENDPOINT  = 'https://www.flyinghigh.live/send_depart_email'
ARRIVE_API_ENDPOINT = 'https://www.flyinghigh.live/send_arrive_email'
import os


def depart_flight():
    driver = set_up_driver() 
    url = 'https://www.taoyuan-airport.com/flight_depart?k=&time=all'
    driver.get(url)
    try:
        for i in range(2, 310):
            crawled_data = crawl_data(i, driver, depart = True)
            if not crawled_data:
                break
            insert_mongodb_atlas(crawled_data, 'flight_depart2')
            # back_up_to_s3(crawled_data)
            if crawled_data['status'] == '預計時間變更.' or crawled_data['status'] == '時間未定' or crawled_data['status'] == '取消':
                inform_depart_flight_user(crawled_data)
    except Exception as e:
        logging.error("Error---->: " + str(e))
    finally:
        driver.quit()  
        

def arrive_flight():
    driver = set_up_driver()
    url = 'https://www.taoyuan-airport.com/flight_arrival?k=&time=all'
    driver.get(url)
    try:
        for i in range(185, 310):
            crawled_data = crawl_data(i, driver, depart = False)
            if not crawled_data:
                break
            insert_mongodb_atlas(crawled_data, 'flight_arrive2')
            if crawled_data['status'] == '預計時間變更.' or crawled_data['status'] == '時間未定' or crawled_data['status'] == '取消':
                inform_arrive_flight_user(crawled_data)
            # back_up_to_s3(crawled_data)
    except Exception as e:
        logging.error("Error---->: " + str(e))
    finally:
        driver.quit()  

def set_up_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Remote(
        command_executor='http://remote_chromedriver:4444/wd/hub',
        keep_alive=True,
        options=options 
    )
    return driver


def inform_arrive_flight_user(crawled_data):
    airlines = crawled_data['airline']
    scheduled_arrive_time = crawled_data['scheduled_arrive_time']
    status = crawled_data['status']
    actual_arrive_time = crawled_data['actual_arrive_time'] if crawled_data['actual_arrive_time'] != "" else None
    logging.info("Actual Arrive Time: %s", actual_arrive_time)
    if actual_arrive_time is not None: # check if the flight has been canceled or time is fixed
        train_ls = []
        actual_arrive_time = datetime.datetime.strptime(actual_arrive_time, "%H:%M").time()
        for airline in airlines:
            airline_code = airline['airline_code']
            send_email_dic = select_user_flight(airline_code, 'flight_arrive_taoyuan', 'arrive_email_send', 'arrive_taiwan_date')
            if len(send_email_dic) != 0: # check if there are users need to be send email (List)
                logging.info("Who need to be notified: %s", send_email_dic)
                hsr_station = send_email_dic[0]['hsr_station']
                train_time = select_hsr_train(hsr_station)
                logging.info("Train time: %s", train_time)
                if train_time is not None: # check if there are trains available
                    for each_train in train_time['train_item']:
                        train_departure_time_str = each_train['departure_time']
                        if train_departure_time_str: # departure_time could be None
                            train_departure_time = datetime.datetime.strptime(train_departure_time_str, "%H:%M").time()
                            if is_within_five_hours(actual_arrive_time, train_departure_time):
                                train_destination_time = each_train['destination_time']
                                non_reserved_car = each_train['non_reserved_Car']
                                train_id = each_train['id']
                                formatted_time_str = train_departure_time.strftime("%H:%M")
                                train_ls.append((train_id,formatted_time_str, train_destination_time, non_reserved_car))
                    logging.info("Train list: %s", train_ls)
                    username = send_email_dic[0]['username']
                    user_info = select_user_email(username)
                    logging.info("User Information: %s", user_info)
                    if user_info is not None:
                        email = user_info['email']
                        actual_arrive_time = actual_arrive_time.strftime("%H:%M") if actual_arrive_time else None
                        data = {'email': email,
                                'scheduled_arrive_time':scheduled_arrive_time,
                                'status':status,
                                'airline_code':airline_code,
                                'username':username,
                                'train_ls':train_ls,
                                "actual_arrive_time":actual_arrive_time  # Could be None
                            }
                        logging.info("Data post to API: %s", data)
                        try:
                            headers = {'Content-Type': 'application/json'}
                            response = requests.post(url=ARRIVE_API_ENDPOINT, data=json.dumps(data), headers=headers, verify=certifi.where())
                            response_text = response.text
                            logging.info("Response after Post: %s", response_text)
                            response.raise_for_status()
                        except requests.exceptions.HTTPError as err:
                            logging.error(f"HTTP error occurred: {err}")
                        except requests.exceptions.ConnectionError as err:
                            logging.error(f"Connection error occurred: {err}")
                        except Exception as err:
                            logging.error(f"An error occurred: {err}")
                
            
def inform_depart_flight_user(crawled_data):
    airlines = crawled_data['airline']
    scheduled_depart_time = crawled_data['scheduled_depart_time']
    status = crawled_data['status']
    for airline in airlines:
        airline_code = airline['airline_code']
        send_email_dic = select_user_flight(airline_code, 'flight_depart_taoyuan', 'depart_email_send', 'depart_taiwan_date')
        if send_email_dic is not None: # check if there are users need to be send email
            for col in send_email_dic:
                username = col['username']
                logging.info("Who need to be notified: %s", username)
                user_info = select_user_email(username)
                if user_info is not None:
                    email = user_info['email']
                    data = {'email': email,
                            'scheduled_depart_time':scheduled_depart_time,
                            'status':status,
                            'airline_code':airline_code,
                            'username':username
                        }
                    logging.info("Data post to API: %s", data)
                    try:
                        response = requests.post(url=DEPART_API_ENDPOINT, data=data, verify=certifi.where())
                        response_text = response.text
                        logging.info("Response after Post: %s", response_text)
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as err:
                        logging.error(f"HTTP error occurred: {err}")
                    except requests.exceptions.ConnectionError as err:
                        logging.error(f"Connection error occurred: {err}")
                    except Exception as err:
                        logging.error(f"An error occurred: {err}")
            
            
def select_user_flight(airline_code, flight_taoyuan, email_send, taiwan_date):
    logging.info("Start to get username for specific flight which assigned for today.")
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        taiwan_tz = pytz.timezone('Asia/Taipei')
        #  Midnight of today
        tw_now = datetime.datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime.datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        # UTC Time
        utc_midnight = tw_midnight.astimezone(pytz.utc)
        logging.info("User's UTC time: %s", utc_midnight)
        # 找出有登記 此飛機 且出發日期為今天 （utc時間）的 user
        filter = {
            flight_taoyuan: airline_code,
            'flight_change': True,
            email_send: False,
            taiwan_date: {
                '$eq': utc_midnight
            }
        }
        result = client['flying_high']['user_flight'].find(
        filter=filter)
        result = list(result)
        return result #list
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)

def select_user_email(username):
    logging.info("Start to get user email.")
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
        'username': username
        }
        result = client['flying_high']['user'].find_one(
        filter=filter
        )   
        return result # dict      
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)

def crawl_data(i, driver, depart):
    try:
        # taiwan_title_time
        taiwan_title_time = '//*[@id="print"]/p[2]'
        taiwan_title_time_element = get_taiwan_title_time(taiwan_title_time, driver)

        # scheduled_depart_time
        scheduled_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[1]/span[2]'
        if get_scheduled_time(scheduled_time, driver):
            scheduled_time_element = get_scheduled_time(scheduled_time, driver)
        else:
            return False
            
        # actual_depart_time
        actual_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[8]/span[2]'
        actual_time_element = get_actual_time(actual_time, driver)

        # destination
        destination = f'//*[@id="print"]/ul[2]/li[{i}]/div[2]/p[2]'
        destination_element = get_destination(destination, driver)

        # airlines
        airline = f'//*[@id="print"]/ul[2]/li[{i}]/div[3]'
        alphabet_ls = get_airlines(airline, driver)

        # terminal
        terminal = f'//*[@id="print"]/ul[2]/li[{i}]/div[4]'
        terminal_element = get_terminal(terminal, driver)

        # gate
        gate = f'//*[@id="print"]/ul[2]/li[{i}]/div[5]'
        gate_element = get_gate(gate, driver)

        # status
        status = f'//*[@id="print"]/ul[2]/li[{i}]/div[7]/p'
        status_element = get_status(status, driver)
        

        # time_difference
        scheduled_time = ''
        actual_time = ''
        if depart:
            time_diff_minute = calculate_time_diff(actual_time_element, scheduled_time_element)
            scheduled_time = 'scheduled_depart_time'
            actual_time = 'actual_depart_time'
        else:
            scheduled_time = 'scheduled_arrive_time'
            actual_time = 'actual_arrive_time'
            time_diff_minute = None
            
        json_format = {
                    "taiwan_title_time": taiwan_title_time_element,  
                    "airline": alphabet_ls,
                    scheduled_time: scheduled_time_element,
                    actual_time: actual_time_element,
                    "destination": destination_element,
                    "terminal": terminal_element,
                    "gate": gate_element,
                    "status": status_element,
                    "time_difference": time_diff_minute
                }
        return json_format
        
        
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)        



def get_taiwan_title_time(taiwan_title_time, driver):
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, taiwan_title_time)))
        taiwan_title_time_element = driver.find_element(By.XPATH, taiwan_title_time).text.strip()
        logging.info(f"taiwan_title_time: {taiwan_title_time_element}")
        return taiwan_title_time_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. taiwan_title_time not found", exc_info=True)


def get_airlines(airline, driver):
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, airline)))
        airline_element = driver.find_element(By.XPATH, airline).text.strip()
        flight = airline_element.split()
        alphabet_ls= []
        for i in range(len(flight)):
            airline_dict = {}
            if i %2 == 0:
                airline_dict['airline_name'] = flight[i]
                airline_dict['airline_code'] = flight[i+1]
                alphabet_ls.append(airline_dict)
        logging.info(f"airline: {alphabet_ls}")
        return alphabet_ls
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. airline not found", exc_info=True)
    

def get_actual_time(actual_time, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, actual_time)))
        actual_time_element = driver.find_element(By.XPATH, actual_time).text.strip()
        logging.info(f"actual_time: {actual_time_element}")
        return actual_time_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. actual_time not found", exc_info=True) 


def get_scheduled_time(scheduled_time, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, scheduled_time)))
        scheduled_time_element = driver.find_element(By.XPATH, scheduled_time).text.strip()
        logging.info(f"scheduled_time: {scheduled_time_element}")
        return scheduled_time_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. scheduled_time not found", exc_info=True)
        return False


def get_destination(destination, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, destination)))
        destination_element = driver.find_element(By.XPATH, destination).text.strip()
        logging.info(f"destination: {destination_element}")
        return destination_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. destination not found", exc_info=True) 


def get_terminal(terminal, driver):
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, terminal)))
        terminal_element = driver.find_element(By.XPATH, terminal).text.strip()
        logging.info(f"terminal: {terminal_element}")
        return terminal_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. terminal not found", exc_info=True)     
    
    
def get_gate(gate, driver):
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, gate)))
        gate_element = driver.find_element(By.XPATH, gate).text.strip()
        logging.info(f"gate: {gate_element}")
        return gate_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. gate not found", exc_info=True) 
    
    
def get_status(status, driver):
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, status)))
        status_element = driver.find_element(By.XPATH, status).text.strip()
        logging.info(f"status: {status_element}")
        return status_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. status not found", exc_info=True)
    
    
def insert_mongodb_atlas(crawled_data, collection_name):
    load_dotenv()
    uri = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(uri)
    db = client['flying_high']
    collection = db[collection_name]
    time_mapping = {
        'flight_depart2': ('scheduled_depart_time', 'actual_depart_time'),
        'flight_arrive2': ('scheduled_arrive_time', 'actual_arrive_time')
    }
    scheduled_time, actual_time = time_mapping.get(collection_name, ('', ''))
        
    try:
        result = collection.update_many(
            {
                "taiwan_title_time": crawled_data['taiwan_title_time'],  
                "airline": crawled_data['airline'] 
            },
            {
                "$set": {
                    scheduled_time: crawled_data[scheduled_time],
                    actual_time: crawled_data[actual_time],
                    "destination": crawled_data['destination'],
                    "airline": crawled_data['airline'],
                    "terminal": crawled_data['terminal'],
                    "gate": crawled_data['gate'],
                    "status": crawled_data['status'],
                    "time_difference": crawled_data['time_difference'],
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


def back_up_to_s3(crawled_data):
    load_dotenv()
    bucket_name = os.getenv('BUCKET_NAME_flying_high')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_region = os.getenv('S3_BUCKET_REGION')
    
    # S3 client configuration
    s3_client = boto3.client(
        's3',
        region_name=bucket_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # folder name
    taiwan_time_split = crawled_data['taiwan_title_time'].split("機")[1].split(" (")[0].strip().split("/")
    taiwan_time_file = f"depart/{taiwan_time_split[0]}-{taiwan_time_split[1]}-{taiwan_time_split[2]}"
    back_up_data = crawled_data
    try:
        airline_code = ""
        for flight in crawled_data['airline']:
            airline_code += flight['airline_code']
            airline_code += "_"
            key = f"{taiwan_time_file}_{airline_code}.json"
            exists = check_file_exists(s3_client, bucket_name, key)
            create_or_update_json(bucket_name, key, back_up_data, exists,s3_client)
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)


def check_file_exists(s3_client, bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        return False
    
    
def create_or_update_json(bucket_name, key, data, exists, s3_client):
    if not exists:
        data['created_at'] = datetime.datetime.utcnow()  

    data['updated_at'] = datetime.datetime.utcnow() 
    json_data = json.dumps(data, ensure_ascii=False, default=str)

    try:
        s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=key)
        print("Data uploaded to S3 successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def calculate_time_diff(actual_depart_time_element, scheduled_depart_time_element):
    if actual_depart_time_element != "":
        time_diff= ""
        time_condition = ""
        return_dict = {}
        time_format = "%H:%M"
        right_depart_time_str = actual_depart_time_element
        left_depart_time_str = scheduled_depart_time_element
        right_depart_time = datetime.datetime.strptime(right_depart_time_str, time_format).time()
        left_depart_time = datetime.datetime.strptime(left_depart_time_str, time_format).time()
        start_time_16_00 = datetime.datetime.strptime("16:00", time_format).time()
        end_time_23_59 = datetime.datetime.strptime("23:59", time_format).time()
        start_time_00_00 = datetime.datetime.strptime("00:00", time_format).time()
        end_time_05_00 = datetime.datetime.strptime("05:00", time_format).time()
        if right_depart_time < left_depart_time:
            time_diff = datetime.datetime.combine(datetime.datetime.today(), right_depart_time) - datetime.datetime.combine(datetime.datetime.today(), left_depart_time)
            minutes_diff = time_diff.total_seconds() / 60
            if minutes_diff > -10:
                time_condition = "早出發"
                logging.info(f"{time_condition} 時間差: {-minutes_diff} minutes")
            elif start_time_16_00 <= left_depart_time <= end_time_23_59 and start_time_00_00 <= right_depart_time <= end_time_05_00:
                time_condition = "跨日"
                time_diff = (datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1), right_depart_time) - datetime.datetime.combine(datetime.datetime.today(), left_depart_time))
                logging.info(f"{time_condition} 時間差: {time_diff.total_seconds() / 60} minutes")
        else:
            time_diff = datetime.datetime.combine(datetime.datetime.today(), right_depart_time) - datetime.datetime.combine(datetime.datetime.today(), left_depart_time)
            time_condition = "正常出發"
            logging.info(f"{time_condition}的情況 時間差: {time_diff.total_seconds() / 60} minutes")
        return_dict = {"time_condition":time_condition,
                    "time_difference_min":int(time_diff.total_seconds() / 60)}
        return return_dict
    return {"time_condition": "時間未定",
            "time_difference_min": None}

def select_hsr_train(hsr_station):
    try:
        logging.info("Start to get HSR train time.")
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        filter={
        'end_station': hsr_station
        }
        sort=list({
            'updated_at': -1
        }.items())
        result = client['flying_high']['hsr_time'].find_one(
        filter=filter,
        sort=sort
        )
        return result # list
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)
        
    
def is_within_five_hours(start_time, end_time):
    # check if the difference between start_time and end_time is within 5 hours
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    return 0 <= (end_minutes - start_minutes) <= 5 * 60      

default_args = {
    'owner': 'airflow',
    'depends_on_past': False, 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="flight_combine",
    schedule="*/30 * * * *",
    start_date=pendulum.datetime(2024, 4, 15, tz="UTC"),
    default_args=default_args,
    catchup=False, # 不會去執行以前的任務
    max_active_runs=1,
    tags=['flight'],
) as dag:
    task_start = EmptyOperator(
    task_id="task_start",
    dag=dag
    )
    task_end = EmptyOperator(
    task_id="task_end",
    dag=dag
    )
    
    task_depart_flight = PythonOperator(
        task_id = "depart_flight",
        python_callable=depart_flight,
        dag = dag
    )
        
    task_arrive_flight = PythonOperator(
        task_id = "arrive_flight",
        python_callable=arrive_flight,
        dag = dag        
    )
    
(task_start >> task_depart_flight >> task_end)
# (task_start >> [task_depart_flight,task_arrive_flight] >> task_end)