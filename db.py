from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
MonGo_URI = os.getenv("DATABASE_URL")
DB_Name = "Todo_DB"

client = MongoClient(MonGo_URI)
db = client[DB_Name]
user_collection = db["Users"]
task_collection = db["Tasks"]
