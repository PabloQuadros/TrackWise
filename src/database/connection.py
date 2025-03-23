import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
DATABASE_NAME = "logistics_db"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]