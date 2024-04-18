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
    
    
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    address = db.embeddedDocumentField(Address)
    
    created_at = db.DateTimeField(default=datetime.datetime.now)

    def hash_password(self):
        self.password = generate_password_hash(self.password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    meta = {
        'collection': 'user'  # 指定 MongoDB 集合名
    }
    
