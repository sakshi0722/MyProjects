from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_URL)

db = client["mediconnect_db"]

# Collections
chatbot_collection = db["chatbot_logs"]
emergency_collection = db["emergency_cases"]
minor_collection = db["minor_injuries"]
recovery_collection = db["recovery_plans"]