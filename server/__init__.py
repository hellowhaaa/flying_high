from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
import os


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv("MONGODB_URI")
}
db = MongoEngine(app)

