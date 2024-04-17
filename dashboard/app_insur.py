import streamlit as st
import pandas as pd
import pymongo  
from pymongo import MongoClient
import datetime
import time
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pymongo

def init_connection():
    # Properly format the connection string to use variables from st.secrets
    db_username = st.secrets["mongo"]["db_username"]
    db_pswd = st.secrets["mongo"]["db_pswd"]
    cluster_name = st.secrets["mongo"]["cluster_name"]
    
    connection_string = f"mongodb+srv://{db_username}:{db_pswd}@{cluster_name}.ddhtgvi.mongodb.net/?retryWrites=true&w=majority"
    print("Using connection string:", connection_string)  # Debugging line

    client = pymongo.MongoClient(connection_string)
    print(client)
    # try:
    #     client.admin.command('ping')
    #     st.success("Successfully connected to MongoDB!")
    # except Exception as e:
    #     st.error(f"Failed to connect to MongoDB: {e}")
    return client

mongo_client = init_connection()

db = mongo_client['flying_high']   

def get_data():
    # collection = db['flight_depart'].find({"status":"0"})
    collection = db['insurance_fubung'].find()
    
    return pd.DataFrame(collection)

data = get_data()


st.write(data)