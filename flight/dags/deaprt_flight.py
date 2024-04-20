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

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

def crawl_data():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Set command timeout to 60 seconds
        capabilities = options.to_capabilities()
        driver = webdriver.Remote(
            command_executor='http://remote_chromedriver:4444/wd/hub',
            keep_alive=True,
            options=options # Increase the timeout to 60 seconds
        )
        url = 'https://www.taoyuan-airport.com/flight_depart?k=&time=all'
        driver.get(url)
        for i in range(2,500):
            taiwan_title_time = '//*[@id="print"]/p[2]'
            scheduled_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[1]/span[2]'
            actual_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[8]/span[2]'
            destination = f'//*[@id="print"]/ul[2]/li[{i}]/div[2]/p[2]'
            airline = f'//*[@id="print"]/ul[2]/li[{i}]/div[3]'
            terminal = f'//*[@id="print"]/ul[2]/li[{i}]/div[4]'
            gate = f'//*[@id="print"]/ul[2]/li[{i}]/div[5]'
            status = f'//*[@id="print"]/ul[2]/li[{i}]/div[7]/p'
            # ? ------ taiwan_title_time ------  
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, taiwan_title_time)))
                taiwan_title_time_element = driver.find_element(By.XPATH, taiwan_title_time).text.strip()
                logging.info(f"taiwan_title_time: {taiwan_title_time_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. taiwan_title_time not found", exc_info=True)     
            # ? ------ airline ------
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
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. airline not found", exc_info=True) 
                break
                # ? ------ actual_depart_time -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, actual_depart_time)))
                actual_depart_time_element = driver.find_element(By.XPATH, actual_depart_time).text.strip()
                logging.info(f"actual_arrive_time: {actual_depart_time_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. actual_arrive_time not found", exc_info=True) 
                break 
            # ? ------ scheduled_depart_time -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, scheduled_depart_time)))
                scheduled_depart_time_element = driver.find_element(By.XPATH, scheduled_depart_time).text.strip()
                logging.info(f"scheduled_depart_time: {scheduled_depart_time_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. scheduled_depart_time not found", exc_info=True) 
                
            # ? ------ destination ------
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, destination)))
                destination_element = driver.find_element(By.XPATH, destination).text.strip()
                logging.info(f"destination: {destination_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. destination not found", exc_info=True) 
            # ? ------ terminal ------   
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, terminal)))
                terminal_element = driver.find_element(By.XPATH, terminal).text.strip()
                logging.info(f"terminal: {terminal_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. terminal not found", exc_info=True)     
            # ? ------ gate ------  
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, gate)))
                gate_element = driver.find_element(By.XPATH, gate).text.strip()
                logging.info(f"gate: {gate_element}")
            except TimeoutException as e:
                logging.error(f"An exception occurred: {str(e)}. gate not found", exc_info=True) 
            # ? ------ status ------ 
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, status)))
                status_element = driver.find_element(By.XPATH, status).text.strip()
                logging.info(f"status: {status_element}")
            except TimeoutException:
                logging.error(f"An exception occurred: {str(e)}. status not found", exc_info=True)
            collection = insert_mongodb_atlas()
            try:
                result = collection.update_many(
                    {
                        "taiwan_title_time": taiwan_title_time_element,  # 符合的日期時間
                        "airline": alphabet_ls  # 符合的航空公司
                    },
                    {
                        "$set": {
                            "scheduled_depart_time": scheduled_depart_time_element,
                            "actual_depart_time": actual_depart_time_element,
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
            print('--------------------')
    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}", exc_info=True)        
    finally:
        driver.quit()
    
        
def insert_mongodb_atlas():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    # try:
    #     conn.admin.command('ping')
    #     print("Pinged your deployment. You successfully connected to MongoDB!")
    # except Exception as e:
    #     print(e)
    db = client['flying_high']
    collection = db['flight_depart2']
    return collection   

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
        python_callable=crawl_data,
        dag = dag  
    )
    
(task_start >> task_depart_flight >> task_end)