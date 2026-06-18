from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGODB_SETTINGS["URI"])

db = client[settings.MONGODB_SETTINGS["DB_NAME"]]