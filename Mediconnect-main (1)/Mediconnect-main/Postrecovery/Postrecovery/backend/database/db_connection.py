from pymongo import MongoClient
from backend.config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db["post_recovery"]

def save_data(data):
    collection.insert_one(data)
