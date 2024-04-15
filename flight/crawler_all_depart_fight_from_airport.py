from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import os
import datetime
from dotenv import load_dotenv
load_dotenv()
# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

def crawl_all():
    url = 'https://www.taoyuan-airport.com/flight_depart?k=&time=all'
    driver.get(url)
    for i in range(2,84):
        all_first_xpath = '//*[@id="print"]/ul[2]/li[2]/div[1]/span[2]'
    

def crawl_data():
    try:
        url = 'https://www.taoyuan-airport.com/flight_depart?k=&time=all'
        driver.get(url)
        for i in range(2,500):
            print(i)
        # Use the correct method to find the element
            taiwan_title_time = '//*[@id="print"]/p[2]'
            scheduled_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[1]/span[2]'
            actual_depart_time = f'//*[@id="print"]/ul[2]/li[{i}]/div[8]/span[2]'
            # next_sch_path = '//*[@id="print"]/ul[2]/li[3]/div[1]/span[2]'
            # next_act_path = '//*[@id="print"]/ul[2]/li[3]/div[8]/span[2]'
        
            destination = f'//*[@id="print"]/ul[2]/li[{i}]/div[2]/p[2]'
            # next_destination = '//*[@id="print"]/ul[2]/li[3]/div[2]/p[2]'
     
            airline = f'//*[@id="print"]/ul[2]/li[{i}]/div[3]'
            terminal = f'//*[@id="print"]/ul[2]/li[{i}]/div[4]'
            gate = f'//*[@id="print"]/ul[2]/li[{i}]/div[5]'
            status = f'//*[@id="print"]/ul[2]/li[{i}]/div[7]/p'
            # Wait for the required element to load on the page\\\
            # ? ------ taiwan_title_time ------
                
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, taiwan_title_time)))
                taiwan_title_time_element = driver.find_element(By.XPATH, taiwan_title_time).text.strip()
                print(taiwan_title_time_element)
            except TimeoutException:
                taiwan_title_time_element = "Not Found"
                print(f"airlines: {taiwan_title_time_element}")   

                
            # ? ------ airline ------
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, airline)))
                airline_element = driver.find_element(By.XPATH, airline).text.strip()
                flight2 = airline_element.split()
                flight = airline_element
                print(flight)
                alphabet_ls= []
                for i in range(len(flight2)):
                    airline_dict = {}
                    if i %2 == 0:
                        airline_dict[flight2[i]] = flight2[i+1]
                        alphabet_ls.append(airline_dict)
                print(alphabet_ls)
            except TimeoutException:
                airline_element = "Not Found"
                print(f"airlines: {airline_element}")   
                # ? ------ actual_depart_time -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, actual_depart_time)))
                actual_depart_time_element = driver.find_element(By.XPATH, actual_depart_time).text.strip()
                print(flight + ' actual_depart_time: ' + actual_depart_time_element)
            except TimeoutException:
                actual_depart_time_element = "Not Found"
                print(f"actual_depart_time: {actual_depart_time_element}")
                break 
            # ? ------ scheduled_depart -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, scheduled_depart_time)))
                scheduled_depart_time_element = driver.find_element(By.XPATH, scheduled_depart_time).text.strip()
                print(flight+ ' scheduled_depart_time: '+ scheduled_depart_time_element)
            except TimeoutException:
                scheduled_depart_time_element = "Not Found"
                print(f"scheduled_depart_time: {scheduled_depart_time_element}")
                
            # ? ------ destination ------
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, destination)))
                destination_element = driver.find_element(By.XPATH, destination).text.strip()
                print(flight+ ' destination: '+ destination_element)
            except TimeoutException:
                destination_element = "Not Found"
                print(f"destination_element: {destination_element}")  
            
                
                
            # # ? ------ terminal ------   
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, terminal)))
                terminal_element = driver.find_element(By.XPATH, terminal).text.strip()
                print(flight+ ' terminal: '+ terminal_element)
            except TimeoutException:
                terminal_element = "Not Found"
                print(f"terminal: {terminal_element}")
                
            # # ? ------ gate ------  
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, gate)))
                gate_element = driver.find_element(By.XPATH, gate).text.strip()
                print(flight+ ' Gate: '+ gate_element)
            except TimeoutException:
                gate_element = "Not Found"
                print(f"Gate: {gate_element}")
            # ? ------ status ------ 
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, status)))
                status_element = driver.find_element(By.XPATH, status).text.strip()
                if status_element == '出發 已飛':
                    status_element = '0' # 
                print(flight+ ' Status: '+ status_element)
            except TimeoutException:
                status_element = "Not Found"
                print(f"Status: {status_element}")
            
            collection = insert_mongodb_atlas()
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
            print(f'Matched count: {result.matched_count}')
            print(f'Modified count: {result.modified_count}')
            if result.upserted_id:
                print(f'Upserted ID: {result.upserted_id}')  # 新建 document 的 ID

            print('--------------------')
    except Exception as e:
        print(f"An error occurred: {e}")
            
    finally:
        # Close the browser
        driver.quit()
        # os.system("pkill chromedriver")
        
def insert_mongodb_atlas():
    uri = os.getenv("MONGODB_URI")
    conn = MongoClient(uri)
    try:
        conn.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # Create a MongoClient instance
    db = conn['flying_high']
    # Access a collection (similar to a table in relational databases)
    collection = db['flight_depart']

    mongo_dblist = conn.list_database_names()
    if "flying_high" in mongo_dblist:
        print("flying_high database 已存在！")
    else:
        print('flying_high database 不存在')
    
    return collection
    
crawl_data()        