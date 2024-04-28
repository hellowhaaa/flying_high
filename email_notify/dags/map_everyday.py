import folium
from folium.plugins import MarkerCluster
from folium import features
import os

# os.path.dirname(__file__) get current file path
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../server/templates"))
print(path)
taoyuan_airport_coords = [25.080, 121.2325]


arrive_destinations = [
  {
    "destination": "布里斯本",
    "latitude_longitude": [22.66651495, 120.31366413016224]
  },
  { "destination": "曼谷", "latitude_longitude": [13.7524938, 100.4935089] },
  {
    "destination": "上海浦東",
    "latitude_longitude": [31.142735899999998, 121.80411312160436]
  },
  { "destination": "亞庇", "latitude_longitude": [5.9780066, 116.0728988] },
  { "destination": "仁川", "latitude_longitude": [37.456, 126.7052] },
  { "destination": "仙台", "latitude_longitude": [38.2597492, 140.8798618] },
  { "destination": "伊斯坦堡", "latitude_longitude": [41.006381, 28.9758715] },
  { "destination": "休士頓", "latitude_longitude": [29.7589382, -95.3676974] },
  {
    "destination": "佐賀",
    "latitude_longitude": [33.26417535, 130.29747292904747]
  },
  { "destination": "倫敦", "latitude_longitude": [51.5074456, -0.1277653] },
  { "destination": "克拉克", "latitude_longitude": [28.3323055, 102.3516198] },
  { "destination": "函館", "latitude_longitude": [41.7737872, 140.7261884] },
  { "destination": "北京", "latitude_longitude": [40.190632, 116.412144] },
  { "destination": "南京", "latitude_longitude": [32.0438284, 118.7788631] },
  {
    "destination": "卡堤克蘭",
    "latitude_longitude": [-0.83170875, 37.00492162779861]
  },
  { "destination": "吉隆坡", "latitude_longitude": [3.1516964, 101.6942371] },
  { "destination": "名古屋", "latitude_longitude": [35.170581, 136.8809822] },
  { "destination": "多倫多", "latitude_longitude": [43.6534817, -79.3839347] },
  { "destination": "大邱", "latitude_longitude": [35.8713, 128.6018] },
  {
    "destination": "大阪關西",
    "latitude_longitude": [34.43420455, 135.2225230169576]
  },
  { "destination": "安大略", "latitude_longitude": [50.000678, -86.000977] },
  { "destination": "宿霧", "latitude_longitude": [10.47, 123.83] },
  {
    "destination": "富國島",
    "latitude_longitude": [22.6627466, 120.34971151344902]
  },
  { "destination": "富山", "latitude_longitude": [36.7020984, 137.2126608] },
  { "destination": "寧波", "latitude_longitude": [29.8622194, 121.6203873] },
  { "destination": "小松", "latitude_longitude": [36.4018391, 136.4528145] },
  { "destination": "岡山", "latitude_longitude": [34.6654089, 133.917825] },
  {
    "destination": "峇里島",
    "latitude_longitude": [22.7277177, 120.29994671624216]
  },
  { "destination": "峴港", "latitude_longitude": [16.068, 108.212] },
  { "destination": "巴黎", "latitude_longitude": [48.8534951, 2.3483915] },
  { "destination": "廈門", "latitude_longitude": [24.4801069, 118.0853479] },
  { "destination": "廣島", "latitude_longitude": [34.3980242, 132.476095] },
  { "destination": "廣州", "latitude_longitude": [23.1301964, 113.2592945] },
  { "destination": "慕尼黑", "latitude_longitude": [48.1371079, 11.5753822] },
  {
    "destination": "成都天府",
    "latitude_longitude": [30.303551050000003, 104.4457087996561]
  },
  { "destination": "新加坡", "latitude_longitude": [1.2899175, 103.8519072] },
  {
    "destination": "曼谷廊曼",
    "latitude_longitude": [24.4477852, 118.0684726]
  },
  { "destination": "札幌", "latitude_longitude": [43.0686365, 141.3509218] },
  { "destination": "杜拜", "latitude_longitude": [0.6353, 124.4958] },
  { "destination": "杭州", "latitude_longitude": [30.2489634, 120.2052342] },
  { "destination": "東京", "latitude_longitude": [35.6821936, 139.762221] },
  { "destination": "松山", "latitude_longitude": [33.8403352, 132.751077] },
  { "destination": "檳城", "latitude_longitude": [37.4311343, 118.0136196] },
  { "destination": "汶萊", "latitude_longitude": [4.4137155, 114.5653908] },
  { "destination": "河內", "latitude_longitude": [34.4691853, 132.8899558] },
  { "destination": "法蘭克福", "latitude_longitude": [50.1106444, 8.6820917] },
  { "destination": "洛杉磯", "latitude_longitude": [34.0536909, -118.242766] },
  { "destination": "深圳", "latitude_longitude": [22.5445741, 114.0545429] },
  { "destination": "清州", "latitude_longitude": [38.5746589, 116.8260491] },
  { "destination": "清邁", "latitude_longitude": [18.7882778, 98.9858802] },
  { "destination": "溫哥華", "latitude_longitude": [49.2608724, -123.113952] },
  { "destination": "澳門", "latitude_longitude": [22.1899448, 113.5380454] },
  { "destination": "濟州", "latitude_longitude": [33.4887737, 126.4987083] },
  { "destination": "熊本", "latitude_longitude": [32.7903435, 130.6888842] },
  { "destination": "沖繩", "latitude_longitude": [38.0058559, 140.6242638] },
  { "destination": "福岡", "latitude_longitude": [36.7081098, 136.9317417] },
  { "destination": "福州", "latitude_longitude": [21.9842196, 111.2062957] },
  { "destination": "秋田", "latitude_longitude": [39.7168833, 140.1296657] },
  { "destination": "紐約", "latitude_longitude": [40.7127281, -74.0060152] },
  { "destination": "維也納", "latitude_longitude": [48.2083537, 16.3725042] },
  { "destination": "羽田", "latitude_longitude": [35.5479444, 139.7466458] },
  {
    "destination": "胡志明市",
    "latitude_longitude": [10.7763897, 106.7011391]
  },
  { "destination": "舊金山", "latitude_longitude": [37.7792588, -122.4193286] },
  { "destination": "芝加哥", "latitude_longitude": [41.8755616, -87.6244212] },
  { "destination": "茨城", "latitude_longitude": [29.9777203, 121.4454192] },
  { "destination": "西雅圖", "latitude_longitude": [47.6038321, -122.330062] },
  { "destination": "鄭州", "latitude_longitude": [34.7533392, 113.6599983] },
  { "destination": "重慶", "latitude_longitude": [30.05518, 107.8748712] },
  { "destination": "金邊", "latitude_longitude": [11.5730391, 104.857807] },
  { "destination": "釜山", "latitude_longitude": [35.1799528, 129.0752365] },
  {
    "destination": "阿姆斯特丹",
    "latitude_longitude": [52.3730796, 4.8924534]
  },
  { "destination": "雅加達", "latitude_longitude": [-6.175247, 106.8270488] },
  { "destination": "青島", "latitude_longitude": [36.0637967, 120.3192081] },
  { "destination": "香港", "latitude_longitude": [22.350627, 114.1849161] },
  { "destination": "馬尼拉", "latitude_longitude": [14.5906346, 120.9799964] },
  { "destination": "高松", "latitude_longitude": [34.350692, 134.0461528] }
]

# let two list be the same
depart_destinations = arrive_destinations

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
    folium.Marker(
        coords,
        popup=f'Arrival to {city}',
        icon=folium.Icon(color='green', icon='plane-arrival')
    ).add_to(arrivals)
    
    folium.PolyLine([taoyuan_airport_coords, coords], color="green").add_to(arrivals)

# Depart
for each in depart_destinations:
    city = each['destination']
    coords = each['latitude_longitude']
    folium.Marker(
        coords,
        popup=f'Departure from {city}',
        icon=folium.Icon(color='blue', icon='plane-departure')
    ).add_to(departures)
    
    folium.PolyLine([coords, taoyuan_airport_coords], color="blue").add_to(departures)

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

