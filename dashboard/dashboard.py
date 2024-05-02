import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from datetime import datetime, timedelta


def get_on_time_performance_by_week(week):
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2'] 
    # 取幾週的資料
    one_week_ago = datetime.utcnow() - timedelta(days=7*int(week))

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
    result = list(collection.aggregate(pipeline))
    print("result", result)
    df = pd.DataFrame({
        'Week': week,
        'All on_time depart flights':[result[0]['on_time_flights']],
        'On_Time_Performance': [result[0]['on_time_flights']/result[0]['total_flights']],
        'All Delay flights': [result[0]['delayed_flights']]
    })
    print(df)
    return df

def get_airline_on_time_performance(airline_name):
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2'] 
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
    return df


def get_destination_on_time_performance(destination):
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2'] 
    # 取幾週的資料
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

    # Assume 'collection' is your MongoDB collection
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
    return df
    


def select_destination():
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2'] 
    pipeline = [
        {"$group": {"_id": "$destination"}}  # Group by destination
    ]
    unique_destinations = list(collection.aggregate(pipeline))
    destinations = [doc['_id'] for doc in unique_destinations if doc['_id'] is not None]
    return destinations


def select_airlines_all(week):
    load_dotenv()
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2'] 
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
    print("result", result)
    df = pd.DataFrame(result)
    df.rename(columns={'_id': 'Airline', 'count': 'Flights Count', 'average_delay_minutes': 'Average Delay Minutes'}, inplace=True)
    return df


def select_airlines():
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
    client = MongoClient(url)
    db = client['flying_high']
    collection = db['flight_depart2']
    pipeline = [
    {"$unwind": "$airline"},  # Deconstruct the airline array
    {"$group": {
        "_id": "$airline.airline_name"  # Group by airline name to get unique names
    }}
    ]

    result = collection.aggregate(pipeline)
    unique_airline_names = [doc['_id'] for doc in result if doc['_id'] is not None]

    return unique_airline_names


def init_db():
    load_dotenv()
    client = MongoClient(os.getenv("MONGODB_URI_FLY"))
    return client['flying_high']


def load_destinations(collection):
    if 'destinations' not in st.session_state:
        destinations = list(collection.aggregate([{"$group": {"_id": "$destination"}}]))
        st.session_state['destinations'] = [dest['_id'] for dest in destinations if dest['_id'] is not None]


def load_airlines(collection):
    if 'airlines' not in st.session_state:
        airlines = list(collection.aggregate([
            {"$unwind": "$airline"},
            {"$group": {"_id": "$airline.airline_name"}}
        ]))
        st.session_state['airlines'] = [airline['_id'] for airline in airlines if airline['_id'] is not None]
        
        
def setup_sidebar():
    st.sidebar.header('FlightFinder')
    # 使用暫存資料 填充下拉選單
    origin = st.sidebar.selectbox('Origin', ['Taoyuan Airport', 'Song Shan Airport'])
    destination = st.sidebar.selectbox('Destination', st.session_state.destinations)
    airline = st.sidebar.selectbox('Airline', st.session_state.airlines)
    weeks = st.sidebar.selectbox('Week', ['1', '2', '3', '4'])
    submit = st.sidebar.button('Submit')
    return weeks, origin, destination, airline, submit

def main():
    db = init_db()
    collection = db['flight_depart2']
    
    # Load destinations and airlines
    load_destinations(collection)
    load_airlines(collection)

    # 設定 Sidebar
    st.sidebar.header('FlightFinder')
    weeks = st.sidebar.selectbox('Week', ['1', '2', '3', '4'])
    origin = st.sidebar.selectbox('Origin', ['Taoyuan Airport', 'Song Shan Airport'])
    destination = st.sidebar.selectbox('Destination', st.session_state.destinations)
    airline = st.sidebar.selectbox('Airline', st.session_state.airlines)
    submit = st.sidebar.button('Submit')
    if submit:
        # Display data as a table
        data = get_on_time_performance_by_week(weeks)
        data_all = get_airline_on_time_performance(airline)
        all_flights = select_airlines_all(weeks)
        all_destinations = get_destination_on_time_performance(destination)
        
        st.title('All flight data for the week')
        st.markdown(f'flights departing from Taoyuan Airport within <span style="color:red; font-size:20px;">{weeks} weeks</span>', unsafe_allow_html=True)
        st.dataframe(data)
        st.dataframe(all_flights)
        
        # Show the airline's on-time performance
        st.markdown(f'Displaying flight data for <span style="color:blue; font-size:20px;">{airline} </span>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])  # Creates two columns, plot in the narrower one
        with col1:
            fig, ax = plt.subplots()
            ax.plot(data_all['Week Starting'], data_all['On-Time Performance (%)'], marker='o')
            ax.set_xlabel('Date')
            ax.set_ylabel('On-Time Performance (%)')
            ax.set_title('Weeks On-Time Performance')
            fig.set_size_inches(5, 3)
            st.pyplot(fig)
            
        # Show the destination's on-time performance
        st.markdown(f'Displaying all flight data from {origin} to <span style="color:blue; font-size:20px;">{destination} </span>', unsafe_allow_html=True)
        col3, col4 = st.columns([3, 1])
        with col3:
            fig, ax = plt.subplots()
            ax.plot(all_destinations['Week Starting'], all_destinations['On-Time Performance (%)'], marker='o')
            ax.set_xlabel('Date')
            ax.set_ylabel('On-Time Performance (%)')
            ax.set_title('Weeks On-Time Performance')
            fig.set_size_inches(5, 3)
            st.pyplot(fig)
    
        
if __name__ == '__main__':
    main()