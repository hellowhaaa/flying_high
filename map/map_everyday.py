import folium
from datetime import datetime, timezone
import os
from pymongo import MongoClient
import pytz
from datetime import datetime
from dotenv import load_dotenv
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut,GeocoderUnavailable
import time
from branca.element import Element
import logging
from logging.handlers import RotatingFileHandler


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
log_path = os.path.join(project_root, 'map', 'logs')
os.makedirs(log_path, exist_ok=True)
# Generate log file name with the current date
current_date = datetime.now().strftime("%Y%m%d")
log_file_path = os.path.join(log_path, f'map_{current_date}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[RotatingFileHandler(log_file_path, maxBytes=10240, backupCount=5)]
)
load_dotenv()
url = os.getenv("MONGODB_URI_FLY")
client = MongoClient(url)

def main():
    logging.info("Start map_everyday.py")
    db = client['flying_high']
    collection_arrive = db['flight_arrive2']
    collection_depart = db['flight_depart2']
    pipeline = aggregation_pipeline()
    aggregated_arrive_destinations = collection_arrive.aggregate(pipeline)
    aggregated_depart_destinations = collection_depart.aggregate(pipeline)
    # for homepage
    insert_count_to_mongodb(aggregated_arrive_destinations, 'arrive')
    insert_count_to_mongodb(aggregated_depart_destinations, 'depart')
    
    unique_depart_destination_list = unique_destination_list(aggregated_depart_destinations)
    unique_arrive_destination_list = unique_destination_list(aggregated_arrive_destinations)
    
    arrive_destinations = result('flight_arrive2', unique_arrive_destination_list, 'arrive')
    depart_destinations = result('flight_depart2', unique_depart_destination_list, 'depart')
    create_map(arrive_destinations, depart_destinations)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    current_date = datetime.now(taiwan_tz).strftime('%Y-%m-%d')
    logging.info(f"End map_everyday.py {current_date}")


def utc_midnight():
    """
    Get 00:00 UTC Time from 00:00 AM in Taiwan Time
    Return:
        datetime object: UTC Time
    """
    try:
        # logging.info("Start utc_midnight")
        taiwan_tz = pytz.timezone('Asia/Taipei')
        tw_now = datetime.now(taiwan_tz)
        tw_midnight = taiwan_tz.localize(datetime(tw_now.year, tw_now.month, tw_now.day, 0, 0, 0))
        utc_mid_night = tw_midnight.astimezone(pytz.utc)
        return utc_mid_night
    except Exception as e:
        logging.error(f"Error in utc_midnight: {e}")


def aggregation_pipeline():
    """ 
    Create an aggregation pipeline to get unique destinations
    Return: 
        list: pipeline list
    """
    try:
        midnight = utc_midnight()
        pipeline = [
                {
                    "$match": {
                        "updated_at": {"$gt": midnight}  
                    }
                },
                {"$group": {"_id": "$destination", "count":{"$sum": 1}}},
                {"$sort": {"_id": 1}} 
            ]
        return pipeline
    except Exception as e:
        logging.error(f"Error in aggregate_unique_destination: {e}")

def extract_chinese(text):
    """ 
    Extract Chinese characters from a string with ()
    Return: 
        str: Chinese characters only
    """
    try:
        chinese_part = re.findall(r'[\u4e00-\u9fff]+', text)
        if '(' in text:
            chinese_only = chinese_part[-1]
        else:
            chinese_only = ''.join(chinese_part)
        return chinese_only
    except Exception as e:
        logging.error(f"Error in extract_chinese: {e}")


def unique_destination_list(unique_destinations):
    """ 
    Extract unique destinations from the aggregation result and extract Chinese characters
    
    Keyword arguments:
        unique_destinations -- aggregate result    
    Return: 
        list: unique destinations list
    """
    try:
        unique_destination_list = []
        for destination in unique_destinations:
            if destination['_id'] is not None: # 排除 None
                destination = extract_chinese(destination['_id'])
                unique_destination_list.append(destination)
        return unique_destination_list
    except Exception as e:
        logging.error(f"Error in unique_destination_list: {e}")

def insert_count_to_mongodb(aggregated_destinations, condition):
    """ 
    Extract unique destinations from the aggregation result and extract Chinese characters
    
    Keyword arguments:
        unique_destinations -- aggregate result    
    Return: 
        list: unique destinations list
    """
    try:
        for destination_dic in aggregated_destinations:
            if destination_dic['_id'] is not None: # 排除 None
                destination = extract_chinese(destination_dic['_id'])
                destination_count = {
                    "condition": condition,
                    "destination": destination,
                    "count": destination_dic['count'],
                    "created_at": datetime.now(timezone.utc)
                }
                collection = client['flying_high']['flight_count']
                result = collection.insert_one(destination_count)
                print("result->", result.inserted_id)
                
    except Exception as e:
        logging.error(f"Error in unique_destination_list: {e}")



def get_flight_data(location, collection_name):
    """
    Get flight data from mongodb collection everyday by destination
    
    Keyword arguments:
        location (str): city name
        collection_name (str): flight_depart2 or flight_arrive2
    Return: 
        list: everyday's each flight's collection in one list 
    """
    try:
        midnight = utc_midnight()
        filter={
            'destination': {
                '$regex': location
            },
            "updated_at": {"$gt": midnight} 
        }
        result = client['flying_high'][collection_name].find(
        filter=filter
        )
        return list(result)
    except Exception as e:
        logging.error(f"Error in flight_data: {e}")



