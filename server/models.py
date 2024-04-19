# models.py
from flask_mongoengine import MongoEngine

import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
db = MongoEngine()


class Address(db.EmbeddedDocument):
    zip = db.StringField(required=True)
    county = db.StringField(required=True)
    district = db.StringField(required=True)
    road = db.StringField(required=True)
    road_detail = db.StringField()



class Road(db.EmbeddedDocument):
    name = db.StringField(required=True)  # 路的名称

class Area(db.EmbeddedDocument):
    AreaName = db.StringField(required=True)  # 地区名称
    RoadList = db.ListField(db.EmbeddedDocumentField(Road))  # 地区下的路列表

class Location(db.Document):
    CityName = db.StringField(required=True)  # 城市名称
    AreaList = db.ListField(db.EmbeddedDocumentField(Area))  # 城市下的地区列表




  
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    address = db.EmbeddedDocumentField(Address)
    
    created_at = db.DateTimeField(default=datetime.datetime.now)

    def hash_password(self):
        self.password = generate_password_hash(self.password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    meta = {
        'collection': 'user'  # 指定 MongoDB 集合名
    }


# # 定义嵌入文档 Airline
# class Airline(db.EmbeddedDocument):
#     code = db.StringField() 
    
    
# class FlightManager3(db.Document):
#     _id = db.ObjectIdField()  # MongoDB中的默认ID字段
#     airline = db.MapField(field=db.StringField())
#     taiwan_title_time = db.StringField()
#     actual_depart_time = db.StringField()
#     created_at = db.DateTimeField()
#     destination = db.StringField()
#     gate = db.StringField()
#     scheduled_depart_time = db.StringField()
#     status = db.StringField()
#     terminal = db.StringField()
#     updated_at = db.DateTimeField()

#     meta = {
#         'collection': 'flight_arrive'  # 指定 MongoDB 集合名
#     }
    
    
#     @staticmethod
#     def get_flight_time(airline_code):  # airline_code 是 JL96 的組合
#         flights = FlightManager3.objects(__raw__={
#             'airline': {
#                 '$elemMatch': {'中華航空': {'$regex': airline_code }}
#             }
#         })
#         return flights