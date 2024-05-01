import folium
from folium.plugins import MarkerCluster
from folium import features
import os
from pymongo import MongoClient
import pytz
from datetime import datetime,timedelta
from dotenv import load_dotenv
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
import pendulum

load_dotenv()
url = os.getenv("MONGODB_URI_FLY")
print(url)
client = MongoClient(url)

db = client['flying_high']
collection_arrive= db['flight_arrive2']
collection_depart= db['flight_depart2']
taiwan_tz = pytz.timezone('Asia/Taipei')
tw_now = datetime.now(taiwan_tz)
tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
utc_midnight = tw_midnight.astimezone(pytz.utc)

# aggregate unique destination
pipeline = [
    {
        "$match": {
            "updated_at": {"$gt": utc_midnight}  
        }
    },
    {"$group": {"_id": "$destination"}},
    {"$sort": {"_id": 1}} 
]

unique_arrive_destinations = collection_arrive.aggregate(pipeline)
unique_depart_destinations = collection_depart.aggregate(pipeline)
# extract chinese and () from destination
def extract_chinese(text):
    chinese_part = re.findall(r'[\u4e00-\u9fff]+', text)
    if '(' in text:
        chinese_only = chinese_part[-1]
    else:
        chinese_only = ''.join(chinese_part)
    return chinese_only

# get unique destination list
def unique_destination_list(unique_destinations):
    unique_destination_list = []
    for destination in unique_destinations:
        if destination['_id'] is not None: # 排除 None
            destination = extract_chinese(destination['_id'])
            unique_destination_list.append(destination)
    return unique_destination_list


unique_depart_destination_list = unique_destination_list(unique_depart_destinations)
unique_arrive_destination_list = unique_destination_list(unique_arrive_destinations)

# get arrive flight data from mongodb everyday by destination
def flight_data(destination, collection_name):
    url = os.getenv("MONGODB_URI_FLY")
    print(url)
    client = MongoClient(url)
    filter={
        'destination': {
            '$regex': destination
        },
        "updated_at": {"$gt": utc_midnight} 
    }
    result = client['flying_high'][collection_name].find(
    filter=filter
    )
    return list(result)


## get longitude and latitude
useranget = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)"
geolocator = Nominatim(user_agent=useranget)

def get_location_list_by_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return [location.latitude, location.longitude]
        else:
            return (None, None)
    except GeocoderTimedOut:
        return get_location_list_by_address(address) # retry if timeout
    
    
def arrive_result(collection_name):
    destinations = []  
    for location in unique_arrive_destination_list:
        # 乾淨的 city name 去拉經緯度
        location_data = get_location_list_by_address(location)
        if location_data:
            flight_collection = flight_data(location, collection_name)
            flight_details = []
            seen = set()  # Set to track unique flights
            for collection in flight_collection:
                airlines_list = collection['airline']
                airline_names = [airline['airline_name'] + airline['airline_code'] for airline in airlines_list]
                flight_tuple = (collection['scheduled_arrive_time'], tuple(airline_names))
                if flight_tuple not in seen:
                    seen.add(flight_tuple)
                    flight_details.append({
                        'scheduled_arrive_time': collection['scheduled_arrive_time'],
                        'airlines': airline_names
                    })

            if not any(dest['destination'] == location for dest in destinations):
                destinations.append({
                    'destination': location,
                    'latitude_longitude': location_data,
                    'flights': flight_details
                })
                print("destinations--->",destinations)
            else:
                print(f"Destination {location} already exists in the dictionary.")
        else:
            print(f"Could not fetch data for {location}")
        time.sleep(1)
    return destinations # list

# print(destinations)

