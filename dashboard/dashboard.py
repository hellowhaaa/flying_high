import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from streamlit_navigation_bar import st_navbar

log_path = os.path.join(os.getcwd(), 'logs')
# Ensure the directory exists
os.makedirs(log_path, exist_ok=True)
# Initialize logging handler
print('log_path:', log_path)
file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=10240, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
# Creates a new logger instance
logger = logging.getLogger('dashboard')
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
def navbar():
    st.markdown("""
        <style>
        .navbar {
            display: flex;
            justify-content: center;
            
            padding: 10px;
        }
        .navbar ul {
            list-style: none;
            display: flex;
            gap: 20px;
        }
        .navbar li {
            display: inline;
        }
        .navbar a {
            text-decoration: none;
            color: #4F4F4F	;
            font-size: 18px;
            font-weight: bold;
        }
        .navbar a:hover {
            text-decoration: underline;
        }
        </style>
        <nav class="navbar">
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#dropdown">Dropdown</a></li>
            </ul>
        </nav>
    """, unsafe_allow_html=True)

# Display the navigation bar at the top of the Streamlit app



def get_on_time_performance_by_week(week):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2'] 
        # 取幾週的資料
        one_week_ago = datetime.utcnow() - timedelta(days=7*int(week))
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None

# Define the aggregation pipeline
    pipeline = [
        {"$match": {
            "created_at": {"$gte": one_week_ago}
        }},
        {"$group": {
            "_id": None,
            "total_flights": {"$sum": 1},
            "delayed_flights": {
                "$sum": {
                    "$cond": [{"$gt": ["$time_difference.time_difference_min", 0]}, 1, 0]
                }
            },
            "on_time_flights": {
                "$sum": {
                    "$cond": [{"$lte": ["$time_difference.time_difference_min", 0]}, 1, 0]
                }
            }
        }}
    ]
    try:
        result = list(collection.aggregate(pipeline))
        logger.info(f'Get on-time performance by week successfully')
        df = pd.DataFrame({
            'Week': week,
            'All On Time Depart Flights':[result[0]['on_time_flights']],
            'On Time Performance': [result[0]['on_time_flights']/result[0]['total_flights']],
            'All Delay flights': [result[0]['delayed_flights']]
        })
        logger.info(f'Get data frame successfully')
        return df
    except Exception as e:
        logger.error(f'Error aggregating data: {e}')
        return None

