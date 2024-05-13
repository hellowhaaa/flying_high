import folium
import os
from pymongo import MongoClient
import pytz
from datetime import datetime
from dotenv import load_dotenv
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut,GeocoderUnavailable
import time
import pendulum
from branca.element import Element
load_dotenv()
url = os.getenv("MONGODB_URI_FLY")
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

# todo -------

def get_location_list_by_address(address, attempt=1, max_attempts=5):
    useranget = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)"
    geolocator = Nominatim(user_agent=useranget)
    try: 
        location = geolocator.geocode(address, timeout=10)
        if location:
            return [location.latitude, location.longitude]
        else:
            return (None, None)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        if attempt <= max_attempts:
            time.sleep(2)
            return get_location_list_by_address(address, attempt=attempt+1)
        else:
            raise e
        

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
    # 設置台灣當天時間 顯示在map最上面
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
                <a class="nav-link" href="https://www.flyinghigh.live/dashboard/">Dashboard</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
    """
    date_element = Element(style_and_navbar_html)
    map.get_root().html.add_child(date_element)



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