def depart_result(collection_name):
    destinations = []  
    for location in unique_depart_destination_list:
        # 乾淨的 city name 去拉經緯度
        location_data = get_location_list_by_address(location)
        if location_data:
            flight_collection = flight_data(location, collection_name)
            flight_details = []
            seen = set()  # Set to track unique flights
            for collection in flight_collection:
                airlines_list = collection['airline']
                airline_names = [airline['airline_name'] + airline['airline_code'] for airline in airlines_list]
                flight_tuple = (collection['scheduled_depart_time'], tuple(airline_names))
                if flight_tuple not in seen:
                    seen.add(flight_tuple)
                    flight_details.append({
                        'scheduled_depart_time': collection['scheduled_depart_time'],
                        'airlines': airline_names
                    })

            if not any(dest['destination'] == location for dest in destinations):
                destinations.append({
                    'destination': location,
                    'latitude_longitude': location_data,
                    'flights': flight_details
                })
                print("destinations--->",destinations)
            else:
                print(f"Destination {location} already exists in the dictionary.")
        else:
            print(f"Could not fetch data for {location}")
        time.sleep(1)
    return destinations # list



def task_map():
    # -----------------------------------------
    # os.path.dirname(__file__) get current file path
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../server/templates"))
    print(path)
    taoyuan_airport_coords = [25.080, 121.2325]

    arrive_destinations = arrive_result('flight_arrive2')
    depart_destinations = depart_result('flight_depart2')


    map = folium.Map(location=taoyuan_airport_coords, zoom_start=5, tiles='cartodbpositron')


    arrivals = folium.FeatureGroup(name='Arrivals to Taoyuan')
    departures = folium.FeatureGroup(name='Departures from Taoyuan')

    # Marker 
    folium.Marker(
        taoyuan_airport_coords,
        popup='桃園國際機場',
        icon=folium.Icon(color='red', icon='plane')
    ).add_to(map)

    # Arrive
    for each in arrive_destinations:
        city = each['destination']
        coords = each['latitude_longitude']
        popup_content = f"<strong>{city}</strong><br/>"
        for flight in each['flights']:
            scheduled_arrive_time = flight['scheduled_arrive_time']
            airlines = ', '.join(flight['airlines'])
            popup_content += f"Scheduled Arrive: {scheduled_arrive_time}<br/>Airlines: {airlines}<br/>"
        
        marker = folium.Marker(
            coords,
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color='green', icon='plane-arrival')
        ).add_to(arrivals)
        
        folium.PolyLine([taoyuan_airport_coords, coords], weight=1,dash_array='10, 10',color="green").add_to(arrivals)

    # Depart
    for each in depart_destinations:
        city = each['destination']
        coords = each['latitude_longitude']
        popup_content = f"<strong>{city}</strong><br/>"
        for flight in each['flights']:
            scheduled_depart_time = flight['scheduled_depart_time']
            airlines = ', '.join(flight['airlines'])
            popup_content += f"Scheduled Depart: {scheduled_depart_time}<br/>Airlines: {airlines}<br/>"
        
        marker = folium.Marker(
            coords,
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color='blue', icon='plane-arrival')
        ).add_to(departures)
        
        folium.PolyLine([taoyuan_airport_coords, coords], weight=1,dash_array='10, 10',color="blue").add_to(departures)

    # add  FeatureGroup to map
    map.add_child(arrivals)
    map.add_child(departures)

    # add LayerControl
    map.add_child(folium.LayerControl())

    style_function = """
        function(feature) {
            return {color: feature.properties.color};
        };
    """
    highlight_function = """
        function(feature) {
            return {weight: 10, color: 'red'};
        };
    """

    map.get_root().html.add_child(folium.Element("""
        <style>
        .leaflet-interactive:hover {
            stroke-width: 10px;
            stroke-color: #red !important;
        }
        </style>
    """))

    map.save(f'{path}/map_with_layers.html')


task_map()

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False, 
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5)
# }

# with DAG(
#     dag_id="release_map_everyday",
#     schedule="0 17 * * *", # 每20分鐘執行一次
#     start_date=pendulum.datetime(2024, 4, 25, tz="UTC"),
#     default_args=default_args,
#     catchup=False, # 不會去執行以前的任務
#     max_active_runs=1,
#     tags=['map'],
# ) as dag:
#     task_start = EmptyOperator(
#     task_id="task_start",
#     dag=dag
#     )
#     task_end = EmptyOperator(
#     task_id="task_end",
#     dag=dag
#     )
    
#     task_map_everyday = PythonOperator(
#         task_id = "map_everyday",
#         python_callable=task_map,
#         dag = dag  
#     )
    
# (task_start >> task_map_everyday >> task_end)

