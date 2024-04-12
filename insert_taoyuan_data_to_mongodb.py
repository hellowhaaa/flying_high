from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from configparser import ConfigParser
import os

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)


def crawl_data():
    try:
        return_ls = []
        # URL you wish to access
        flight_ls = ['CI4', 'CI51', 'CI110','CI8001']
        for flight in flight_ls :
            flight_dic = {}
            url = f'https://www.taoyuan-airport.com/flight_depart?k={flight}&time=all'

        # Use WebDriver to get page source
            driver.get(url)
        # Use the correct method to find the element
            arrival_time = '//*[@id="print"]/ul/li[2]/div[8]/span[2]'
            depart_time = '//*[@id="print"]/ul/li[2]/div[1]/span[2]'
            destination = '//*[@id="print"]/ul/li[2]/div[2]/p[2]'
            airline1 = '//*[@id="print"]/ul/li[2]/div[3]/p[1]'
            airline2 = '//*[@id="print"]/ul/li[2]/div[3]/p[2]'
            terminal = '//*[@id="print"]/ul/li[2]/div[4]'
            gate = '//*[@id="print"]/ul/li[2]/div[5]'
            status = '//*[@id="print"]/ul/li[2]/div[7]'
            # Wait for the required element to load on the page
            # ? ------ arrival_time -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, arrival_time)))
                arrival_time_element = driver.find_element(By.XPATH, arrival_time).text.strip()
                print(flight + ' arrival_time_element: ' + arrival_time_element)
            except TimeoutException:
                arrival_time_element = "Not Found"
                print(f"{flight} arrival_time_element: {arrival_time_element}") 
            # ? ------ depart_time -----
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, depart_time)))
                depart_time_element = driver.find_element(By.XPATH, depart_time).text.strip()
                print(flight+ ' depart_time_element: '+ depart_time_element)
            except TimeoutException:
                depart_time_element = "Not Found"
                print(f"{flight} depart_time_element: {depart_time_element}")   
            # ? ------ destination ------
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, destination)))
                destination_element = driver.find_element(By.XPATH, destination).text.strip()
                print(flight+ ' destination: '+ destination_element)
            except TimeoutException:
                destination_element = "Not Found"
                print(f"{flight} destination_element: {destination_element}")  
            # ? ------ airline1 ------
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, airline1)))
                airline1_element = driver.find_element(By.XPATH, airline1).text.strip()
                print(flight+ ' airline1: '+ airline1_element)
            except TimeoutException:
                airline1_element = "Not Found"
                print(f"{flight} airline1: {airline1_element}")
            # ? ------ airline2 ------
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, airline2)))
                airline2_element = driver.find_element(By.XPATH, airline2).text.strip()
                print(flight+ ' airline2: '+ airline2_element)
            except TimeoutException:
                airline2_element = None
                print(f"{flight} airline2: {airline2_element}")
            # ? ------ terminal ------   
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, terminal)))
                terminal_element = driver.find_element(By.XPATH, terminal).text.strip()
                print(flight+ ' terminal: '+ terminal_element)
            except TimeoutException:
                terminal_element = "Not Found"
                print(f"{flight} terminal: {terminal_element}")
                
            # ? ------ gate ------  
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, gate)))
                gate_element = driver.find_element(By.XPATH, gate).text.strip()
                print(flight+ ' Gate: '+ gate_element)
            except TimeoutException:
                gate_element = "Not Found"
                print(f"{flight} Gate: {gate_element}")
            # ? ------ status ------ 
            try:  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, status)))
                status_element = driver.find_element(By.XPATH, status).text.strip()
                print(flight+ ' Status: '+ status_element)
            except TimeoutException:
                status_element = "Not Found"
                print(f"{flight} Status: {status_element}")
            flight_dic = {
                "depart_time": depart_time_element,
                "arrival_time": arrival_time_element,
                "destination": destination_element,
                'airline': [airline1_element, airline2_element],
                'terminal': terminal_element,
                'gate': gate_element,
                'status': status_element    
            }
            print(flight_dic)
            return_ls.append(flight_dic)
            print('--------------------')
        return return_ls
            
    except Exception as e:
        print(f"An error occurred: {e}")
            
    finally:
        # Close the browser
        driver.quit()

def your_crawler_function():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_directory, '.config.ini')
    config = ConfigParser()
    config.read(config_file_path)
    mongo = config['MONGO']
    hostname = mongo['host']
    port = int(mongo['port'])
    # username = mongo['username']


    # Create a MongoClient instance
    conn = MongoClient(hostname, port)
    db = conn['flight']
    # Access a collection (similar to a table in relational databases)
    collection = db['depart']

    mongo_dblist = conn.list_database_names()
    if "flight" in mongo_dblist:
        print("flight database 已存在！")
    else:
        print('flight database 不存在')
    # Your crawling logic here
    data = crawl_data()  # replace with your own crawling process
    for _ in data:
    # Connection to MongoDB
    # client = MongoClient('your_mongodb_uri')
    # db = client.your_database
    # collection = db.your_collection

    # Insert data into MongoDB
        collection.insert_one(_)
    
crawl_data()
# your_crawler_function()    