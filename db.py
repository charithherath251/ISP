# db.py
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.captcha_logs  # Your database

pre_login_collection = database.get_collection("pre_login_logs")
post_login_collection = database.get_collection("post_login_logs")