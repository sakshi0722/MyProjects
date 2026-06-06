from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Same MONGO_URL and database name as your existing database.py
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

async_client = AsyncIOMotorClient(MONGO_URL)
async_db = async_client["mediconnect_db"]