def get_airline_on_time_performance(airline_name):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2']
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None
    try:
        # 取幾週的資料
        current_date = datetime.utcnow()
        four_weeks_ago = current_date - timedelta(weeks=4)
        pipeline = [
            {
                "$match": {
                    "updated_at": {"$gte": four_weeks_ago, "$lte": current_date},
                    "airline.airline_name": airline_name
                }
            },
            {
                "$project": {
                    "week_difference": {
                        "$floor": {
                            "$divide": [
                                {"$subtract": [current_date, "$updated_at"]},
                                1000 * 60 * 60 * 24 * 7  # milliseconds in a week
                            ]
                        }
                    },
                    "time_difference_min": "$time_difference.time_difference_min"
                }
            },
            {
                "$group": {
                    "_id": "$week_difference",
                    "total_flights": {"$sum": 1},
                    "on_time_flights": {
                        "$sum": {
                            "$cond": [{"$lte": ["$time_difference_min", 0]}, 1, 0]
                        }
                    },
                    "delayed_flights": {
                        "$sum": {
                            "$cond": [{"$gt": ["$time_difference_min", 0]}, 1, 0]
                        }
                    }
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        results = list(collection.aggregate(pipeline))
        weeks = []
        on_time_performance = []

        for result in results:
            # Calculate the start date of the week
            week_start_date = current_date - timedelta(weeks=result['_id'])
            week_label = week_start_date.strftime('%Y-%m-%d')
            
            performance = (result['on_time_flights'] / result['total_flights']) * 100 if result['total_flights'] > 0 else 0
            weeks.append(week_label)
            on_time_performance.append(performance)

        # Create DataFrame from the lists
        df = pd.DataFrame({
            'Week Starting': weeks,
            'On-Time Performance (%)': on_time_performance
        })
        df.sort_values('Week Starting', inplace=True)
        logger.info(f'Get airline on-time performance successfully')
        return df
    except Exception as e:
        logger.error(f'Error aggregating data: {e}')
        return None

def get_destination_on_time_performance(destination):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2'] 
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None
    try:
        current_date = datetime.utcnow()
        four_weeks_ago = current_date - timedelta(weeks=4)
        pipeline = [
            {
                "$match": {
                    "updated_at": {"$gte": four_weeks_ago, "$lte": current_date},
                    "destination": destination
                }
            },
            {
                "$project": {
                    "week_difference": {
                        "$floor": {
                            "$divide": [
                                {"$subtract": [current_date, "$updated_at"]},
                                1000 * 60 * 60 * 24 * 7  # milliseconds in a week
                            ]
                        }
                    },
                    "time_difference_min": "$time_difference.time_difference_min"
                }
            },
            {
                "$group": {
                    "_id": "$week_difference",
                    "total_flights": {"$sum": 1},
                    "on_time_flights": {
                        "$sum": {
                            "$cond": [{"$lte": ["$time_difference_min", 0]}, 1, 0]
                        }
                    },
                    "delayed_flights": {
                        "$sum": {
                            "$cond": [{"$gt": ["$time_difference_min", 0]}, 1, 0]
                        }
                    }
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        results = list(collection.aggregate(pipeline))
        weeks = []
        on_time_performance = []

        for result in results:
            # Calculate the start date of the week
            week_start_date = current_date - timedelta(weeks=result['_id'])
            week_label = week_start_date.strftime('%Y-%m-%d')
            
            performance = (result['on_time_flights'] / result['total_flights']) * 100 if result['total_flights'] > 0 else 0
            weeks.append(week_label)
            on_time_performance.append(performance)

        # Create DataFrame from the lists
        df = pd.DataFrame({
            'Week Starting': weeks,
            'On-Time Performance (%)': on_time_performance
        })
        df.sort_values('Week Starting', inplace=True)
        logger.info(f'Get destination on-time performance successfully')
        return df
    except Exception as e:
        logger.error(f'Error aggregating data: {e}')
        return None
    


def select_destination():
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2'] 
        pipeline = [
            {"$group": {"_id": "$destination"}}  # Group by destination
        ]
        unique_destinations = list(collection.aggregate(pipeline))
        destinations = [doc['_id'] for doc in unique_destinations if doc['_id'] is not None]
        logger.info(f'Get all destinations successfully')
        return destinations
    except Exception as e:
        logger.error(f'Catch an error: {e}')
        return None


def select_airlines_all(week):
    try:
        load_dotenv()
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2']
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None
    try:
        one_week_ago = datetime.utcnow() - timedelta(days=7*int(week))
        pipeline = [
        {"$match": {
            "created_at": {"$gte": one_week_ago}
        }},
        {"$unwind": "$airline"},  # Unwind the airline array to access individual airline objects
        {"$group": {
            "_id": "$airline.airline_name",  # Group by airline name
            "count": {"$sum": 1},  
            "average_delay_minutes": {"$avg": "$time_difference.time_difference_min"} 
        }},
        {"$sort": {"count": -1}}   #sort by the count in descending order
        ]

        result = list(collection.aggregate(pipeline))
        df = pd.DataFrame(result)
        df.rename(columns={'_id': 'Airline', 'count': 'Flights Count', 'average_delay_minutes': 'Average Delay Minutes'}, inplace=True)
        logger.info(f'Get all airlines data successfully')
        return df
    except Exception as e:
        logger.error(f'Error aggregating data: {e}')
        return None


def select_airlines():
    try:
        url = os.getenv("MONGODB_URI_FLY")
        client = MongoClient(url)
        db = client['flying_high']
        collection = db['flight_depart2']
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None
    try:
        pipeline = [
        {"$unwind": "$airline"},  # Deconstruct the airline array
        {"$group": {
            "_id": "$airline.airline_name"  # Group by airline name to get unique names
        }}
        ]

        result = collection.aggregate(pipeline)
        unique_airline_names = [doc['_id'] for doc in result if doc['_id'] is not None]
        logger.info(f'Get all airlines successfully')
        return unique_airline_names
    except Exception as e:
        logger.error(f'Error aggregating data: {e}')
        return None


def init_db():
    try:
        load_dotenv()
        client = MongoClient(os.getenv("MONGODB_URI_FLY"))
        logger.info(f'Connected to MongoDB')
        return client['flying_high']
    except Exception as e:
        logger.error(f'Error connecting to MongoDB: {e}')
        return None


def load_destinations(collection):
    try:
        if 'destinations' not in st.session_state:
            destinations = list(collection.aggregate([{"$group": {"_id": "$destination"}}]))
            st.session_state['destinations'] = [dest['_id'] for dest in destinations if dest['_id'] is not None]
    except Exception as e:
        logger.error(f'Error loading destinations: {e}')

def load_airlines(collection):
    try:
        if 'airlines' not in st.session_state:
            airlines = list(collection.aggregate([
                {"$unwind": "$airline"},
                {"$group": {"_id": "$airline.airline_name"}}
            ]))
            st.session_state['airlines'] = [airline['_id'] for airline in airlines if airline['_id'] is not None]
    except Exception as e:
        logger.error(f'Error loading airlines: {e}')
        
# def setup_sidebar():
#     try:
#         navbar()
#         st.sidebar.header('Get Flight Punctuality')
#         # fill out the dropdown in sidebar
#         # origin = st.sidebar.selectbox('Origin', ['Taoyuan Airport', 'Song Shan Airport'])
#         destination = st.sidebar.selectbox('Destination', st.session_state.destinations)
#         airline = st.sidebar.selectbox('Airline', st.session_state.airlines)
#         weeks = st.sidebar.selectbox('Within weeks', ['1', '2', '3', '4'])
#         submit = st.sidebar.button('Submit')
#         return weeks, destination, airline, submit
#     except Exception as e:
#         logger.error(f'Error setting up sidebar: {e}')
#         return None, None, None, None, None

def main():
    try:
        
        db = init_db()
        collection = db['flight_depart2']
        
        # Load destinations and airlines
        load_destinations(collection)
        load_airlines(collection)

        # Setting Sidebar
        st.sidebar.header('Get Flight Punctuality')
        weeks = st.sidebar.selectbox('Within weeks', ['1', '2', '3', '4'])
        # origin = st.sidebar.selectbox('Origin', ['Taoyuan Airport', 'Song Shan Airport'])
        destination = st.sidebar.selectbox('To Specific Destination', st.session_state.destinations)
        airline = st.sidebar.selectbox('With Specific Airline', st.session_state.airlines)
        submit = st.sidebar.button('Submit')
        if submit:
            # Display data as a table
            navbar()
            data = get_on_time_performance_by_week(weeks)
            data_all = get_airline_on_time_performance(airline)
            all_flights = select_airlines_all(weeks)
            all_destinations = get_destination_on_time_performance(destination)
            if weeks == '1':
                word = 'week'
            else:
                word = 'weeks'
            st.subheader(f"All flights' On time performance for the past {weeks} {word}")
            st.dataframe(data, width=600)
            st.dataframe(all_flights, width=600)
            
            # Show the airline's on-time performance
            st.subheader(f"{airline}")
            # st.markdown(f'flight data for <span style="color:blue; font-size:20px;">{airline} </span>', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])  # Creates two columns, plot in the narrower one
            with col1:
                fig, ax = plt.subplots()
                ax.plot(data_all['Week Starting'], data_all['On-Time Performance (%)'], marker='o')
                ax.set_xlabel('Date')
                ax.set_ylabel('On-Time Performance (%)')
                ax.set_title('Each Week On-Time Performance')
                fig.set_size_inches(5, 3)
                st.pyplot(fig)
                
            # Show the destination's on-time performance
            st.subheader(f"{destination}")
            # st.markdown(f'Flight data to <span style="color:blue; font-size:20px;">{destination} </span>', unsafe_allow_html=True)
            col3, col4 = st.columns([3, 1])
            with col3:
                fig, ax = plt.subplots()
                ax.plot(all_destinations['Week Starting'], all_destinations['On-Time Performance (%)'], marker='o')
                ax.set_xlabel('Date')
                ax.set_ylabel('On-Time Performance (%)')
                ax.set_title('Each Week On-Time Performance')
                fig.set_size_inches(5, 3)
                st.pyplot(fig)
        st.markdown("""
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f'Error in main: {e}')
    
        
if __name__ == '__main__':
    main()