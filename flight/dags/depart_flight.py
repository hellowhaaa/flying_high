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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
import datetime
import logging
from airflow.utils.dates import days_ago

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import boto3
import json
from botocore.exceptions import ClientError

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def main_steps():
    for i in range(2, 310):
        crawled_data = crawl_data(i)
        insert_mongodb_atlas(crawled_data)
        # back_up_to_s3(crawled_data)
    

def crawl_data(i):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    capabilities = options.to_capabilities()
    driver = webdriver.Remote(
        command_executor='http://remote_chromedriver:4444/wd/hub',
        keep_alive=True,
        options=options 
    )

    url = 'https://www.taoyuan-airport.com/flight_depart?k=&time=all'
    driver.get(url)

    try:
    
        # taiwan_title_time
        taiwan_title_time = '//*[@id="print"]/p[2]'
        taiwan_title_time_element = get_taiwan_title_time(taiwan_title_time, driver)

        # scheduled_depart_time
        scheduled_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[1]/span[2]'
        scheduled_depart_time_element = get_scheduled_depart_time(scheduled_depart_time, driver)

        # actual_depart_time
        actual_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[8]/span[2]'
        actual_depart_time_element = get_actual_depart_time(actual_depart_time, driver)

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
        time_diff_minute = calculate_time_diff(actual_depart_time_element, scheduled_depart_time_element)
        
        json_format = {
                    "taiwan_title_time": taiwan_title_time_element,  
                    "airline": alphabet_ls,
                    "scheduled_depart_time": scheduled_depart_time_element,
                    "actual_depart_time": actual_depart_time_element,
                    "destination": destination_element,
                    "terminal": terminal_element,
                    "gate": gate_element,
                    "status": status_element,
                    "time_difference": time_diff_minute
                }
        return json_format
        
        
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)        
    finally:
        driver.quit()


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
        flight2 = airline_element.split()
        flight = airline_element
        alphabet_ls= []
        for i in range(len(flight2)):
            airline_dict = {}
            if i %2 == 0:
                airline_dict['airline_name'] = flight2[i]
                airline_dict['airline_code'] = flight2[i+1]
                alphabet_ls.append(airline_dict)
        logging.info(f"airline: {alphabet_ls}")
        return alphabet_ls
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. airline not found", exc_info=True)
    

def get_actual_depart_time(actual_depart_time, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, actual_depart_time)))
        actual_depart_time_element = driver.find_element(By.XPATH, actual_depart_time).text.strip()
        logging.info(f"actual_arrive_time: {actual_depart_time_element}")
        return actual_depart_time_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. actual_arrive_time not found", exc_info=True) 


def get_scheduled_depart_time(scheduled_depart_time, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, scheduled_depart_time)))
        scheduled_depart_time_element = driver.find_element(By.XPATH, scheduled_depart_time).text.strip()
        logging.info(f"scheduled_depart_time: {scheduled_depart_time_element}")
        return scheduled_depart_time_element
    except TimeoutException as e:
        logging.error(f"An exception occurred: {str(e)}. scheduled_depart_time not found", exc_info=True) 


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
    
    
def insert_mongodb_atlas(crawled_data):
    load_dotenv()
    uri = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(uri)
    db = client['flying_high']
    collection = db['flight_depart2']
    try:
        result = collection.update_many(
            {
                "taiwan_title_time": crawled_data['taiwan_title_time'],  
                "airline": crawled_data['airline'] 
            },
            {
                "$set": {
                    "scheduled_depart_time": crawled_data['scheduled_depart_time'],
                    "actual_depart_time": crawled_data['actual_depart_time'],
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
    return return_dict
        

default_args = {
    'owner': 'airflow',
    'depends_on_past': False, 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="release_depart_flight2",
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
        task_id = "insert_depart_flight_mongodb",
        python_callable=main_steps,
        dag = dag  
    )
    
(task_start >> task_depart_flight >> task_end)