def get_latitude_longitude_list(destination, max_attempts=5):
    """ 
    Get latitude and longitude from chinese city name
    
    Keyword arguments:
        destination (str) -- city name
        attempt (int)-- current attempt
        max_attempts (int) -- max attempts
    Return: 
        list: latitude and longitude
    """
    attempt = 0
    user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)"
    geolocator = Nominatim(user_agent=user_agent)
    while attempt < max_attempts:
        try:
            destination_result = geolocator.geocode(destination, timeout=10)
            if destination_result:
                return (destination_result.latitude, destination_result.longitude)
            else:
                return (None, None)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logging.warning(f"Attempt {attempt+1} failed: {str(e)}")
            attempt += 1
            time.sleep(2)  
        except Exception as e:
            logging.error(f"Error in get_latitude_longitude_list: {e}")
            return (None, None)



def result(collection_name, unique_destination_list, status):
    """
    Clean duplicate data and create a dictionary with destination, latitude and longitude, and flight details
    
    Keyword arguments:
        collection_name (str)-- flight_depart2 or flight_arrive2
        unique_destination_list (list) -- unique destinations list
        status -- depart or arrive
    Return: 
        list: dictionary inside with destination, latitude_longitude, flights and {scheduled_arrive_time, airlines}
    """
    try:
        # logging.info("Start result")
        destinations = []  
        for destination in unique_destination_list:
            latitude_longitude_list = get_latitude_longitude_list(destination)
            if latitude_longitude_list:
                each_flight_collection = get_flight_data(destination, collection_name)
                flight_details = []
                seen = set()  # Set to track unique flights
                for collection in each_flight_collection:
                    airlines_list = collection['airline']
                    airline_names = [airline['airline_name'] + airline['airline_code'] for airline in airlines_list]
                    flight_tuple = (collection[f'scheduled_{status}_time'], tuple(airline_names))
                    if flight_tuple not in seen:
                        seen.add(flight_tuple)
                        flight_details.append({
                            f'scheduled_{status}_time': collection[f'scheduled_{status}_time'],
                            'airlines': airline_names
                        })

                if not any(dest['destination'] == destination for dest in destinations):
                    destinations.append({
                        'destination': destination,
                        'latitude_longitude': latitude_longitude_list,
                        'flights': flight_details
                    })
        print("destinations-->", destinations)
        return destinations
    except Exception as e:
        logging.error(f"Error in result: {e}")


def create_map(arrive_destinations,depart_destinations):
    """
    Create a map with folium and add markers and lines 
    Keyword arguments:
        arrive_destinations (dict)
        depart_destinations (dict)  
    """
    # logging.info("Start create_map")
    try:
        
        # html file path
        path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../server/templates"))
        
        # Create a map centered on Taoyuan Airport
        taoyuan_airport_coords = [25.080, 121.2325]
        
        # create map instance
        map = folium.Map(location=taoyuan_airport_coords, zoom_start=5, tiles='cartodbpositron')
        
        # Set Taiwan's current date to display at the top of the map
        taiwan_tz = pytz.timezone('Asia/Taipei')
        current_date = datetime.now(taiwan_tz).strftime('%Y-%m-%d')

        date_html = f"""
        <div style="position: absolute; bottom: 10px; left: 10px; z-index:9999; font-size:16px; 
                    background-color: white; padding: 5px; border: 2px solid black; border-radius: 5px;">
            Map created on: {current_date}
        </div>
        """
        
        date_element = Element(date_html)
        map.get_root().html.add_child(date_element)
        
        
        # Add a navbar to the map
        style_and_navbar_html = """
        <style>
        .navbar-nav {
            display: flex;
            gap: 7px;
            margin-left: 0;
        }

        .nav-item {
            margin-right: 10px;
        }

        .nav-link {
            color: #555;
            transition: all 0.2s ease;
        }

        .nav-link:hover {
            color: #000;
            text-decoration: underline;
        }

        .navbar-brand {
            color: #000;
        }
        </style>
        <nav class="navbar-expand-sm bg-body-tertiary">
        <div class="container-fluid">
            <div class="row w-100">
            <div class="col-2 d-flex justify-content-center align-items-center">
                <a class="navbar-brand" href="/">Flying High</a>
            </div>
            <div class="col-9">
                <ul class="navbar-nav d-flex justify-content-start">
                <li class="nav-item">
                    <a class="nav-link" href="/search_flight">Search Flight</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/insurance">Insurance</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/flight_map">Flight Map</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="https://www.flyinghigh.live/dashboard/">Airline On-Time Performance</a>
                </li>
                </ul>
            </div>
            </div>
        </div>
        </nav>
        """
        date_element = Element(style_and_navbar_html)
        map.get_root().html.add_child(date_element)

        # FeatureGroup
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
        map.save(f'{path}/map_with_layers.html')
        
    except Exception as e:
        logging.error(f"Error in create_map: {e}")

if __name__ == '__main__':
    main()