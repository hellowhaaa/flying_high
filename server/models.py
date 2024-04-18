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
    
